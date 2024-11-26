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
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from urllib.parse import quote
import time

load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', os.urandom(24).hex())
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Configure CORS
CORS(app, supports_credentials=True)

# Initialize JWT
jwt = JWTManager(app)

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

# Configure logging
logging.basicConfig(level=logging.INFO)

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
        client_id = os.getenv('LINKEDIN_CLIENT_ID')
        
        if not redirect_uri or not client_id:
            app.logger.error("LinkedIn configuration missing")
            raise AuthError({
                "code": "configuration_error",
                "description": "OAuth configuration error"
            }, 500)
        
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(16)
        session['oauth_state'] = state
        
        # Build LinkedIn authorization URL
        auth_url = (
            "https://www.linkedin.com/oauth/v2/authorization?"
            f"response_type=code&"
            f"client_id={client_id}&"
            f"redirect_uri={quote(redirect_uri)}&"
            f"state={state}&"
            f"scope={quote('openid profile email')}"
        )
        
        app.logger.info(f"Redirecting to LinkedIn auth URL: {auth_url}")
        return redirect(auth_url)
        
    except Exception as e:
        app.logger.error(f"LinkedIn login error: {str(e)}", exc_info=True)
        raise AuthError({
            "code": "linkedin_auth_error",
            "description": str(e)
        }, 500)

@app.route('/api/auth/linkedin/callback')
def linkedin_callback():
    try:
        app.logger.info("Received callback request:")
        app.logger.info(f"Args: {request.args}")
        
        # Verify state parameter
        expected_state = session.pop('oauth_state', None)
        received_state = request.args.get('state')
        
        if not expected_state or expected_state != received_state:
            app.logger.error(f"State mismatch. Expected: {expected_state}, Received: {received_state}")
            raise AuthError({
                "code": "invalid_state",
                "description": "Invalid state parameter"
            }, 400)
            
        # Get the authorization code
        code = request.args.get('code')
        if not code:
            raise AuthError({
                "code": "missing_code",
                "description": "No authorization code received"
            }, 400)
            
        # Exchange code for access token
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": os.getenv('LINKEDIN_REDIRECT_URI'),
            "client_id": os.getenv('LINKEDIN_CLIENT_ID'),
            "client_secret": os.getenv('LINKEDIN_SECRET_KEY')
        }
        
        app.logger.info("Requesting access token...")
        token_response = requests.post(token_url, data=token_data)
        
        if token_response.status_code != 200:
            app.logger.error(f"Token error: {token_response.text}")
            raise AuthError({
                "code": "token_error",
                "description": "Failed to get access token"
            }, 500)
            
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        
        # Get user info
        userinfo_url = "https://api.linkedin.com/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        app.logger.info("Requesting user info...")
        userinfo_response = requests.get(userinfo_url, headers=headers)
        
        if userinfo_response.status_code != 200:
            app.logger.error(f"Userinfo error: {userinfo_response.text}")
            raise AuthError({
                "code": "userinfo_error",
                "description": "Failed to get user info"
            }, 500)
            
        userinfo = userinfo_response.json()
        app.logger.info(f"User info received: {userinfo}")
        
        # Extract user info
        email = userinfo.get('email')
        full_name = userinfo.get('name')
        email_verified = userinfo.get('email_verified', False)
        provider_id = userinfo.get('sub')  # LinkedIn's unique identifier
        avatar_url = userinfo.get('picture')
        
        if not email:
            raise AuthError({
                "code": "missing_email",
                "description": "Email not provided by LinkedIn"
            }, 400)
            
        # Try to find existing user
        existing_user = supabase.table('users').select('*').eq('email', email).execute()
        
        if len(existing_user.data) == 0:
            # Create new user
            user_data = {
                'email': email,
                'full_name': full_name,
                'email_verified': email_verified,
                'auth_provider': 'linkedin',
                'provider_id': provider_id,
                'avatar_url': avatar_url,
                'onboarding_step': 1,
                'onboarding_completed': False,
                'last_sign_in': datetime.utcnow().isoformat()
            }
            
            result = supabase.table('users').insert(user_data).execute()
            user = result.data[0]
            app.logger.info(f"Created new user: {user['id']}")
        else:
            # Update existing user
            user = existing_user.data[0]
            update_data = {
                'full_name': full_name,
                'email_verified': email_verified,
                'auth_provider': 'linkedin',
                'provider_id': provider_id,
                'avatar_url': avatar_url,
                'last_sign_in': datetime.utcnow().isoformat()
            }
            
            result = supabase.table('users').update(update_data).eq('id', user['id']).execute()
            user = result.data[0]
            app.logger.info(f"Updated existing user: {user['id']}")
            
        # Generate JWT token with additional claims
        access_token = create_access_token(
            identity=user['id'],
            additional_claims={
                'email': email,
                'full_name': full_name,
                'onboarding_completed': user.get('onboarding_completed', False),
                'onboarding_step': user.get('onboarding_step', 1),
                'provider': 'linkedin'
            }
        )
        
        # Redirect to frontend with token
        frontend_url = os.getenv('FRONTEND_URL')
        if not user.get('onboarding_completed', False):
            redirect_url = f"{frontend_url}/onboarding?token={access_token}&step={user.get('onboarding_step', 1)}"
        else:
            redirect_url = f"{frontend_url}/auth/callback?token={access_token}"
        
        return redirect(redirect_url)
        
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

# User profile endpoint
@app.route('/api/user/profile')
@jwt_required()
def get_user_profile():
    try:
        current_user_email = get_jwt_identity()
        
        # Get user data from Supabase
        user_query = supabase.from_('users').select('*').eq('email', current_user_email).execute()
        
        if not user_query.data:
            return jsonify({
                "error": "User not found"
            }), 404
            
        user_data = user_query.data[0]
        
        return jsonify({
            "email": user_data['email'],
            "name": user_data['name'],
            "email_verified": user_data['email_verified'],
            "auth_provider": user_data['auth_provider']
        })
        
    except Exception as e:
        app.logger.error(f"Error fetching user profile: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal server error"
        }), 500

# Onboarding API endpoints
@app.route('/api/onboarding/career-info', methods=['POST'])
@jwt_required()
def update_career_info():
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        # Validate university
        university_id = data.get('university_id')
        if university_id == 'other':
            # Add custom university
            custom_university = data.get('custom_university')
            if not custom_university:
                raise ValueError("Custom university name required")
            
            result = supabase.rpc('add_custom_university', {'university_name': custom_university}).execute()
            university_id = result.data[0]
        
        # Update user's career information
        update_data = {
            'university_id': university_id,
            'education_program_id': data.get('education_program_id'),
            'onboarding_step': 2  # Move to next step
        }
        
        result = supabase.table('users').update(update_data).eq('id', user_id).execute()
        return jsonify({'message': 'Career information updated', 'step': 2}), 200
        
    except Exception as e:
        app.logger.error(f"Career info update error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 400

@app.route('/api/onboarding/career-aspirations', methods=['POST'])
@jwt_required()
def update_career_aspirations():
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        update_data = {
            'career_goal': data.get('career_goal'),
            'career_path': data.get('career_path'),
            'onboarding_step': 3  # Move to next step
        }
        
        result = supabase.table('users').update(update_data).eq('id', user_id).execute()
        return jsonify({'message': 'Career aspirations updated', 'step': 3}), 200
        
    except Exception as e:
        app.logger.error(f"Career aspirations update error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 400

@app.route('/api/onboarding/industry-preferences', methods=['POST'])
@jwt_required()
def update_industry_preferences():
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        # Start a transaction for updating multiple tables
        update_data = {
            'dream_companies': data.get('dream_companies', []),
            'work_mode_preference': data.get('work_mode_preference'),
            'onboarding_step': 4  # Move to next step
        }
        
        # Update user preferences
        result = supabase.table('users').update(update_data).eq('id', user_id).execute()
        
        # Update industry preferences
        if 'industry_ids' in data:
            # First, remove existing preferences
            supabase.table('user_industries').delete().eq('user_id', user_id).execute()
            
            # Then add new preferences
            industry_data = [
                {'user_id': user_id, 'industry_id': industry_id}
                for industry_id in data['industry_ids']
            ]
            if industry_data:
                supabase.table('user_industries').insert(industry_data).execute()
        
        return jsonify({'message': 'Industry preferences updated', 'step': 4}), 200
        
    except Exception as e:
        app.logger.error(f"Industry preferences update error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 400

@app.route('/api/onboarding/personality', methods=['POST'])
@jwt_required()
def update_personality():
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        update_data = {
            'personality_type': data.get('personality_type'),
            'personality_test_url': data.get('personality_test_url'),
            'onboarding_step': 5,
            'onboarding_completed': True
        }
        
        result = supabase.table('users').update(update_data).eq('id', user_id).execute()
        return jsonify({'message': 'Personality information updated', 'completed': True}), 200
        
    except Exception as e:
        app.logger.error(f"Personality update error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 400

@app.route('/api/onboarding/cv', methods=['POST'])
@jwt_required()
def upload_cv():
    try:
        user_id = get_jwt_identity()
        
        if 'cv' not in request.files:
            return jsonify({'error': 'No CV file provided'}), 400
            
        cv_file = request.files['cv']
        if cv_file.filename == '':
            return jsonify({'error': 'No CV file selected'}), 400
            
        if not cv_file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Generate a secure filename
        filename = f"cv_{user_id}_{int(time.time())}.pdf"
        
        # Upload to Supabase Storage
        file_path = f"cv/{filename}"
        with cv_file.stream as file:
            result = supabase.storage.from_('documents').upload(file_path, file)
        
        # Get the public URL
        cv_url = supabase.storage.from_('documents').get_public_url(file_path)
        
        # Update user's CV URL
        result = supabase.table('users').update({
            'cv_url': cv_url
        }).eq('id', user_id).execute()
        
        return jsonify({'message': 'CV uploaded successfully', 'cv_url': cv_url}), 200
        
    except Exception as e:
        app.logger.error(f"CV upload error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 400

# Helper endpoints for onboarding
@app.route('/api/universities', methods=['GET'])
@jwt_required()
def get_universities():
    try:
        result = supabase.table('universities').select('*').order('name').execute()
        return jsonify(result.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/education-programs/<university_id>', methods=['GET'])
@jwt_required()
def get_education_programs(university_id):
    try:
        result = supabase.table('education_programs').select('*').eq('university_id', university_id).execute()
        return jsonify(result.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/industries', methods=['GET'])
@jwt_required()
def get_industries():
    try:
        result = supabase.table('industries').select('*').order('name').execute()
        return jsonify(result.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/onboarding/status', methods=['GET'])
@jwt_required()
def get_onboarding_status():
    try:
        user_id = get_jwt_identity()
        result = supabase.table('users').select('onboarding_step,onboarding_completed').eq('id', user_id).execute()
        
        if not result.data:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify(result.data[0]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))