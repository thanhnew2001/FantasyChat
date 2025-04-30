import os
from dotenv import load_dotenv

def main():
    print("Testing environment variables...")
    print("Current working directory:", os.getcwd())
    print("Files in directory:", os.listdir('.'))
    
    # Try to load .env file
    print("\nLoading .env file...")
    load_dotenv(verbose=True)
    
    # Get and print environment variables
    openai_key = os.getenv('OPENAI_API_KEY')
    replicate_key = os.getenv('REPLICATE_API_TOKEN')
    
    print("\nEnvironment variables:")
    print(f"OPENAI_API_KEY exists: {bool(openai_key)}")
    if openai_key:
        print(f"OPENAI_API_KEY length: {len(openai_key)}")
        print(f"OPENAI_API_KEY starts with: {openai_key[:10]}...")
    
    print(f"\nREPLICATE_API_TOKEN exists: {bool(replicate_key)}")
    if replicate_key:
        print(f"REPLICATE_API_TOKEN length: {len(replicate_key)}")
        print(f"REPLICATE_API_TOKEN starts with: {replicate_key[:10]}...")

if __name__ == "__main__":
    main() 