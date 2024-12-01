from skill3.mongodb_config import get_database

def test_db_connection():
    try:
        db = get_database()
        print("Database connection successful!")
        print(f"Connected to database: {db.name}")
        
        # Test a simple operation
        test_collection = db['test_collection']
        test_collection.insert_one({"test": "connection"})
        print("Test document inserted successfully.")
        
        # Clean up test document
        test_collection.delete_one({"test": "connection"})
        print("Test document removed.")
        
    except Exception as e:
        print(f"Database connection failed: {e}")

if __name__ == "__main__":
    test_db_connection()
