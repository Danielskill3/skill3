import os
import sys
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

# Add the parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Use absolute import
from skill3.core.config import settings

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)

    # Comprehensive CORS configuration
    cors_origins = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://192.168.100.82:3000',
        'https://skill3-frontend.onrender.com',
        'https://skill3.onrender.com'
    ]

    # CORS Configuration with detailed options
    CORS(app, resources={
        r"/v1/*": {
            "origins": cors_origins,
            "allow_headers": [
                "Content-Type", 
                "Authorization", 
                "X-Requested-With",
                "Access-Control-Allow-Origin",
                "Access-Control-Allow-Headers",
                "Access-Control-Allow-Credentials"
            ],
            "supports_credentials": True,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        }
    })

    # Middleware to log and handle CORS preflight requests
    @app.before_request
    def log_request_info():
        logger.debug(f'Request Method: {request.method}')
        logger.debug(f'Request Origin: {request.headers.get("Origin")}')
        logger.debug(f'Request Headers: {request.headers}')

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin')
        
        # Always set these headers
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = (
            'Content-Type, Authorization, X-Requested-With, '
            'Access-Control-Allow-Origin, Access-Control-Allow-Headers, '
            'Access-Control-Allow-Credentials'
        )
        
        # Set origin headers if it's in allowed origins
        if origin and origin in cors_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        elif origin:
            # Fallback for development
            response.headers['Access-Control-Allow-Origin'] = origin
        
        return response

    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = settings.JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

    # Optional: Conditionally import authentication modules
    try:
        from skill3.auth.utils import mail
        from skill3.auth.routes import auth_bp
        
        # Email Configuration
        app.config['MAIL_SERVER'] = settings.MAIL_SERVER
        app.config['MAIL_PORT'] = settings.MAIL_PORT
        app.config['MAIL_USE_TLS'] = settings.MAIL_USE_TLS
        app.config['MAIL_USERNAME'] = settings.MAIL_USERNAME
        app.config['MAIL_PASSWORD'] = settings.MAIL_PASSWORD
        app.config['MAIL_DEFAULT_SENDER'] = settings.MAIL_DEFAULT_SENDER

        # LinkedIn OAuth Configuration
        app.config['LINKEDIN_CLIENT_ID'] = settings.LINKEDIN_CLIENT_ID
        app.config['LINKEDIN_CLIENT_SECRET'] = settings.LINKEDIN_CLIENT_SECRET

        # Frontend URL for password reset
        app.config['FRONTEND_URL'] = settings.FRONTEND_URL

        # Initialize extensions
        jwt = JWTManager(app)
        mail.init_app(app)

        # Register blueprints
        app.register_blueprint(auth_bp, url_prefix='/v1/auth')
    except ImportError as e:
        print(f"Authentication modules not imported. Error: {e}")

    @app.route('/v1/auth/options', methods=['OPTIONS'])
    def handle_options():
        logger.debug("Handling OPTIONS request for CORS preflight")
        response = jsonify(success=True)
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = (
            'Content-Type, Authorization, X-Requested-With, '
            'Access-Control-Allow-Origin, Access-Control-Allow-Headers, '
            'Access-Control-Allow-Credentials'
        )
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response, 200

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return jsonify(error=str(e)), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
