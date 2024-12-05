import os
from dotenv import load_dotenv
import urllib.parse
from flask import Flask, request, jsonify, make_response
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
import bcrypt
from datetime import timedelta
from bson.json_util import dumps

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# CORS Configuration
CORS(app, 
     resources={r"/*": {
         "origins": ["http://localhost:3000", "https://skill3-frontend-1.onrender.com", "https://skill3.onrender.com"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "supports_credentials": True
     }})

# Database Configuration
username = urllib.parse.quote_plus(os.getenv('MONGODB_USERNAME'))
password = urllib.parse.quote_plus(os.getenv('MONGODB_PASSWORD'))

uri = f"mongodb+srv://{username}:{password}@cluster0.ubsrj.mongodb.net/{os.getenv('DB_NAME')}?retryWrites=true&w=majority"
app.config['MONGO_URI'] = uri
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# Initialize extensions
mongo = PyMongo(app)
jwt = JWTManager(app)

# Ensure email field is indexed for fast lookups
mongo.db.users.create_index('email', unique=True)

# Simple in-memory cache for demonstration purposes
cache = {}

# Debug route to view users
@app.route('/debug/users', methods=['GET'])
def debug_users():
    try:
        # Check cache first
        if 'users' in cache:
            return jsonify(cache['users'])

        users = list(mongo.db.users.find({}, {'email': 1, 'password': 1}))
        cache['users'] = users  # Store in cache
        response = jsonify(users)
        return response
    except Exception as e:
        print(f"Debug route error: {str(e)}")
        response = jsonify({'error': str(e)})
        response.status_code = 500
        return response

# Helper function for password hashing
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


# Helper function for password verification
def verify_password(password, hashed):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    except Exception as e:
        print(f"Password verification error: {str(e)}")
        return False

@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return ''

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        response = jsonify({'error': 'Email and password are required'})
        response.status_code = 400
        return response

    # Check if user already exists
    if mongo.db.users.find_one({'email': email}):
        response = jsonify({'error': 'User already exists'})
        response.status_code = 400
        return response

    try:
        # Hash the password and store it
        hashed_password = hash_password(password)
        
        # Insert new user with binary password hash
        mongo.db.users.insert_one({
            'email': email,
            'password': hashed_password,
            'name': data.get('name', '')  # Store the user's name from registration
        })

        response = jsonify({'message': 'User registered successfully'})
        response.status_code = 201
        return response

    except Exception as e:
        print(f"Registration error: {str(e)}")
        response = jsonify({'error': 'Registration failed'})
        response.status_code = 500
        return response

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    user = mongo.db.users.find_one({"email": email})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        token = create_access_token(identity=str(user['_id']))
        
        # Extract the part of the email before '@' as the name
        name = user.get('name', user['email'].split('@')[0])
        return jsonify({
            "token": token,
            "name": name,
            "message": "Login successful"
        }), 200
    
    return jsonify({"error": "Invalid email or password"}), 401

# Endpoint to save university details
@app.route('/api/university', methods=['POST'])
def save_university():
    try:
        data = request.json
        # Insert university details into the database
        mongo.db.universities.insert_one(data)
        return jsonify({'message': 'University details saved successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to save personality type
@app.route('/api/personality', methods=['POST'])
def save_personality():
    try:
        data = request.json
        # Insert personality type into the database
        mongo.db.personalities.insert_one(data)
        return jsonify({'message': 'Personality type saved successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to save work model
@app.route('/api/work-model', methods=['POST'])
def save_work_model():
    try:
        data = request.json
        # Insert work model into the database
        mongo.db.work_models.insert_one(data)
        return jsonify({'message': 'Work model saved successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to save industry selection
@app.route('/api/industry', methods=['POST'])
def save_industry():
    try:
        data = request.json
        # Insert industry selection into the database
        mongo.db.industries.insert_one(data)
        return jsonify({'message': 'Industry selection saved successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to save new school
@app.route('/api/schools', methods=['POST'])
def save_school():
    try:
        data = request.json
        # Insert new school into the database
        mongo.db.schools.insert_one(data)
        return jsonify({'message': 'School saved successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host=os.getenv('HOST'), port=int(os.getenv('PORT')))