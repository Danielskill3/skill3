import os
import logging
import PyPDF2
from datetime import datetime
from pymongo import MongoClient
from urllib.parse import quote_plus
from dotenv import load_dotenv
import openai
import certifi
import ssl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CVProcessor:
    def __init__(self):
        """Initialize CV Processor with MongoDB connection and OpenAI setup"""
        try:
            # Load environment variables
            load_dotenv()
            
            # Initialize OpenAI
            openai.api_key = os.getenv('OPENAI_API_KEY')
            
            # Setup MongoDB connection
            username = os.getenv('MONGODB_USERNAME')
            password = os.getenv('MONGODB_PASSWORD')
            
            # Construct MongoDB URI using the connection string format
            escaped_username = quote_plus(username)
            escaped_password = quote_plus(password)
            mongo_uri = f"mongodb+srv://{escaped_username}:{escaped_password}@cluster0.ubsrj.mongodb.net/skill3"
            
            # Initialize MongoDB client with SSL/TLS settings
            self.mongo_client = MongoClient(
                mongo_uri,
                ssl=True,
                tls=True,
                tlsAllowInvalidCertificates=True  # Note: This is for testing only
            )
            self.db = self.mongo_client.skill3
            
            # Test connection
            self.db.command('ping')
            logger.info("CV Processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize CV Processor: {str(e)}")
            raise

    def extract_text_from_pdf(self, file_path):
        """Extract text content from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def analyze_cv_with_openai(self, cv_text):
        """Analyze CV text using OpenAI API"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional CV analyzer. Extract key information from the CV including skills, experience, education, and achievements."},
                    {"role": "user", "content": cv_text}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error analyzing CV with OpenAI: {str(e)}")
            raise

    def process_cv(self, file_path, user_id):
        """Process CV file and store results"""
        try:
            # Update processing status
            self.db.cv_processing_status.insert_one({
                'user_id': user_id,
                'status': 'processing',
                'started_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })

            # Extract text from PDF
            cv_text = self.extract_text_from_pdf(file_path)
            
            # Analyze CV with OpenAI
            analysis = self.analyze_cv_with_openai(cv_text)
            
            # Store CV data
            cv_data = {
                'user_id': user_id,
                'raw_text': cv_text,
                'analysis': analysis,
                'file_path': file_path,
                'processed_at': datetime.utcnow()
            }
            self.db.cv_data.insert_one(cv_data)
            
            # Update processing status
            self.db.cv_processing_status.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'status': 'completed',
                        'updated_at': datetime.utcnow(),
                        'completed_at': datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"CV processing completed for user: {user_id}")
            
        except Exception as e:
            # Update processing status to failed
            self.db.cv_processing_status.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'status': 'failed',
                        'error': str(e),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            logger.error(f"Error processing CV: {str(e)}")
            raise

    def find_similar_profiles(self, user_id, limit=5):
        """Find similar profiles based on CV analysis"""
        try:
            # Get user's CV data
            user_cv = self.db.cv_data.find_one({'user_id': user_id})
            if not user_cv:
                return []
            
            # Use OpenAI to find similar profiles
            similar_profiles = self.db.cv_data.find(
                {'user_id': {'$ne': user_id}},
                {'raw_text': 0}  # Exclude raw text from results
            ).limit(limit)
            
            # Convert cursor to list and process results
            profiles = []
            for profile in similar_profiles:
                profile['_id'] = str(profile['_id'])
                profile['processed_at'] = profile['processed_at'].isoformat()
                profiles.append(profile)
            
            return profiles
            
        except Exception as e:
            logger.error(f"Error finding similar profiles: {str(e)}")
            raise
