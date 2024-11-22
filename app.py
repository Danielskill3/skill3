import os
import re
import logging
from datetime import datetime
from flask import Flask, jsonify, request, session, redirect
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from supabase import create_client, Client
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError
from flask_talisman import Talisman

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Flask application setup
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))  

Talisman(app, content_security_policy=None)

# Add these headers to your responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response
# CORS setup for React
CORS(app, resources={r"/*": {"origins": os.getenv('FRONTEND_URL', 'http://localhost:5173')}}, supports_credentials=True)

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# OAuth setup for LinkedIn
oauth = OAuth(app)
linkedin = oauth.register(
    name='linkedin',
    client_id=os.getenv("LINKEDIN_CLIENT_ID"),
    client_secret=os.getenv("LINKEDIN_CLIENT_SECRET"),
    access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
    authorize_url='https://www.linkedin.com/oauth/v2/authorization',
    api_base_url='https://api.linkedin.com/v2/',
    client_kwargs={
        'scope': 'r_liteprofile r_emailaddress',
        'response_type': 'code',
    }
)

# Password validation function
def validate_password(password):
    """
    Password validation rules:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one number
    """
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True

# Default route
@app.route('/')
def home():
    """Default route."""
    return jsonify({"message": "Welcome to the Authentication Backend"})

# LinkedIn OAuth Routes
@app.route('/api/auth/linkedin/login')
def linkedin_login():
    """Initiate LinkedIn OAuth."""
    redirect_uri = os.getenv('LINKEDIN_REDIRECT_URI')
    return linkedin.authorize_redirect(redirect_uri)

@app.route('/api/auth/linkedin/callback')
def linkedin_callback():
    """Handle LinkedIn OAuth callback."""
    try:
        # Get the LinkedIn access token
        token = linkedin.authorize_access_token()
        if not token:
            return jsonify({"error": "Failed to obtain token"}), 400

        # Fetch user profile
        user_resp = linkedin.get('me', token=token)
        email_resp = linkedin.get('emailAddress?q=members&projection=(elements*(handle~))', token=token)
        user_info = user_resp.json()
        email_data = email_resp.json()
        email = email_data['elements'][0]['handle~']['emailAddress']

        user_data = {
            "linkedin_id": user_info.get('id'),
            "first_name": user_info.get('localizedFirstName', ''),
            "last_name": user_info.get('localizedLastName', ''),
            "email": email,
            "last_login": datetime.utcnow().isoformat(),
        }

        # Store or update user info in Supabase
        existing_user = supabase.table('users').select('*').eq('linkedin_id', user_data['linkedin_id']).execute()
        if existing_user.data:
            supabase.table('users').update(user_data).eq('linkedin_id', user_data['linkedin_id']).execute()
        else:
            supabase.table('users').insert(user_data).execute()

        session['user'] = user_data
        return jsonify({
            "message": "Login successful",
            "user": user_data,
            "token": token,
        })
    except Exception as e:
        logging.error(f"Error during LinkedIn callback: {e}")
        return jsonify({"error": "Authorization failed"}), 500

# Email/Password Authentication Routes
@app.route('/register', methods=['POST'])
def register():
    """Register a new user with email and password."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Email validation
    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError:
        return jsonify({"error": "Invalid email address"}), 400

    # Password validation
    if not validate_password(password):
        return jsonify({
            "error": "Password must be at least 8 characters long and contain uppercase, lowercase, and numeric characters"
        }), 400

    try:
        # Create user in Supabase
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return jsonify({
            "message": "User registered successfully",
            "user_id": response.user.id
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/login', methods=['POST'])
def login():
    """Login with email and password."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        # Authenticate user
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        # Set session
        session['user'] = {
            'id': response.user.id, 
            'email': email
        }

        return jsonify({
            "message": "Login successful",
            "user_id": response.user.id
        }), 200
    except Exception as e:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/reset-password', methods=['POST'])
def reset_password():
    """Send password reset email."""
    data = request.get_json()
    email = data.get('email')

    try:
        # Send password reset email
        supabase.auth.reset_password_email(email)
        return jsonify({"message": "Password reset email sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/logout', methods=['POST'])
def logout():
    """Logout the current user."""
    session.clear()
    try:
        supabase.auth.sign_out()
        return jsonify({"message": "Logged out successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)