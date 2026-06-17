import sys, os, subprocess

#  Autoinstalación 
def _mod_disponible(nombre):
    try:
        __import__(nombre)
        return True
    except ImportError:
        return False

_PAQUETES = {
    "flask":      "flask>=3.0.0",
    "pulp":       "pulp>=2.8.0",
    "reportlab":  "reportlab>=4.1.0",
}
_faltantes = [paq for mod, paq in _PAQUETES.items() if not _mod_disponible(mod)]

if _faltantes:
    print(f"\n  Instalando dependencias (solo ocurre una vez)...")
    print(f"  Paquetes: {', '.join(_faltantes)}\n")
    ret = subprocess.call([sys.executable, "-m", "pip", "install"] + _faltantes)
    if ret != 0:
        print("\n  ERROR: No se pudieron instalar las dependencias.")
        print("  Ejecuta manualmente:  pip install flask pulp reportlab")
        input("\n  Presiona Enter para salir...")
        sys.exit(1)
    print("\n  Instalacion completada. Reiniciando...\n")
    os.execv(sys.executable, [sys.executable] + sys.argv)
# ────────────────────────────────────────────────────────────────

import threading, webbrowser
from flask import send_from_directory
from backend import create_app
from config import Config

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

flask_app = create_app()

@flask_app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@flask_app.route("/<path:path>")
def static_files(path):
    return send_from_directory(FRONTEND_DIR, path)

def _abrir_navegador(port):
    import time; time.sleep(1.2)
    webbrowser.open(f"http://localhost:{port}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", Config.PORT))
    print(f"\n  OptiPlan listo en: http://localhost:{port}")
    print(f"  (Ctrl+C para detener)\n")
    threading.Thread(target=_abrir_navegador, args=(port,), daemon=True).start()
    flask_app.run(host="0.0.0.0", port=port, debug=False)
