from pulp import (
    LpProblem, LpMinimize, LpVariable, lpSum,
    value, PULP_CBC_CMD, LpStatusOptimal
)

def resolver(datos):
    periodos    = datos["periodos"]
    productos   = datos["productos"]
    demanda_raw = datos["demanda"]
    cap         = datos["capacidad"]
    inv_cfg     = datos["inventario"]

    nombres = [p["nombre"] for p in productos]
    T = list(range(1, periodos + 1))

    demanda = {}
    for d in demanda_raw:
        t = d["periodo"]
        for n in nombres:
            demanda[(t, n)] = d.get(n, 0)

    corte_regular   = cap.get("corteRegular", 300)
    ensam_regular   = cap.get("ensambleRegular", 240)
    extra_corte_max = cap.get("extraCorte", 60)
    extra_ensam_max = cap.get("extraEnsamble", 50)
    costo_he1       = cap.get("costoHoraExtra1", 20)
    costo_he2       = cap.get("costoHoraExtra2", 30)
    limite_he1      = cap.get("limiteHoraExtra1", 20)
    reduccion_p3    = cap.get("reduccionCorteP3", True)

    inv_max   = inv_cfg.get("maximo", 50)
    inv_ini   = {n: inv_cfg.get(f"inicial{n}", 0) for n in nombres}
    inv_min_f = {n: inv_cfg.get(f"minFinal{n}", 0) for n in nombres}

    params = {p["nombre"]: p for p in productos}

    prob = LpProblem("OptiPlan", LpMinimize)

    x  = {(t, n): LpVariable(f"x_{t}_{n}", lowBound=0) for t in T for n in nombres}
    s  = {(t, n): LpVariable(f"s_{t}_{n}", lowBound=0) for t in T for n in nombres}
    I  = {(t, n): LpVariable(f"I_{t}_{n}", lowBound=0, upBound=inv_max) for t in T for n in nombres}
    f  = {(t, n): LpVariable(f"f_{t}_{n}", lowBound=0) for t in T for n in nombres}

    hec1 = {t: LpVariable(f"hec1_{t}", lowBound=0, upBound=limite_he1)      for t in T}
    hec2 = {t: LpVariable(f"hec2_{t}", lowBound=0, upBound=max(0, extra_corte_max - limite_he1)) for t in T}
    hee  = {t: LpVariable(f"hee_{t}", lowBound=0, upBound=extra_ensam_max) for t in T}

    costo_prod = lpSum(
        params[n]["costoProd"] * x[(t, n)] +
        params[n]["costoSub"]  * s[(t, n)] +
        params[n]["costoInv"]  * I[(t, n)] +
        params[n]["penFaltante"] * f[(t, n)]
        for t in T for n in nombres
    )
    costo_he = lpSum(
        costo_he1 * hec1[t] + costo_he2 * hec2[t] + costo_he2 * hee[t]
        for t in T
    )
    prob += costo_prod + costo_he

    for t in T:
        for n in nombres:
            inv_prev = inv_ini[n] if t == 1 else I[(t - 1, n)]
            prob += (
                inv_prev + x[(t, n)] + s[(t, n)] == demanda[(t, n)] + I[(t, n)] + f[(t, n)],
                f"balance_{t}_{n}"
            )

    for t in T:
        cap_corte_t = corte_regular * 0.8 if (reduccion_p3 and t == 3) else corte_regular
        prob += (
            lpSum(params[n]["tiempoCorte"] * x[(t, n)] for n in nombres) <=
            cap_corte_t + hec1[t] + hec2[t],
            f"cap_corte_{t}"
        )
        prob += (
            lpSum(params[n]["tiempoEnsamble"] * x[(t, n)] for n in nombres) <=
            ensam_regular + hee[t],
            f"cap_ensam_{t}"
        )

    for n in nombres:
        prob += I[(periodos, n)] >= inv_min_f[n], f"inv_min_final_{n}"

    solver = PULP_CBC_CMD(msg=0)
    prob.solve(solver)

    if prob.status != LpStatusOptimal:
        return {
            "status": "infeasible",
            "mensaje": "No se encontró solución factible. Revisa capacidades vs demanda e inventarios mínimos."
        }

    resultado_periodos = []
    for t in T:
        prod_t   = {n: round(value(x[(t, n)]) or 0, 2) for n in nombres}
        sub_t    = {n: round(value(s[(t, n)]) or 0, 2) for n in nombres}
        inv_t    = {n: round(value(I[(t, n)]) or 0, 2) for n in nombres}
        falt_t   = {n: round(value(f[(t, n)]) or 0, 2) for n in nombres}
        he_corte = round((value(hec1[t]) or 0) + (value(hec2[t]) or 0), 2)
        he_ensam = round(value(hee[t]) or 0, 2)

        costo_p  = sum(params[n]["costoProd"]  * prod_t[n] for n in nombres)
        costo_s  = sum(params[n]["costoSub"]   * sub_t[n]  for n in nombres)
        costo_i  = sum(params[n]["costoInv"]   * inv_t[n]  for n in nombres)
        costo_f  = sum(params[n]["penFaltante"] * falt_t[n] for n in nombres)
        costo_he_t = costo_he1 * (value(hec1[t]) or 0) + costo_he2 * (value(hec2[t]) or 0) + costo_he2 * he_ensam
        costos_periodo = costo_p + costo_s + costo_i + costo_f + costo_he_t

        ingresos_periodo = sum(
            params[n]["precio"] * (demanda[(t, n)] - falt_t[n])
            for n in nombres
        )

        tot_corte = sum(params[n]["tiempoCorte"] * prod_t[n] for n in nombres)

        resultado_periodos.append({
            "periodo":          t,
            "produccion":       prod_t,
            "subcontrato":      sub_t,
            "inventario":       inv_t,
            "faltante":         falt_t,
            "horasExtraCorte":  he_corte,
            "horasExtraEnsamble": he_ensam,
            "totalHorasCorte":  round(tot_corte, 2),
            "costoProduccion":  round(costo_p, 2),
            "costoSubcontrato": round(costo_s, 2),
            "costoInventario":  round(costo_i, 2),
            "costoFaltante":    round(costo_f, 2),
            "costoHorasExtra":  round(costo_he_t, 2),
            "costosPeriodo":    round(costos_periodo, 2),
            "ingresosPeriodo":  round(ingresos_periodo, 2),
            "utilidadPeriodo":  round(ingresos_periodo - costos_periodo, 2),
        })

    resumen = {
        "costoProduccion":  round(sum(p["costoProduccion"]  for p in resultado_periodos), 2),
        "costoSubcontrato": round(sum(p["costoSubcontrato"] for p in resultado_periodos), 2),
        "costoInventario":  round(sum(p["costoInventario"]  for p in resultado_periodos), 2),
        "costoFaltante":    round(sum(p["costoFaltante"]    for p in resultado_periodos), 2),
        "costoHorasExtra":  round(sum(p["costoHorasExtra"]  for p in resultado_periodos), 2),
        "ingresoTotal":     round(sum(p["ingresosPeriodo"]  for p in resultado_periodos), 2),
    }
    resumen["costoTotal"]    = round(sum([
        resumen["costoProduccion"], resumen["costoSubcontrato"],
        resumen["costoInventario"], resumen["costoFaltante"], resumen["costoHorasExtra"]
    ]), 2)
    resumen["utilidadTotal"] = round(resumen["ingresoTotal"] - resumen["costoTotal"], 2)

    return {
        "status":        "optimal",
        "periodos":      resultado_periodos,
        "resumenCostos": resumen,
        "utilidadTotal": resumen["utilidadTotal"],
    }


def resolver_escenario(datos_base, nombre_escenario):
    import copy
    datos = copy.deepcopy(datos_base)
    cap = datos["capacidad"]
    demanda = datos["demanda"]

    if nombre_escenario == "base":
        pass
    elif nombre_escenario == "demanda_alta":
        for d in demanda:
            for k in d:
                if k != "periodo":
                    d[k] = round(d[k] * 1.20, 1)
    elif nombre_escenario == "demanda_baja":
        for d in demanda:
            for k in d:
                if k != "periodo":
                    d[k] = round(d[k] * 0.80, 1)
    elif nombre_escenario == "sin_horas_extra":
        cap["extraCorte"]   = 0
        cap["extraEnsamble"] = 0
    elif nombre_escenario == "capacidad_extra":
        cap["corteRegular"]   = round(cap["corteRegular"] * 1.10, 1)
        cap["ensambleRegular"] = round(cap["ensambleRegular"] * 1.10, 1)

    resultado = resolver(datos)
    return resultado
