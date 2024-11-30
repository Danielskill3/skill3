from openai import OpenAI
import os
from dotenv import load_dotenv

def test_openai_connection():
    # Load environment variables
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(env_path)
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables")
        return False
        
    try:
        # Initialize client
        client = OpenAI(api_key=api_key)
        
        # Test API connection
        models = client.models.list()
        print("Successfully connected to OpenAI API")
        print("Available models:", [model.id for model in models.data[:5]])  # Show first 5 models
        
        # Test chat completion
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello!"}]
        )
        print("\nChat completion test:")
        print(completion.choices[0].message.content)
        return True
        
    except Exception as e:
        print(f"Error testing OpenAI connection: {str(e)}")
        return False

if __name__ == "__main__":
    test_openai_connection()
