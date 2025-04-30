import os
from dotenv import load_dotenv
import openai
import replicate

def clean_api_key(key):
    """Clean API key by removing trailing characters and whitespace"""
    return key.strip().rstrip('$') if key else None

def verify_openai_key():
    print("Verifying OpenAI API key...")
    try:
        # Get and clean the key
        key = clean_api_key(os.getenv('OPENAI_API_KEY'))
        print(f"Key starts with: {key[:10]}...")
        
        # Make a simple API call
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        print("✅ OpenAI API key is valid!")
        return True
    except Exception as e:
        print(f"❌ OpenAI API key error: {str(e)}")
        print(f"Error type: {type(e)}")
        return False

def verify_replicate_key():
    print("\nVerifying Replicate API key...")
    try:
        # Get and clean the key
        key = clean_api_key(os.getenv('REPLICATE_API_TOKEN'))
        print(f"Key starts with: {key[:10]}...")
        
        # Initialize client
        client = replicate.Client(api_token=key)
        # Try to list models (lightweight operation)
        client.models.list()
        print("✅ Replicate API key is valid!")
        return True
    except Exception as e:
        print(f"❌ Replicate API key error: {str(e)}")
        print(f"Error type: {type(e)}")
        return False

def main():
    print("Current working directory:", os.getcwd())
    print("Files in current directory:", os.listdir('.'))
    
    # Load environment variables
    load_dotenv(verbose=True)
    
    print("\nChecking API keys in .env file...")
    
    # Check if keys exist and clean them
    openai_key = clean_api_key(os.getenv('OPENAI_API_KEY'))
    replicate_key = clean_api_key(os.getenv('REPLICATE_API_TOKEN'))
    
    if not openai_key:
        print("❌ OPENAI_API_KEY not found in .env file")
    else:
        print(f"✅ OPENAI_API_KEY found (length: {len(openai_key)})")
        print(f"Key starts with: {openai_key[:10]}...")
    
    if not replicate_key:
        print("❌ REPLICATE_API_TOKEN not found in .env file")
    else:
        print(f"✅ REPLICATE_API_TOKEN found (length: {len(replicate_key)})")
        print(f"Key starts with: {replicate_key[:10]}...")
    
    print("\nVerifying API keys...")
    openai_valid = verify_openai_key()
    replicate_valid = verify_replicate_key()
    
    if not openai_valid or not replicate_valid:
        print("\n❌ Some API keys are invalid. Please check your .env file and update the keys.")
    else:
        print("\n✅ All API keys are valid!")

if __name__ == "__main__":
    main() 