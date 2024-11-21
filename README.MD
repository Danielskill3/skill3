# Supabase Email Authentication System

## Prerequisites
- Python 3.8+
- Supabase Account
- Flask
- Supabase Python Library

## Setup Steps

1. **Create Supabase Project**
   - Sign up at supabase.com
   - Create a new project
   - Go to Project Settings > API
   - Copy Project URL and Anon Key

2. **Project Configuration**
   ```bash
   # Clone the project
   git clone <your-repo-url>
   cd supabase_auth_project

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

   # Install dependencies
   pip install -r requirements.txt

   # Create .env file
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   ```

3. **Authentication Endpoints**
   - `/register`: Create new user
   - `/login`: User login
   - `/logout`: User logout
   - `/reset-password`: Password reset

4. **Password Requirements**
   - Minimum 8 characters
   - Contains uppercase letter
   - Contains lowercase letter
   - Contains number

## Security Notes
- Uses environment variables for credentials
- Implements password complexity validation
- Leverages Supabase's secure authentication

## Running the Application
```bash
python app.py
```

## Testing with Postman/curl
- Register: `POST /register` with `{"email": "user@example.com", "password": "StrongPass123"}`
- Login: `POST /login` with same credentials
- Logout: `POST /logout`
- Reset Password: `POST /reset-password` with `{"email": "user@example.com"}`