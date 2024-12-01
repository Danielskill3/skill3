from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from .models import User
from .utils import send_reset_email
import linkedin_oauth

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.get_by_email(data['email']):
        return jsonify({"error": "Email already registered"}), 400
    
    user = User(
        email=data['email'],
        full_name=data.get('full_name'),
        university=data.get('university'),
        education=data.get('education'),
        career_goal=data.get('career_goal'),
        career_path=data.get('career_path'),
        industry_preferences=data.get('industry_preferences'),
        dream_companies=data.get('dream_companies'),
        work_mode=data.get('work_mode'),
        personality_type=data.get('personality_type')
    )
    user.set_password(data['password'])
    user.save()
    
    access_token = create_access_token(identity=str(user._id))
    return jsonify({
        "message": "User registered successfully",
        "access_token": access_token
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.get_by_email(data['email'])
    
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid email or password"}), 401
    
    access_token = create_access_token(identity=str(user._id))
    return jsonify({
        "access_token": access_token,
        "user": {
            "email": user.email,
            "full_name": user.full_name
        }
    })

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    user = User.get_by_email(data['email'])
    
    if not user:
        return jsonify({"error": "Email not found"}), 404
    
    token = user.set_reset_token()
    send_reset_email(user.email, token)
    
    return jsonify({
        "message": "Password reset link sent to your email"
    })

@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    user = User.verify_reset_token(token)
    if not user:
        return jsonify({"error": "Invalid or expired reset token"}), 400
    
    data = request.get_json()
    user.set_password(data['password'])
    user.reset_token = None
    user.reset_token_exp = None
    user.save()
    
    return jsonify({"message": "Password reset successful"})

@auth_bp.route('/linkedin/auth', methods=['GET'])
def linkedin_auth():
    return linkedin_oauth.authorize()

@auth_bp.route('/linkedin/callback')
def linkedin_callback():
    try:
        user_info = linkedin_oauth.callback()
        user = User.get_by_email(user_info['email'])
        
        if not user:
            user = User(
                email=user_info['email'],
                full_name=user_info['name'],
                # Add other LinkedIn profile data as needed
            )
            user.save()
        
        access_token = create_access_token(identity=str(user._id))
        return jsonify({
            "access_token": access_token,
            "user": {
                "email": user.email,
                "full_name": user.full_name
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    # Implement get user profile logic
    return jsonify({"message": "Profile data"})
