from flask import Flask, jsonify, redirect, request, session
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Flask application setup
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))  # Replace in production with a secure secret key

# CORS setup for React
CORS(app, resources={r"/*": {"origins": os.getenv('FRONTEND_URL', 'http://localhost:3000')}}, supports_credentials=True)

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

# Routes
@app.route('/')
def home():
    """Default route."""
    return jsonify({"message": "Welcome to the LinkedIn OAuth backend"})

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

        return jsonify({
            "message": "Login successful",
            "user": user_data,
            "token": token,
        })
    except Exception as e:
        logging.error(f"Error during LinkedIn callback: {e}")
        return jsonify({"error": "Authorization failed"}), 500

@app.route('/api/auth/logout')
def logout():
    """Log the user out."""
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
