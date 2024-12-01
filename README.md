# Skill3 Authentication Service

## Setup Instructions

### Prerequisites
- Python 3.10+
- pip
- virtualenv (recommended)

### Installation Steps

1. Clone the repository
```bash
git clone <repository-url>
cd skill3
```

2. Create a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
- Copy `.env.example` to `.env`
- Fill in the required environment variables

5. Run the application
```bash
# Development
flask run

# Production
gunicorn -w 4 wsgi:app
```

### Environment Variables
- `MONGODB_URL`: MongoDB connection string
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `LINKEDIN_CLIENT_ID`: LinkedIn OAuth Client ID
- `LINKEDIN_SECRET_KEY`: LinkedIn OAuth Client Secret
- `FRONTEND_URL`: URL of the frontend application

### Authentication Endpoints
- `/auth/register`: User registration
- `/auth/login`: User login
- `/auth/forgot-password`: Initiate password reset
- `/auth/reset-password/<token>`: Complete password reset
- `/auth/linkedin/auth`: LinkedIn OAuth login
- `/auth/profile`: Get user profile (protected route)

### Development
- Always activate the virtual environment before working
- Use `pip freeze > requirements.txt` to update dependencies
- Run tests before committing changes
