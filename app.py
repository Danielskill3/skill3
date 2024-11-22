# app.py
from flask import Flask, request, jsonify, session, redirect, url_for
import base64
import hashlib
import secrets
from flask_cors import CORS
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import re
from email_validator import validate_email, EmailNotValidError
from supabase import create_client, Client
from flask_talisman import Talisman
from authlib.integrations.flask_client import OAuth
#import authlib.oauth2.rfc7636 

def generate_pkce_pair():
    """Generate PKCE code verifier and code challenge."""
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b'=').decode('utf-8')
    return code_verifier, code_challenge
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Security headers
Talisman(app, content_security_policy=None)

# Setup CORS
CORS(app, resources={r"/*": {
    "origins": os.getenv('FRONTEND_URL', 'http://localhost:5173'),
    "supports_credentials": True
}})

# Add security headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Initialize JWT
jwt = JWTManager(app)

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_ANON_KEY')
)

# Setup OAuth for LinkedIn OpenID Connect
oauth = OAuth(app)
linkedin = oauth.register(
    name='linkedin',
    server_metadata_url='https://www.linkedin.com/.well-known/openid-configuration',
    client_id=os.getenv("LINKEDIN_CLIENT_ID"),
    client_secret=os.getenv("LINKEDIN_CLIENT_SECRET"),
    client_kwargs={
        'scope': 'openid profile email',
        'response_type': 'code',
        'token_endpoint_auth_method': 'client_secret_post'
    }
)

# Setup logging
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/auth.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
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
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

# Utility functions
def validate_password(password):
    """Password validation rules."""
    if len(password) < 8:
        raise AuthError({"code": "invalid_password",
                        "message": "Password must be at least 8 characters long"}, 400)
    if not re.search(r'[A-Z]', password):
        raise AuthError({"code": "invalid_password",
                        "message": "Password must contain at least one uppercase letter"}, 400)
    if not re.search(r'[a-z]', password):
        raise AuthError({"code": "invalid_password",
                        "message": "Password must contain at least one lowercase letter"}, 400)
    if not re.search(r'\d', password):
        raise AuthError({"code": "invalid_password",
                        "message": "Password must contain at least one number"}, 400)
    return True

# Routes
@app.route('/api/auth/linkedin/login')
def linkedin_login():
    """Initiate LinkedIn OpenID Connect flow."""
    try:
        # Generate PKCE challenge
        code_verifier, code_challenge = generate_pkce_pair()
        
        # Store PKCE code verifier in session
        session['code_verifier'] = code_verifier
        
        redirect_uri = os.getenv('LINKEDIN_REDIRECT_URI')
        return linkedin.authorize_redirect(
            redirect_uri=redirect_uri,
            code_challenge=code_challenge,
            code_challenge_method='S256'
        )
    except Exception as e:
        app.logger.error(f"LinkedIn login error: {str(e)}")
        raise AuthError({
            "code": "linkedin_login_error",
            "message": f"Failed to initiate LinkedIn login: {str(e)}"
        }, 500)

@app.route('/api/auth/linkedin/callback')
def linkedin_callback():
    """Handle LinkedIn OpenID Connect callback."""
    try:
        # Retrieve PKCE verifier
        code_verifier = session.pop('code_verifier', None)
        if not code_verifier:
            raise AuthError({
                "code": "invalid_state",
                "message": "PKCE verification failed"
            }, 400)

        # Exchange code for token with PKCE
        token = linkedin.authorize_access_token(code_verifier=code_verifier)
        if not token:
            raise AuthError({
                "code": "token_error",
                "message": "Failed to obtain token"
            }, 400)

        # Get user info from ID token
        userinfo = linkedin.parse_id_token(token)
        email = userinfo.get('email')
        
        if not email:
            raise AuthError({
                "code": "missing_email",
                "message": "Email not provided by LinkedIn"
            }, 400)

        # Sign in with Supabase (OAuth)
        auth_response = supabase.auth.sign_in_with_oauth({
            "provider": "linkedin",
            "access_token": token['access_token'],
            "id_token": token.get('id_token')
        })

        if auth_response.error:
            raise AuthError({
                "code": "supabase_auth_error",
                "message": auth_response.error.message
            }, 400)

        # Update user data in Supabase
        user_data = {
            "id": auth_response.user.id,
            "email": email,
            "linkedin_id": userinfo.get('sub'),
            "first_name": userinfo.get('given_name'),
            "last_name": userinfo.get('family_name'),
            "last_login": datetime.now(datetime.timezone.utc).isoformat()
        }

        supabase.table('users').upsert(user_data).execute()

        return jsonify({
            "message": "Login successful",
            "session": auth_response.session,
            "user": user_data
        })

    except AuthError as e:
        raise e
    except Exception as e:
        app.logger.error(f"LinkedIn callback error: {str(e)}")
        raise AuthError({
            "code": "callback_error",
            "message": f"Authorization failed: {str(e)}"
        }, 500)

@app.route('/register', methods=['POST'])
def register():
    """Register a new user with email and password."""
    try:
        data = request.get_json()
        
        try:
            valid = validate_email(data['email'])
            email = valid.email
        except EmailNotValidError as e:
            raise AuthError({
                "code": "invalid_email",
                "message": str(e)
            }, 400)

        validate_password(data['password'])

        # Sign up with Supabase
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": data['password']
        })

        if auth_response.error:
            raise AuthError({
                "code": "signup_error",
                "message": auth_response.error.message
            }, 400)

        # Store additional user data
        user_data = {
            "id": auth_response.user.id,
            "email": email,
            "name": data.get('name', ''),
            "created_at": datetime.now(datetime.timezone.utc).isoformat()
        }
        
        supabase.table('users').insert(user_data).execute()

        return jsonify({
            'message': 'User created successfully',
            'session': auth_response.session,
            'user': user_data
        }), 201

    except AuthError as e:
        raise e
    except Exception as e:
        app.logger.error(f'Registration error: {str(e)}')
        raise AuthError({
            "code": "registration_error",
            "message": f"Registration failed: {str(e)}"
        }, 500)

@app.route('/login', methods=['POST'])
def login():
    """Login with email and password."""
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['email', 'password']):
            raise AuthError({
                "code": "missing_credentials",
                "message": "Email and password are required"
            }, 400)

        auth_response = supabase.auth.sign_in_with_password({
            "email": data['email'],
            "password": data['password']
        })

        if auth_response.error:
            raise AuthError({
                "code": "invalid_credentials",
                "message": "Invalid email or password"
            }, 401)

        # Fetch user data
        user_data = supabase.table('users').select('*').eq('id', auth_response.user.id).execute()
        
        if not user_data.data:
            raise AuthError({
                "code": "user_not_found",
                "message": "User data not found"
            }, 404)

        return jsonify({
            'session': auth_response.session,
            'user': user_data.data[0]
        })

    except AuthError as e:
        raise e
    except Exception as e:
        app.logger.error(f'Login error: {str(e)}')
        raise AuthError({
            "code": "login_error",
            "message": f"Login failed: {str(e)}"
        }, 500)

@app.route('/reset-password', methods=['POST'])
def reset_password():
    """Send password reset email."""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            raise AuthError({
                "code": "missing_email",
                "message": "Email is required"
            }, 400)

        response = supabase.auth.reset_password_email(email)
        
        if response.error:
            raise AuthError({
                "code": "reset_password_error",
                "message": response.error.message
            }, 400)

        return jsonify({
            "message": "Password reset email sent"
        }), 200

    except AuthError as e:
        raise e
    except Exception as e:
        app.logger.error(f'Password reset error: {str(e)}')
        raise AuthError({
            "code": "reset_password_error",
            "message": f"Password reset failed: {str(e)}"
        }, 500)

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout the current user."""
    try:
        response = supabase.auth.sign_out()
        
        if response.error:
            raise AuthError({
                "code": "logout_error",
                "message": response.error.message
            }, 400)

        session.clear()
        return jsonify({
            "message": "Logged out successfully"
        }), 200

    except AuthError as e:
        raise e
    except Exception as e:
        app.logger.error(f'Logout error: {str(e)}')
        raise AuthError({
            "code": "logout_error",
            "message": f"Logout failed: {str(e)}"
        }, 500)

@app.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    """Get current user details."""
    try:
        current_user_id = get_jwt_identity()
        user_data = supabase.table('users').select('*').eq('id', current_user_id).execute()

        if not user_data.data:
            raise AuthError({
                "code": "user_not_found",
                "message": "User not found"
            }, 404)

        return jsonify(user_data.data[0])

    except AuthError as e:
        raise e
    except Exception as e:
        app.logger.error(f'Get user error: {str(e)}')
        raise AuthError({
            "code": "user_fetch_error",
            "message": f"Failed to fetch user data: {str(e)}"
        }, 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))