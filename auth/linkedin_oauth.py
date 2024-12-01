from flask import current_app, url_for, session, request
from linkedin_v2 import linkedin
import json
import os

def get_linkedin():
    return linkedin.LinkedInApplication(
        token=session.get('linkedin_token'),
        authentication={
            'client_id': current_app.config['LINKEDIN_CLIENT_ID'],
            'client_secret': current_app.config['LINKEDIN_CLIENT_SECRET'],
            'redirect_uri': url_for('auth.linkedin_callback', _external=True)
        }
    )

def authorize():
    linkedin = get_linkedin()
    return linkedin.get_authorization_url()

def callback():
    code = request.args.get('code')
    linkedin = get_linkedin()
    
    # Get access token
    authentication = linkedin.authentication
    token = linkedin.get_access_token(code)
    session['linkedin_token'] = token
    
    # Get basic profile data
    profile = linkedin.get_profile()
    email = linkedin.get_email_address()
    
    return {
        'email': email,
        'name': f"{profile.get('firstName', '')} {profile.get('lastName', '')}".strip(),
        'linkedin_id': profile.get('id'),
        'profile_url': profile.get('publicProfileUrl')
    }
