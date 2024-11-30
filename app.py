from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import os
import logging
import urllib.parse
from dotenv import load_dotenv
from services.cv_processor import CVProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, 
     resources={r"/v1/*": {
         "origins": ["http://localhost:5173"],
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

# Initialize CV Processor
cv_processor = None
try:
    cv_processor = CVProcessor()
    logger.info("CV Processor initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize CV Processor: {str(e)}")
    raise

# Connect to MongoDB
try:
    mongodb_username = urllib.parse.quote_plus(os.getenv('MONGODB_USERNAME'))
    mongodb_password = urllib.parse.quote_plus(os.getenv('MONGODB_PASSWORD'))
    mongodb_uri = f"mongodb+srv://{mongodb_username}:{mongodb_password}@cluster0.ubsrj.mongodb.net/"
    
    client = MongoClient(
        mongodb_uri,
        tls=True,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=5000
    )
    db = client.skill3_db
    
    # Test connection
    db.command('ping')
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise

# Routes
@app.route('/v1/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'name']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user already exists
        if db.users.find_one({'email': data['email']}):
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        new_user = {
            'email': data['email'],
            'password': generate_password_hash(data['password']),
            'name': data['name'],
            'created_at': datetime.utcnow()
        }
        
        result = db.users.insert_one(new_user)
        
        # Create access token
        access_token = create_access_token(identity=str(result.inserted_id))
        
        return jsonify({
            'message': 'Registration successful',
            'access_token': access_token
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/v1/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = db.users.find_one({'email': data['email']})
        if not user or not check_password_hash(user['password'], data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create access token
        access_token = create_access_token(identity=str(user['_id']))
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/v1/profile/cv/upload', methods=['POST'])
@jwt_required()
def upload_cv():
    try:
        user_id = get_jwt_identity()
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
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
    try:
        user_id = get_jwt_identity()
        logger.info(f"Checking CV processing status for user: {user_id}")
        
        # Find the latest processing status
        status = db.cv_processing_status.find_one(
            {'user_id': user_id},
            sort=[('updated_at', -1)]
        )
        
        if not status:
            return jsonify({
                'status': 'not_found',
                'message': 'No CV processing status found'
            }), 404
        
        # Convert ObjectId to string for JSON serialization
        status['_id'] = str(status['_id'])
        if isinstance(status.get('updated_at'), datetime):
            status['updated_at'] = status['updated_at'].isoformat()
            
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
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 5))
        
        similar_profiles = cv_processor.find_similar_profiles(user_id, limit)
        return jsonify(similar_profiles), 200
        
    except Exception as e:
        logger.error(f"Error finding similar profiles: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
