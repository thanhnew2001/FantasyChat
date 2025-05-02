from flask import Flask, render_template, request, jsonify, url_for
import openai
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecretkey')

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Character configurations
CHARACTERS = json.load(open(os.path.join(os.path.dirname(__file__), 'characters.json'), 'r'))

# Update the default system message to be character-specific
def get_system_message(character_id="luna"):
    return CHARACTERS[character_id]["system_message"]

@app.route('/')
def home():
    return render_template('index.html', characters=CHARACTERS)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    character_id = data.get('character_id', 'luna')
    
    try:
        # Build messages list using client-provided history to preserve context
        history = data.get('history', [])
        messages = [{"role": "system", "content": get_system_message(character_id)}] + history + [{"role": "user", "content": user_message}]
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        bot_response = response.choices[0].message.content
        
        # Return bot response; client will update localStorage with history
        return jsonify({
            "response": bot_response,
            "character": CHARACTERS[character_id]
        })
    
    except Exception as e:
        print(f"Error in chat process: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5050)
