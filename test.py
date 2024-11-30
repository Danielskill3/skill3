from pymongo import MongoClient
import os
from dotenv import load_dotenv
import urllib.parse
from datetime import datetime

# Load environment variables
load_dotenv()

# Print all environment variables for debugging
print("Environment Variables:")
for key, value in os.environ.items():
    print(f"{key}: {value}")

# Get MongoDB credentials
username = os.getenv('MONGODB_USERNAME')
password = os.getenv('MONGODB_PASSWORD')

print(f"\nUsername: {username}")
print(f"Password: {password}")

if not username or not password:
    print("ERROR: MongoDB credentials not found in environment variables!")
    exit(1)

# URL encode the username and password
username = urllib.parse.quote_plus(username)
password = urllib.parse.quote_plus(password)

# Construct the MongoDB URI
mongo_uri = f'mongodb+srv://{username}:{password}@cluster0.ubsrj.mongodb.net/skill3_db?retryWrites=true&w=majority'

print(f"\nAttempting to connect to: {mongo_uri}")

try:
    # Create a MongoClient
    client = MongoClient(mongo_uri)
    
    # Test the connection by accessing the admin database
    client.admin.command('ismaster')
    
    # Get or create the database
    db = client.skill3_db
    
    print("Connection successful!")
    print(f"Database name: {db.name}")
    
    # Create or get the users collection
    users_collection = db.users
    
    # Check if the collection is empty
    user_count = users_collection.count_documents({})
    print(f"Current number of users: {user_count}")
    
    # If no users exist, insert a test user
    if user_count == 0:
        test_user = {
            'email': 'test_user@example.com',
            'fullName': 'Test User',
            'registrationStep': 1,
            'createdAt': datetime.utcnow()
        }
        result = users_collection.insert_one(test_user)
        print(f"Inserted test user with ID: {result.inserted_id}")
    
    # List all collections
    print("\nCollections:")
    print(db.list_collection_names())
    
    # Print some details about the users collection
    print("\nUsers Collection Details:")
    print(f"Number of documents: {users_collection.count_documents({})}")
    
    # Fetch and print the first user
    first_user = users_collection.find_one()
    if first_user:
        print("\nFirst User:")
        print(first_user)

except Exception as e:
    print(f"Connection failed: {e}")
    import traceback
    traceback.print_exc()
