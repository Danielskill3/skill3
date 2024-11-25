from flask import Flask, request, jsonify, session, redirect, url_for
import base64
import hashlib
import secrets
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import re
from email_validator import validate_email, EmailNotValidError
from supabase import create_client, Client
from authlib.integrations.flask_client import OAuth
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24).hex())
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', os.urandom(24).hex())
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Setup CORS
CORS(app, resources={r"/*": {
    "origins": [
        os.getenv('FRONTEND_URL', 'http://localhost:3000'),
        "https://www.linkedin.com",
        "https://api.linkedin.com"
    ],
    "supports_credentials": True,
    "allow_headers": ["Content-Type", "Authorization"],
    "methods": ["GET", "POST", "OPTIONS"]
}})

# Initialize JWT
jwt = JWTManager(app)

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_ANON_KEY')
)

oauth = OAuth(app)
# Initialize OAuth with OpenID Connect for LinkedIn
oauth.register(
    name='linkedin',
    client_id=os.getenv('LINKEDIN_CLIENT_ID'),
    client_secret=os.getenv('LINKEDIN_SECRET_KEY'),
    api_base_url='https://api.linkedin.com/v2/',
    access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
    authorize_url='https://www.linkedin.com/oauth/v2/authorization',
    userinfo_url='https://api.linkedin.com/v2/userinfo',
    client_kwargs={
        'scope': 'openid profile email',
        'token_endpoint_auth_method': 'client_secret_post',
        'response_type': 'code'
    }
)


# Setup logging with more detailed formatting
if not os.path.exists('logs'):
    os.mkdir('logs')
    
file_handler = RotatingFileHandler('logs/auth.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s\nDetails: %(exc_info)s\nPath: %(pathname)s:%(lineno)d\n'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Auth service startup')

# Error handling
class AuthError(Exception):
    def __init__(self, error, status_code):
        super().__init__()
        self.error = error
        self.status_code = status_code

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    app.logger.error(f"Auth error: {ex.error}")
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

@app.errorhandler(Exception)
def handle_generic_error(ex):
    app.logger.error(f"Unexpected error: {str(ex)}", exc_info=True)
    return jsonify({
        "code": "internal_error",
        "description": "An unexpected error occurred"
    }), 500

# Utility functions
def validate_password(password):
    """Password validation rules."""
    if len(password) < 8:
        raise AuthError({
            "code": "invalid_password",
            "description": "Password must be at least 8 characters long"
        }, 400)
    if not re.search(r'[A-Z]', password):
        raise AuthError({
            "code": "invalid_password",
            "description": "Password must contain at least one uppercase letter"
        }, 400)
    if not re.search(r'[a-z]', password):
        raise AuthError({
            "code": "invalid_password",
            "description": "Password must contain at least one lowercase letter"
        }, 400)
    if not re.search(r'\d', password):
        raise AuthError({
            "code": "invalid_password",
            "description": "Password must contain at least one number"
        }, 400)
    return True

def create_user_in_supabase(email, password):
    """Create a user in Supabase with better error handling."""
    try:
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        app.logger.info(f"Supabase auth response: {auth_response}")
        
        if hasattr(auth_response, 'error') and auth_response.error:
            raise AuthError({
                "code": "supabase_error",
                "description": str(auth_response.error)
            }, 400)
            
        if not auth_response.user:
            raise AuthError({
                "code": "signup_error",
                "description": "Failed to create user account - no user returned"
            }, 400)
            
        return auth_response.user
        
    except Exception as e:
        app.logger.error(f"Supabase user creation error: {str(e)}", exc_info=True)
        raise AuthError({
            "code": "supabase_error",
            "description": f"Failed to create user in Supabase: {str(e)}"
        }, 500)


@app.route('/api/auth/linkedin/login')
@app.route('/api/auth/linkedin')
def linkedin_login():
    try:
        redirect_uri = os.getenv('LINKEDIN_REDIRECT_URI')
        if not redirect_uri:
            app.logger.error("LinkedIn redirect URI not configured")
            raise AuthError({
                "code": "configuration_error",
                "description": "OAuth configuration error"
            }, 500)
        
        return oauth.linkedin.authorize_redirect(
            redirect_uri=redirect_uri,
            state=secrets.token_urlsafe(16)
        )
    except Exception as e:
        app.logger.error(f"LinkedIn login error: {str(e)}", exc_info=True)
        raise AuthError({
            "code": "linkedin_auth_error",
            "description": str(e)
        }, 500)

@app.route('/api/auth/linkedin/callback')
def linkedin_callback():
    try:
        token = oauth.linkedin.authorize_access_token()
        resp = oauth.linkedin.get('userinfo')
        
        if resp.status_code != 200:
            app.logger.error(f"LinkedIn userinfo error: {resp.text}")
            raise AuthError({
                "code": "userinfo_error",
                "description": "Failed to get user info from LinkedIn"
            }, 500)
            
        userinfo = resp.json()
        app.logger.info(f"LinkedIn userinfo response: {userinfo}")
        
        email = userinfo.get('email')
        name = userinfo.get('name')
        email_verified = userinfo.get('email_verified', False)
        
        if not email or not email_verified:
            raise AuthError({
                "code": "invalid_email",
                "description": "Email not provided or not verified"
            }, 400)

        # Check if user exists in Supabase
        user_query = supabase.from_('users').select('*').eq('email', email).execute()
        
        if not user_query.data:
            # Create new user if they don't exist
            supabase.from_('users').insert({
                'email': email,
                'name': name,
                'auth_provider': 'linkedin',
                'email_verified': email_verified
            }).execute()

        # Generate JWT token
        access_token = create_access_token(identity=email)
        
        # Redirect to frontend with token
        frontend_url = os.getenv('FRONTEND_URL')
        return redirect(f"{frontend_url}/auth/callback?token={access_token}")
        
    except Exception as e:
        app.logger.error(f"LinkedIn callback error: {str(e)}", exc_info=True)
        frontend_url = os.getenv('FRONTEND_URL')
        return redirect(f"{frontend_url}/auth/error?error={str(e)}")

@app.route('/register', methods=['POST'])
def register():
    """Register a new user with email and password."""
    try:
        app.logger.info("Starting registration process")
        
        # Get and validate request data
        data = request.get_json()
        if not data:
            raise AuthError({
                "code": "invalid_request",
                "description": "No JSON data provided"
            }, 400)
            
        app.logger.info(f"Registration request data: {data}")
        
        # Validate email
        try:
            valid = validate_email(data.get('email', ''))
            email = valid.email
        except EmailNotValidError as e:
            raise AuthError({
                "code": "invalid_email",
                "description": str(e)
            }, 400)

        # Validate password
        password = data.get('password')
        if not password:
            raise AuthError({
                "code": "missing_password",
                "description": "Password is required"
            }, 400)
            
        validate_password(password)

        # Create user in Supabase
        user = create_user_in_supabase(email, password)
        app.logger.info(f"User created in Supabase: {user.id}")

        # Store additional user data
        user_data = {
            "id": user.id,
            "email": email,
            "name": data.get('name', ''),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            db_response = supabase.table('users').insert(user_data).execute()
            app.logger.info(f"User data stored in database: {db_response}")
        except Exception as e:
            app.logger.error(f"Database error: {str(e)}", exc_info=True)
            # Continue even if this fails, as the auth user is already created
            
        # Create JWT token
        access_token = create_access_token(identity=user.id)
        
        app.logger.info(f"Registration successful for user: {user.id}")
        
        return jsonify({
            'message': 'User created successfully. Please verify your email.',
            'access_token': access_token,
            'user': user_data
        }), 201

    except AuthError as e:
        raise e
    except Exception as e:
        app.logger.error(f"Unexpected registration error: {str(e)}", exc_info=True)
        raise AuthError({
            "code": "registration_error",
            "description": str(e)
        }, 500)

@app.route('/login', methods=['POST'])
def login():
    """Login with email and password."""
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['email', 'password']):
            raise AuthError({
                "code": "missing_credentials",
                "description": "Email and password are required"
            }, 400)

        auth_response = supabase.auth.sign_in_with_password({
            "email": data['email'],
            "password": data['password']
        })

        if not auth_response.user:
            raise AuthError({
                "code": "invalid_credentials",
                "description": "Invalid email or password"
            }, 401)

        # Fetch user data
        user_data = supabase.table('users').select('*').eq('id', auth_response.user.id).execute()
        
        if not user_data.data:
            raise AuthError({
                "code": "user_not_found",
                "description": "User data not found"
            }, 404)
            
        # Create JWT token
        access_token = create_access_token(identity=auth_response.user.id)

        return jsonify({
            'access_token': access_token,
            'user': user_data.data[0]
        })

    except AuthError as e:
        raise e
    except Exception as e:
        app.logger.error(f'Login error: {str(e)}')
        raise AuthError({
            "code": "login_error",
            "description": str(e)
        }, 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))