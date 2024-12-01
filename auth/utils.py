from flask import current_app, render_template
from flask_mail import Message, Mail

mail = Mail()

def send_reset_email(email, token):
    reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password/{token}"
    
    msg = Message(
        'Reset Your Password',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[email]
    )
    
    msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request then simply ignore this email and no changes will be made.

This link will expire in 15 minutes.
'''
    
    mail.send(msg)
