from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import os
import sys
import json
import urllib.parse
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from dotenv import load_dotenv
from services.cv_processor import CVProcessor
from celery import Celery
from redis import Redis
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables from the correct path
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# Initialize CV Processor early to catch any initialization errors
try:
    cv_processor = CVProcessor()
    logger.info("CV Processor initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize CV Processor: {str(e)}")
    raise

app = Flask(__name__)

# Configure CORS
CORS(app, 
     resources={r"/v1/*": {
         "origins": ["http://localhost:5173"],  # React dev server
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "supports_credentials": True
     }},
     expose_headers=["Content-Range", "X-Content-Range"])

# Configure Flask app
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize JWT
jwt = JWTManager(app)

# Connect to MongoDB
try:
    mongodb_username = urllib.parse.quote_plus(os.getenv('MONGODB_USERNAME'))
    mongodb_password = urllib.parse.quote_plus(os.getenv('MONGODB_PASSWORD'))
    mongodb_uri = f"mongodb+srv://{mongodb_username}:{mongodb_password}@cluster0.ubsrj.mongodb.net/skill3?retryWrites=true&w=majority"
    
    client = MongoClient(
        mongodb_uri,
        tls=True,
        tlsAllowInvalidCertificates=True,  # Only for development
        serverSelectionTimeoutMS=5000
    )
    db = client.skill3_db
    
    # Test connection
    db.command('ping')
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise

# Configure Mail
mail = Mail(app)

# Initialize Redis
redis_client = Redis(host='localhost', port=6379, db=0)

@app.route('/v1/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    logger.debug("Received registration request")
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')

        if not email or not password or not name:
            return jsonify({'error': 'Missing required fields'}), 400

        # Check if user already exists
        if db.users.find_one({'email': email}):
            return jsonify({'error': 'Email already registered'}), 409

        # Hash password and create user
        hashed_password = generate_password_hash(password)
        user = {
            'email': email,
            'password': hashed_password,
            'name': name,
            'created_at': datetime.utcnow()
        }
        
        result = db.users.insert_one(user)
        
        # Create access token
        access_token = create_access_token(identity=str(result.inserted_id))
        
        logger.info(f"User registered successfully: {email}")
        return jsonify({
            'message': 'Registration successful',
            'access_token': access_token
        }), 201
        
    except Exception as e:
        logger.error(f"Error in registration: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/v1/auth/login', methods=['POST'])
def login():
    """Login user"""
    logger.debug("Received login request")
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Missing email or password'}), 400

        # Find user
        user = db.users.find_one({'email': email})
        if not user or not check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid email or password'}), 401

        # Create access token
        access_token = create_access_token(identity=str(user['_id']))
        
        logger.info(f"User logged in successfully: {email}")
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token
        }), 200
        
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/v1/profile/cv/upload', methods=['POST'])
@jwt_required()
def upload_cv():
    """Upload and process CV"""
    logger.debug("Received CV upload request")
    try:
        user_id = get_jwt_identity()
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400

        # Save file
        filename = f"{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process CV
        try:
            cv_processor.process_cv(filepath, user_id)
            logger.info(f"CV processing started for user: {user_id}")
            return jsonify({'message': 'CV upload successful and processing started'}), 202
        except Exception as e:
            logger.error(f"Error processing CV: {str(e)}")
            return jsonify({'error': 'Error processing CV'}), 500
            
    except Exception as e:
        logger.error(f"Error in CV upload: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/v1/profile/cv/processing-status', methods=['GET'])
@jwt_required()
def get_cv_processing_status():
    """Get CV processing status"""
    logger.debug("Received CV processing status request")
    try:
        user_id = get_jwt_identity()
        logger.info(f"Checking CV processing status for user: {user_id}")
        
        # Find the latest processing status
        status = db.processing_status.find_one(
            {'user_id': user_id},  
            sort=[('updated_at', -1)]
        )
        
        if not status:
            logger.info(f"No processing status found for user: {user_id}")
            return jsonify({
                'status': 'not_found',
                'message': 'No CV processing status found'
            }), 404
        
        # Convert ObjectId to string for JSON serialization
        status['_id'] = str(status['_id'])
        if isinstance(status.get('updated_at'), datetime):
            status['updated_at'] = status['updated_at'].isoformat()
            
        logger.info(f"Returning processing status for user: {user_id}")
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Error getting CV processing status: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/v1/profile/cv/similar', methods=['GET'])
@jwt_required()
def get_similar_profiles():
    """Get similar profiles based on CV"""
    logger.debug("Received similar profiles request")
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 5))
        
        similar_profiles = cv_processor.find_similar_profiles(user_id, limit)
        
        # Convert ObjectId to string for JSON serialization
        for profile in similar_profiles:
            profile['_id'] = str(profile['_id'])
        
        logger.info(f"Found {len(similar_profiles)} similar profiles for user: {user_id}")
        return jsonify(similar_profiles), 200
        
    except Exception as e:
        logger.error(f"Error getting similar profiles: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Log all registered routes
logger.info("Registered routes:")
for rule in app.url_map.iter_rules():
    logger.info(f"Route: {rule.rule} Methods: {rule.methods}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
