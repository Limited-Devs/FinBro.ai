# FinBro.ai Backend - Flask Application Factory
"""
Production-grade Flask application with layered architecture.

Architecture:
- API Layer (routes/) - HTTP request handling
- Service Layer (services/) - Business logic
- Repository Layer (repositories/) - Data access
- Models (models/) - Domain entities and schemas
"""
import os
import sys
from flask import Flask
from flask_cors import CORS

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_app(config_name: str = None) -> Flask:
    """
    Flask application factory.
    
    Args:
        config_name: Configuration environment ('development', 'production', 'testing')
    
    Returns:
        Configured Flask application instance
    """
    from app.config import config
    from app.extensions import init_extensions
    from app.api.middleware.error_handler import register_error_handlers
    from app.api.middleware.request_logger import register_request_logging
    from app.utils.logging import setup_logging
    
    # Determine config
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Create Flask app
    app = Flask(
        __name__,
        static_folder='../../frontend/dist',
        static_url_path=''
    )
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Setup logging
    setup_logging(app)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    
    # Initialize Flask extensions
    init_extensions(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register request logging
    register_request_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    return app


def register_blueprints(app: Flask) -> None:
    """Register all API blueprints."""
    from app.api.routes.prediction import prediction_bp
    from app.api.routes.chat import chat_bp
    from app.api.routes.health import health_bp
    
    app.register_blueprint(prediction_bp, url_prefix='/api')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(health_bp, url_prefix='/api')
    
    # Serve React static files
    @app.route('/')
    def serve_react():
        """Serve the main React app."""
        from flask import send_from_directory
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:path>')
    def serve_static_or_react(path):
        """Serve static files or React app for client-side routing."""
        from flask import send_from_directory
        try:
            return send_from_directory(app.static_folder, path)
        except Exception:
            return send_from_directory(app.static_folder, 'index.html')
