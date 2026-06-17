import os

class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    HOST = "127.0.0.1"
    PORT = int(os.getenv("PORT", 5000))
    SECRET_KEY = os.getenv("SECRET_KEY", "optiplan-dev-key")
    WINDOW_TITLE = "OptiPlan — Planificación de Producción"
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 800
    WINDOW_RESIZABLE = True
