from flask import Blueprint, request, jsonify, send_file
from backend.pdf_export import generar_pdf
from backend.validator import validar_datos

export_bp = Blueprint("export", __name__)


@export_bp.route("/exportar-pdf", methods=["POST"])
def exportar_pdf():
    body = request.get_json(force=True)
    if not body:
        return jsonify({"error": "No se recibieron datos"}), 400

    resultado = body.get("resultado")
    datos     = body.get("datos")

    if not resultado or not datos:
        return jsonify({"error": "Se requieren 'resultado' y 'datos'"}), 400

    if resultado.get("status") != "optimal":
        return jsonify({"error": "Solo se puede exportar un resultado óptimo"}), 400

    try:
        buffer = generar_pdf(resultado, datos)
        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="OptiPlan_Resultados.pdf"
        )
    except Exception as e:
        return jsonify({"error": f"Error al generar PDF: {str(e)}"}), 500
