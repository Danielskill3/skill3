import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # MongoDB settings
    MONGODB_URL: str = f"mongodb+srv://{os.getenv('MONGODB_USERNAME', '')}:{os.getenv('MONGODB_PASSWORD', '')}@cluster0.mongodb.net/{os.getenv('DB_NAME', '')}"
    MONGODB_DB_NAME: str = os.getenv('DB_NAME', 'skill3_db')
    
    # Application settings
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', 8000))
    DEBUG: bool = os.getenv('FLASK_DEBUG', '0') == '1'
    
    # JWT settings
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'fallback-secret-key')
    
    # Email settings (placeholder, update with actual email configuration if needed)
    MAIL_SERVER: str = 'smtp.gmail.com'
    MAIL_PORT: int = 587
    MAIL_USE_TLS: bool = True
    MAIL_USERNAME: str = os.getenv('EMAIL_USERNAME', '')
    MAIL_PASSWORD: str = os.getenv('EMAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER: str = os.getenv('EMAIL_DEFAULT_SENDER', '')
    
    # LinkedIn OAuth settings
    LINKEDIN_CLIENT_ID: str = os.getenv('LINKEDIN_CLIENT_ID', '')
    LINKEDIN_CLIENT_SECRET: str = os.getenv('LINKEDIN_SECRET_KEY', '')
    LINKEDIN_REDIRECT_URI: str = os.getenv('LINKEDIN_REDIRECT_URI', '')
    
    # Frontend URL with multiple fallback options
    @property
    def FRONTEND_URLS(self) -> list:
        # Priority order: 
        # 1. Environment variable
        # 2. Production URLs
        # 3. Local development URLs
        frontend_urls = [
            os.getenv('FRONTEND_URL'),
            'https://skill3-frontend.onrender.com',
            'https://skill3.onrender.com',
            'http://localhost:3000',
            'http://127.0.0.1:3000',
            'http://192.168.100.82:3000'
        ]
        
        # Remove None and empty strings
        return [url for url in frontend_urls if url]
    
    @property
    def FRONTEND_URL(self) -> str:
        # Return the first available URL
        return self.FRONTEND_URLS[0] if self.FRONTEND_URLS else 'http://localhost:3000'
    
    # Pinecone settings
    PINECONE_API_KEY: str = os.getenv('PINECONE_API_KEY', '')
    PINECONE_ENVIRONMENT: str = os.getenv('PINECONE_ENVIRONMENT', '')
    PINECONE_INDEX_NAME: str = os.getenv('PINECONE_INDEX_NAME', '')
    
    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')

    # Allow extra environment variables
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra='allow'
    )

    # Additional method to access any environment variable
    def get_env(self, key: str, default: str = '') -> str:
        return os.getenv(key, default)

settings = Settings()
