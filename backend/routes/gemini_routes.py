# ============================================================
# gemini_routes.py — Proxy seguro para Gemini API
# La API key nunca sale al frontend, vive solo en el .env
# ============================================================

import os
import json
import requests
from flask import Blueprint, request, jsonify

gemini_bp = Blueprint("gemini", __name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)

SYSTEM_PROMPT = """Eres el asistente de análisis de OptiPlan, una aplicación de planificación de producción por programación lineal.
Tu rol es interpretar resultados de optimización y dar recomendaciones claras, concretas y breves.
Cuando el usuario pregunte sobre los resultados, usa los datos del contexto JSON que se te proporciona.
Responde siempre en español. Usa emojis con moderación para facilitar la lectura.
Sé directo y práctico. Máximo 200 palabras por respuesta a menos que el usuario pida más detalle.
No inventes datos que no estén en el contexto. Si no hay resultados disponibles, díselo al usuario."""


@gemini_bp.route("/chat", methods=["POST"])
def chat():
    if not GEMINI_API_KEY:
        return jsonify({"error": "Gemini no configurado. Agrega GEMINI_API_KEY al .env"}), 503

    body = request.get_json(force=True)
    if not body:
        return jsonify({"error": "Cuerpo vacío"}), 400

    pregunta = body.get("pregunta", "").strip()
    contexto = body.get("contexto", None)   # resultado + datosActuales del frontend

    if not pregunta:
        return jsonify({"error": "El campo 'pregunta' es requerido"}), 400

    # Construir el mensaje con contexto opcional
    if contexto:
        user_text = (
            f"Contexto del modelo OptiPlan (JSON):\n{json.dumps(contexto, ensure_ascii=False)}\n\n"
            f"Pregunta del usuario: {pregunta}"
        )
    else:
        user_text = f"Pregunta del usuario (sin resultados aún): {pregunta}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": SYSTEM_PROMPT},
                    {"text": user_text}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 512,
        }
    }

    try:
        resp = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json=payload,
            timeout=20
        )

        if resp.status_code != 200:
            return jsonify({"error": f"Error de Gemini: {resp.status_code}", "detalle": resp.text}), 502

        data = resp.json()
        texto = (
            data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
                .strip()
        )

        if not texto:
            return jsonify({"error": "Gemini devolvió respuesta vacía"}), 502

        return jsonify({"respuesta": texto})

    except requests.exceptions.Timeout:
        return jsonify({"error": "Gemini tardó demasiado. Intenta de nuevo."}), 504
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500
