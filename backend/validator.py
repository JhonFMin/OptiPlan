def validar_datos(datos):
    errores = []

    periodos = datos.get("periodos", 0)
    if not isinstance(periodos, int) or periodos < 1 or periodos > 12:
        errores.append("El número de periodos debe ser entre 1 y 12.")

    productos = datos.get("productos", [])
    if not productos or len(productos) < 1:
        errores.append("Debe haber al menos un producto.")
    for i, p in enumerate(productos):
        nombre = p.get("nombre", f"Producto {i+1}")
        for campo in ["precio", "costoProd", "costoSub", "costoInv", "penFaltante", "tiempoCorte", "tiempoEnsamble"]:
            val = p.get(campo)
            if val is None or not isinstance(val, (int, float)) or val < 0:
                errores.append(f"Producto '{nombre}': '{campo}' debe ser un número no negativo.")
        if p.get("costoProd", 0) >= p.get("precio", 0):
            pass
        if p.get("costoSub", 0) < p.get("costoProd", 0):
            pass

    demanda = datos.get("demanda", [])
    nombres_prods = [p.get("nombre") for p in productos]
    if len(demanda) != periodos:
        errores.append(f"La demanda debe tener exactamente {periodos} periodos.")
    for d in demanda:
        for nombre in nombres_prods:
            val = d.get(nombre)
            if val is None or not isinstance(val, (int, float)) or val < 0:
                errores.append(f"Demanda periodo {d.get('periodo','?')}, producto '{nombre}': valor inválido.")

    cap = datos.get("capacidad", {})
    for campo in ["corteRegular", "ensambleRegular"]:
        val = cap.get(campo)
        if val is None or not isinstance(val, (int, float)) or val <= 0:
            errores.append(f"Capacidad '{campo}' debe ser mayor a 0.")

    inv = datos.get("inventario", {})
    for nombre in nombres_prods:
        ini = inv.get(f"inicial{nombre}", 0)
        minf = inv.get(f"minFinal{nombre}", 0)
        if not isinstance(ini, (int, float)) or ini < 0:
            errores.append(f"Inventario inicial '{nombre}' inválido.")
        if not isinstance(minf, (int, float)) or minf < 0:
            errores.append(f"Inventario mínimo final '{nombre}' inválido.")

    return errores
