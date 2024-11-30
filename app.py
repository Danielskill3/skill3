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
import certifi

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app and configure CORS
app = Flask(__name__)

# Configure CORS with all necessary settings
CORS(app, 
     resources={
         r"/*": {
             "origins": [
                 "http://localhost:5173",
                 "http://localhost:3000",
                 "https://skill3-frontend.onrender.com",
                 "https://skill3-react.onrender.com",
                 "https://skill3-login.onrender.com"
             ],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
             "expose_headers": ["Authorization", "Content-Type"],
             "supports_credentials": True,
             "max_age": 600
         }
     })

# Add OPTIONS handler for all routes
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    return '', 204

# Configure JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
jwt = JWTManager(app)

# Configure Flask app
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
    mongodb_uri = f"mongodb+srv://{mongodb_username}:{mongodb_password}@cluster0.ubsrj.mongodb.net/?retryWrites=true&w=majority"
    
    client = MongoClient(
        mongodb_uri,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=20000,
        socketTimeoutMS=20000
    )
    db = client.skill3_db
    
    # Test connection
    db.command('ping')
    logger.info("Successfully connected to MongoDB")
    
    def initialize_universities():
        """Initialize the universities collection with Danish universities"""
        danish_universities = [
            {"name": "University of Copenhagen", "country": "Denmark", "city": "Copenhagen"},
            {"name": "Technical University of Denmark (DTU)", "country": "Denmark", "city": "Lyngby"},
            {"name": "Aarhus University", "country": "Denmark", "city": "Aarhus"},
            {"name": "Aalborg University", "country": "Denmark", "city": "Aalborg"},
            {"name": "University of Southern Denmark", "country": "Denmark", "city": "Odense"},
            {"name": "Copenhagen Business School", "country": "Denmark", "city": "Copenhagen"},
            {"name": "IT University of Copenhagen", "country": "Denmark", "city": "Copenhagen"},
            {"name": "Roskilde University", "country": "Denmark", "city": "Roskilde"},
            {"name": "VIA University College", "country": "Denmark", "city": "Aarhus"},
            {"name": "Copenhagen School of Design and Technology", "country": "Denmark", "city": "Copenhagen"}
        ]

        try:
            # Check if universities already exist
            existing_count = db.universities.count_documents({})
            if existing_count == 0:
                # Insert universities if collection is empty
                db.universities.insert_many(danish_universities)
                logger.info(f"Successfully initialized {len(danish_universities)} Danish universities")
            else:
                logger.info(f"Universities collection already contains {existing_count} documents")
        except Exception as e:
            logger.error(f"Error initializing universities: {str(e)}")

    initialize_universities()
    
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise

# Add universities endpoint
@app.route('/v1/universities', methods=['GET'])
def get_universities():
    try:
        # Add debug logging
        logger.info("Fetching universities from database")
        universities = list(db.universities.find({}, {'_id': 0}))
        logger.info(f"Found {len(universities)} universities")
        
        if not universities:
            # If no universities found, try to initialize again
            initialize_universities()
            universities = list(db.universities.find({}, {'_id': 0}))
            logger.info(f"After initialization, found {len(universities)} universities")
        
        return jsonify(universities), 200
    except Exception as e:
        logger.error(f"Error fetching universities: {str(e)}")
        return jsonify({'error': f'Failed to fetch universities: {str(e)}'}), 500

# Add API test endpoints
@app.route('/v1/test', methods=['GET'])
def test_endpoint():
    return jsonify({'message': 'API is working'}), 200

@app.route('/v1/test/universities', methods=['GET'])
def test_universities():
    try:
        # Count universities
        count = db.universities.count_documents({})
        # Get a sample university
        sample = db.universities.find_one({}, {'_id': 0})
        return jsonify({
            'status': 'success',
            'university_count': count,
            'sample_university': sample,
            'mongodb_connected': True
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'mongodb_connected': False
        }), 500

# Add health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'mongodb': 'connected' if cv_processor else 'disconnected'
    }), 200

# Routes
@app.route('/v1/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        logger.info("Received registration request")
        
        # Validate required fields
        required_fields = ['email', 'password', 'name']
        if not all(field in data for field in required_fields):
            missing_fields = [field for field in required_fields if field not in data]
            logger.error(f"Missing required fields: {missing_fields}")
            return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400
        
        # Check if user already exists
        existing_user = db.users.find_one({'email': data['email']})
        if existing_user:
            logger.warning(f"Attempt to register existing email: {data['email']}")
            return jsonify({'error': 'Email already registered', 'code': 'EMAIL_EXISTS'}), 409
        
        # Create new user
        new_user = {
            'email': data['email'],
            'password': generate_password_hash(data['password']),
            'name': data['name'],
            'created_at': datetime.utcnow()
        }
        
        result = db.users.insert_one(new_user)
        logger.info(f"Successfully created new user with ID: {result.inserted_id}")
        
        # Create access token
        access_token = create_access_token(identity=str(result.inserted_id))
        
        response = jsonify({
            'message': 'Registration successful',
            'access_token': access_token,
            'user': {
                'id': str(result.inserted_id),
                'name': data['name'],
                'email': data['email']
            }
        })
        return response, 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': str(e), 'code': 'SERVER_ERROR'}), 500

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

@app.route('/v1/cv/upload', methods=['POST'])
def upload_cv():
    try:
        # Get the token from the request header
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'No token provided'}), 401

        # Verify the token and get the user ID
        try:
            user_id = get_jwt_identity()
        except Exception as e:
            return jsonify({'error': 'Invalid token'}), 401

        # Check if file is present in request
        if 'cv' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['cv']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Get additional information
        university = request.form.get('university', 'Not Specified')
        program = request.form.get('program', 'Not Specified')
        graduation_year = request.form.get('graduationYear', 'Not Specified')

        # Process the CV
        cv_processor.process_cv(
            file,
            user_id=user_id,
            university=university,
            program=program,
            graduation_year=graduation_year
        )

        return jsonify({
            'message': 'CV uploaded and processed successfully',
            'user_id': user_id
        }), 200

    except Exception as e:
        logger.error(f"Error in CV upload: {str(e)}")
        return jsonify({'error': f'Failed to upload CV: {str(e)}'}), 500

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
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
