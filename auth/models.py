from datetime import datetime, timedelta
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from ..mongodb_config import get_database

class User:
    def __init__(self, email, password_hash=None, full_name=None, university=None, 
                 education=None, career_goal=None, career_path=None, 
                 industry_preferences=None, dream_companies=None, 
                 work_mode=None, personality_type=None, cv_url=None):
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.university = university
        self.education = education
        self.career_goal = career_goal
        self.career_path = career_path
        self.industry_preferences = industry_preferences or []
        self.dream_companies = dream_companies or []
        self.work_mode = work_mode
        self.personality_type = personality_type
        self.cv_url = cv_url
        self.created_at = datetime.utcnow()
        self.reset_token = None
        self.reset_token_exp = None

    @staticmethod
    def get_by_email(email):
        db = get_database()
        user_data = db.users.find_one({"email": email})
        if user_data:
            return User.from_dict(user_data)
        return None

    @staticmethod
    def from_dict(data):
        user = User(
            email=data['email'],
            password_hash=data.get('password_hash'),
            full_name=data.get('full_name'),
            university=data.get('university'),
            education=data.get('education'),
            career_goal=data.get('career_goal'),
            career_path=data.get('career_path'),
            industry_preferences=data.get('industry_preferences'),
            dream_companies=data.get('dream_companies'),
            work_mode=data.get('work_mode'),
            personality_type=data.get('personality_type'),
            cv_url=data.get('cv_url')
        )
        user._id = data.get('_id')
        user.created_at = data.get('created_at', datetime.utcnow())
        user.reset_token = data.get('reset_token')
        user.reset_token_exp = data.get('reset_token_exp')
        return user

    def to_dict(self):
        return {
            "_id": getattr(self, '_id', None),
            "email": self.email,
            "password_hash": self.password_hash,
            "full_name": self.full_name,
            "university": self.university,
            "education": self.education,
            "career_goal": self.career_goal,
            "career_path": self.career_path,
            "industry_preferences": self.industry_preferences,
            "dream_companies": self.dream_companies,
            "work_mode": self.work_mode,
            "personality_type": self.personality_type,
            "cv_url": self.cv_url,
            "created_at": self.created_at,
            "reset_token": self.reset_token,
            "reset_token_exp": self.reset_token_exp
        }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save(self):
        db = get_database()
        data = self.to_dict()
        if hasattr(self, '_id') and self._id:
            db.users.update_one({"_id": self._id}, {"$set": data})
        else:
            result = db.users.insert_one(data)
            self._id = result.inserted_id

    def set_reset_token(self):
        import secrets
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_exp = datetime.utcnow() + timedelta(minutes=15)
        self.save()
        return self.reset_token

    @staticmethod
    def verify_reset_token(token):
        db = get_database()
        user_data = db.users.find_one({
            "reset_token": token,
            "reset_token_exp": {"$gt": datetime.utcnow()}
        })
        if user_data:
            return User.from_dict(user_data)
        return None
