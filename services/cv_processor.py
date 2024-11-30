import PyPDF2
from openai import OpenAI, Client
import os
from urllib.parse import quote_plus
from datetime import datetime
from typing import Dict, List, Any, Optional
import numpy as np
from pymongo import MongoClient
from bson import ObjectId
import json
from dotenv import load_dotenv
import traceback
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CVProcessor:
    _instance: Optional['CVProcessor'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CVProcessor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        # Load environment variables if not already loaded
        env_path = os.path.join(os.path.dirname(__file__), '../.env')
        load_dotenv(env_path)
        
        # Initialize OpenAI client
        self._init_openai_client()
        
        # Initialize MongoDB
        self._init_mongodb()
        
        self._initialized = True
    
    def _init_openai_client(self):
        """Initialize OpenAI client with error handling"""
        if self._client is not None:
            return
            
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set")
            
            logger.info("Initializing OpenAI client...")
            self._client = OpenAI(api_key=api_key)
            
            # Verify the client works and log its attributes
            logger.debug(f"OpenAI client attributes: {dir(self._client)}")
            models = self._client.models.list()
            logger.info("Available models: %s", [model.id for model in models])
            
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error("Error initializing OpenAI client: %s", str(e))
            logger.error("Stack trace: %s", traceback.format_exc())
            raise

    def _init_mongodb(self):
        """Initialize MongoDB client with error handling"""
        username = os.getenv('MONGODB_USERNAME')
        password = os.getenv('MONGODB_PASSWORD')
        
        if not username or not password:
            raise ValueError("MongoDB credentials are not set")
        
        try:
            # Construct MongoDB URI with properly escaped credentials
            escaped_username = quote_plus(username)
            escaped_password = quote_plus(password)
            mongo_uri = f"mongodb+srv://{escaped_username}:{escaped_password}@cluster0.ubsrj.mongodb.net/"
            
            # Initialize MongoDB client with updated SSL configuration
            self.mongo_client = MongoClient(
                mongo_uri,
                tls=True,
                tlsAllowInvalidCertificates=True,  # Only for development
                serverSelectionTimeoutMS=5000
            )
            self.db = self.mongo_client.skill3
            
            # Test connection
            self.db.command('ping')
            logger.info("MongoDB client initialized successfully")
            
            # Ensure vector search index exists
            self.ensure_vector_index()
        except Exception as e:
            logger.error("Error initializing MongoDB client: %s", str(e))
            logger.error("Stack trace: %s", traceback.format_exc())
            raise

    def update_processing_status(self, user_id: str, status: str, progress: int, data: dict = None):
        """Update CV processing status and progress"""
        try:
            update_data = {
                'user_id': ObjectId(user_id),
                'status': status,
                'progress': progress,
                'updated_at': datetime.utcnow()
            }
            
            if data:
                update_data['latest_data'] = data
            
            self.db.cv_processing_status.update_one(
                {'user_id': ObjectId(user_id)},
                {'$set': update_data},
                upsert=True
            )
            logger.debug("Updated processing status for user %s", user_id)
        except Exception as e:
            logger.error("Error updating processing status: %s", str(e))
            logger.error("Stack trace: %s", traceback.format_exc())
            raise

    def process_cv(self, file_path: str, user_id: str):
        """Process CV with incremental updates"""
        try:
            logger.info(f"Starting CV processing for user {user_id}")
            
            # Initialize processing
            self.update_processing_status(user_id, 'started', 0)
            
            # Extract text from PDF
            logger.debug("Extracting text from PDF...")
            self.update_processing_status(user_id, 'extracting_text', 10)
            with open(file_path, 'rb') as file:
                text = self.extract_text_from_pdf(file)
            self.update_processing_status(user_id, 'text_extracted', 20)
            logger.debug(f"Extracted text length: {len(text)}")

            # Process personal information
            logger.debug("Processing personal information...")
            self.update_processing_status(user_id, 'processing_personal_info', 30)
            try:
                logger.debug("OpenAI client type: %s", type(self._client))
                logger.debug("OpenAI client attributes: %s", dir(self._client))
                
                logger.info("Creating completion for personal info...")
                completion = self._client.completions.create(
                    model="gpt-3.5-turbo-instruct",
                    prompt=f"""Extract the following information from the CV in JSON format: {{name: string, email: string, phone: string, summary: string}}

CV Text:
{text}""",
                    max_tokens=500,
                    temperature=0.3,
                    n=1
                )
                logger.debug("Completion response: %s", completion)
                
                personal_info = json.loads(completion.choices[0].text.strip())
                cv_data = {'personal_info': personal_info}
                self.update_processing_status(user_id, 'personal_info_extracted', 40, {'personal_info': personal_info})
                logger.info("Personal information extracted successfully")
            except Exception as e:
                logger.error("Error in personal info extraction: %s", str(e))
                logger.error("Stack trace: %s", traceback.format_exc())
                self.update_processing_status(user_id, 'error', 30, {
                    'error': str(e),
                    'traceback': traceback.format_exc()
                })
                raise

            # Process skills
            logger.debug("Processing skills...")
            self.update_processing_status(user_id, 'processing_skills', 50)
            try:
                logger.info("Creating completion for skills...")
                completion = self._client.completions.create(
                    model="gpt-3.5-turbo-instruct",
                    prompt=f"""Extract a list of skills from the CV in JSON format: {{skills: string[]}}

CV Text:
{text}""",
                    max_tokens=500,
                    temperature=0.3,
                    n=1
                )
                logger.debug("Completion response: %s", completion)
                
                skills = json.loads(completion.choices[0].text.strip())
                cv_data['skills'] = skills['skills']
                self.update_processing_status(user_id, 'skills_extracted', 60, {'skills': skills})
                logger.info("Skills extracted successfully")
            except Exception as e:
                logger.error("Error in skills extraction: %s", str(e))
                logger.error("Stack trace: %s", traceback.format_exc())
                self.update_processing_status(user_id, 'error', 50, {
                    'error': str(e),
                    'traceback': traceback.format_exc()
                })
                raise

            # Process work experience
            logger.debug("Processing work experience...")
            self.update_processing_status(user_id, 'processing_experience', 70)
            try:
                logger.info("Creating completion for work experience...")
                completion = self._client.completions.create(
                    model="gpt-3.5-turbo-instruct",
                    prompt=f"""Extract work experience from the CV in JSON format:
{{
    work_experience: [
        {{
            company: string,
            position: string,
            start_date: string,
            end_date: string,
            description: string,
            achievements: string[]
        }}
    ]
}}

CV Text:
{text}""",
                    max_tokens=1000,
                    temperature=0.3,
                    n=1
                )
                logger.debug("Completion response: %s", completion)
                
                work_experience = json.loads(completion.choices[0].text.strip())
                cv_data['work_experience'] = work_experience['work_experience']
                self.update_processing_status(user_id, 'experience_extracted', 80, {'work_experience': work_experience})
                logger.info("Work experience extracted successfully")
            except Exception as e:
                logger.error("Error in work experience extraction: %s", str(e))
                logger.error("Stack trace: %s", traceback.format_exc())
                self.update_processing_status(user_id, 'error', 70, {
                    'error': str(e),
                    'traceback': traceback.format_exc()
                })
                raise

            # Process education
            logger.debug("Processing education...")
            self.update_processing_status(user_id, 'processing_education', 90)
            try:
                logger.info("Creating completion for education...")
                completion = self._client.completions.create(
                    model="gpt-3.5-turbo-instruct",
                    prompt=f"""Extract education information from the CV in JSON format:
{{
    education: [
        {{
            institution: string,
            degree: string,
            field: string,
            start_date: string,
            end_date: string,
            achievements: string[]
        }}
    ]
}}

CV Text:
{text}""",
                    max_tokens=1000,
                    temperature=0.3,
                    n=1
                )
                logger.debug("Completion response: %s", completion)
                
                education = json.loads(completion.choices[0].text.strip())
                cv_data['education'] = education['education']
                self.update_processing_status(user_id, 'education_extracted', 95, {'education': education})
                logger.info("Education extracted successfully")
            except Exception as e:
                logger.error("Error in education extraction: %s", str(e))
                logger.error("Stack trace: %s", traceback.format_exc())
                self.update_processing_status(user_id, 'error', 90, {
                    'error': str(e),
                    'traceback': traceback.format_exc()
                })
                raise

            # Create embeddings for skills and achievements
            skills_text = ", ".join(cv_data['skills'])
            achievements_text = ""
            for exp in cv_data['work_experience']:
                achievements_text += ", ".join(exp.get('achievements', []))
            
            logger.info("Creating embeddings for skills and achievements...")
            cv_data['skills_vector'] = self.get_embedding(skills_text)
            cv_data['achievements_vector'] = self.get_embedding(achievements_text)
            logger.info("Embeddings created successfully")

            # Save to database
            logger.info("Saving data to database...")
            self.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': cv_data},
                upsert=True
            )
            logger.info("Data saved successfully")
            
            self.update_processing_status(user_id, 'completed', 100)
            logger.info("CV processing completed successfully")
            return cv_data
            
        except Exception as e:
            logger.error("Error processing CV: %s", str(e))
            logger.error("Stack trace: %s", traceback.format_exc())
            self.update_processing_status(user_id, 'error', 0, {
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            raise

    def extract_text_from_pdf(self, file) -> str:
        """Extract text content from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            logger.debug(f"Extracted text length: {len(text)}")
            return text
        except Exception as e:
            logger.error("Error extracting text from PDF: %s", str(e))
            logger.error("Stack trace: %s", traceback.format_exc())
            raise

    def get_embedding(self, text: str) -> List[float]:
        """Get OpenAI embedding for text"""
        try:
            logger.info("Creating embedding for text...")
            response = self._client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            logger.debug("Embedding response: %s", response)
            return response.data[0].embedding
        except Exception as e:
            logger.error("Error getting embedding: %s", str(e))
            logger.error("Stack trace: %s", traceback.format_exc())
            raise

    def ensure_vector_index(self):
        """Create vector search index if it doesn't exist"""
        try:
            if "vector_index" not in self.db.users.list_indexes():
                logger.info("Creating vector search index...")
                self.db.users.create_index([
                    ("skills_vector", "2dsphere"),
                    ("achievements_vector", "2dsphere")
                ])
                logger.info("Vector search index created successfully")
        except Exception as e:
            logger.error("Error creating vector search index: %s", str(e))
            logger.error("Stack trace: %s", traceback.format_exc())
            raise

    def find_similar_profiles(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Find profiles with similar skills and achievements"""
        try:
            logger.info(f"Finding similar profiles for user {user_id}...")
            user = self.db.users.find_one({'_id': ObjectId(user_id)})
            if not user:
                logger.error("User not found")
                return []
            
            # Find similar profiles based on skills and achievements vectors
            similar_profiles = self.db.users.find({
                '_id': {'$ne': ObjectId(user_id)},
                '$or': [
                    {'skills_vector': {'$near': user['skills_vector']}},
                    {'achievements_vector': {'$near': user['achievements_vector']}}
                ]
            }).limit(limit)
            logger.info("Similar profiles found successfully")
            return list(similar_profiles)
        except Exception as e:
            logger.error("Error finding similar profiles: %s", str(e))
            logger.error("Stack trace: %s", traceback.format_exc())
            raise
