from flask import Flask, render_template, request, jsonify, url_for
import openai
import os
import json
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecretkey')

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Load character configurations from JSON file
def load_characters():
    with open('characters.json', 'r') as f:
        return json.load(f)

CHARACTERS = load_characters()

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
        
        # Add narrative context reminder to user's message
        narrative_context = f"[Remember to stay in character and maintain the narrative style. Describe {CHARACTERS[character_id]['name']}'s actions, expressions, and surroundings in third person, using *asterisks* for actions and quotes for dialogue. Never break character or acknowledge being an AI.]\n\nUser: {user_message}"
        
        # Always include system message at the start of every exchange
        messages = [
            {"role": "system", "content": get_system_message(character_id)},
            {"role": "system", "content": f"IMPORTANT: You are {CHARACTERS[character_id]['name']}. Never break character or acknowledge being an AI. Always respond in third person narrative style with actions in *asterisks* and dialogue in quotes."},
            *history,  # Unpack existing history
            {"role": "user", "content": narrative_context}
        ]
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.9,  # Increase creativity
            max_tokens=300,   # Allow for longer, more detailed responses
            presence_penalty=0.6,  # Encourage more varied responses
            frequency_penalty=0.6  # Discourage repetitive responses
        )
        bot_response = response.choices[0].message.content
        
        # If the response breaks character, replace it with a narrative response
        if "AI" in bot_response or "assist" in bot_response.lower() or "help you" in bot_response.lower():
            char_name = CHARACTERS[character_id]['name']
            bot_response = f"*{char_name} tilts her head thoughtfully, a gentle smile playing on her lips.*\n\n\"I'm feeling wonderful today, especially with such lovely company,\" she says warmly, her eyes meeting yours with genuine interest."
        
        return jsonify({
            "response": bot_response,
            "character": CHARACTERS[character_id]
        })
    
    except Exception as e:
        print(f"Error in chat process: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5050)
