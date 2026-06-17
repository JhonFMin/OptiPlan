from .solver_routes import solver_bp
from .export_routes import export_bp
from .gemini_routes import gemini_bp

def register_routes(app):
    app.register_blueprint(solver_bp, url_prefix="/api")
    app.register_blueprint(export_bp, url_prefix="/api")
    app.register_blueprint(gemini_bp, url_prefix="/api")
