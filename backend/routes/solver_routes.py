from flask import Blueprint, request, jsonify
from backend.solver import resolver, resolver_escenario
from backend.validator import validar_datos

solver_bp = Blueprint("solver", __name__)

ESCENARIOS = [
    {"key": "base",          "nombre": "Base",              "descripcion": "Datos originales sin cambios"},
    {"key": "demanda_alta",  "nombre": "Demanda +20%",      "descripcion": "Incremento del 20% en toda la demanda"},
    {"key": "demanda_baja",  "nombre": "Demanda -20%",      "descripcion": "Reducción del 20% en toda la demanda"},
    {"key": "sin_horas_extra","nombre": "Sin Horas Extra",  "descripcion": "Sin disponibilidad de horas extra"},
    {"key": "capacidad_extra","nombre": "Capacidad +10%",   "descripcion": "Incremento del 10% en capacidades regulares"},
]


@solver_bp.route("/resolver", methods=["POST"])
def resolver_endpoint():
    datos = request.get_json(force=True)
    if not datos:
        return jsonify({"error": "No se recibieron datos"}), 400

    errores = validar_datos(datos)
    if errores:
        return jsonify({"error": "Datos inválidos", "detalles": errores}), 422

    try:
        resultado = resolver(datos)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": f"Error interno al resolver: {str(e)}"}), 500


@solver_bp.route("/escenarios", methods=["POST"])
def escenarios_endpoint():
    datos = request.get_json(force=True)
    if not datos:
        return jsonify({"error": "No se recibieron datos"}), 400

    errores = validar_datos(datos)
    if errores:
        return jsonify({"error": "Datos inválidos", "detalles": errores}), 422

    resultados = []
    for esc in ESCENARIOS:
        try:
            res = resolver_escenario(datos, esc["key"])
            resultados.append({
                "key":         esc["key"],
                "nombre":      esc["nombre"],
                "descripcion": esc["descripcion"],
                "resultado":   res,
            })
        except Exception as e:
            resultados.append({
                "key":         esc["key"],
                "nombre":      esc["nombre"],
                "descripcion": esc["descripcion"],
                "resultado":   {"status": "error", "mensaje": str(e)},
            })

    return jsonify(resultados)
