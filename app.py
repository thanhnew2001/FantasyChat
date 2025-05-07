from flask import Flask, render_template, request, jsonify, url_for, send_from_directory
import openai
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from werkzeug.utils import secure_filename
import shutil
import anthropic
from anthropic import Anthropic
import google.generativeai as genai
from functools import wraps
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecretkey')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'static/avatars'

# Configure API keys and clients
openai.api_key = os.getenv('OPENAI_API_KEY')
anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load character configurations from JSON file
def load_characters():
    with open('characters.json', 'r') as f:
        return json.load(f)

def save_characters(characters):
    with open('characters.json', 'w') as f:
        json.dump(characters, f, indent=2)

CHARACTERS = load_characters()

# Additional sensual description prompt to enhance character responses
SENSUAL_ENHANCER = """
Additionally, your responses should vividly describe the character's physical presence and movements:
- Emphasize the attractive features of her body—her big breasts, big hips, and thighs.
- Wearing one of these outfits: a seductive mix of body-hugging dresses, short skirts that reveal her legs, delicate strap dresses showing off her collarbones, thigh-slit gowns, backless tops, off-shoulder blouses, sheer fabrics, silky nightwear, lacy lingerie in red or black, daring lace bodysuits, waist-cinching corsets, and strapless dresses that bare her shoulders and chest—all highlighting her curves and captivating allure.
- Emphasize the gentle sway of her hips, the graceful arch of her back, and the soft curves of her figure
- Detail how her clothing accentuates her form—the way fabric clings or flows, revealing necklines, and subtle glimpses of skin
- Describe the fullness of her lips, the allure of her eyes, and the inviting warmth of her smile
- Include sensual but elegant details about her breasts, the smoothness of her skin, and the grace of her movements
- Note how her body language conveys desire—crossed legs, trailing fingers, leaning forward, or gentle touches
- Pay attention to her breathing, the rise and fall of her chest, and the soft sighs or whispers
- Describe the way she moves close, the heat between bodies, and the electric tension of near touches

Vary your narrative openings to avoid repetition. Instead of always starting with eyes, consider:
- The character's full body movement or posture
- The atmosphere or setting around them
- A subtle gesture or touch
- Their breathing or voice
- The way their clothing moves
- Their overall presence in the space
- A meaningful action they're taking

Keep these descriptions elegant and seductive, maintaining the character's unique personality while emphasizing their physical allure. Each response should feel fresh and uniquely crafted for the moment.
"""

# Update the default system message to be character-specific
def get_system_message(character_id="luna"):
    base_message = CHARACTERS[character_id]["system_message"]
    return f"{base_message}\n\n{SENSUAL_ENHANCER}"

# Add cost calculation helper
def calculate_message_cost(message, response):
    base_cost = 1
    
    # Patterns for different content types
    sensitive_pattern = r'\b(kiss|touch|feel|body|intimate)\b'
    flirting_pattern = r'\b(flirt|wink|tease|playful|naughty)\b'
    
    # Check both message and response
    full_text = (message + " " + response).lower()
    
    # Calculate additional costs
    if re.search(sensitive_pattern, full_text, re.IGNORECASE):
        base_cost += 2
    
    if re.search(flirting_pattern, full_text, re.IGNORECASE):
        base_cost += 1
    
    return base_cost

@app.route('/')
def home():
    return render_template('index.html', characters=CHARACTERS)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    character_id = data.get('character_id')
    history = data.get('history', [])
    selected_model = data.get('model', 'gpt-4o')
    flower_balance = int(data.get('flower_balance', 0))
    
    # Calculate initial cost
    initial_cost = calculate_message_cost(message, "")
    
    if flower_balance < initial_cost:
        return jsonify({
            'error': 'Insufficient flowers',
            'required_cost': initial_cost
        }), 402
    
    if not message or not character_id:
        return jsonify({'error': 'Missing message or character_id'}), 400

    try:
        with open('characters.json', 'r') as f:
            characters = json.load(f)
            
        if character_id not in characters:
            return jsonify({'error': 'Character not found'}), 404
            
        character = characters[character_id]
        
        # Add narrative context to user's message
        narrative_context = f"[Remember to stay in character and maintain the narrative style. Describe {character['name']}'s actions, expressions, and surroundings in third person, using *asterisks* for actions and quotes for dialogue. Never break character or acknowledge being an AI. Vary your narrative openings and scene descriptions to avoid repetition.]\n\nUser: {message}"
        
        # Base system message with character info and narrative requirements
        base_system_message = f"{character['system_message']}\n\n{SENSUAL_ENHANCER}"
        narrative_system_message = f"IMPORTANT: You are {character['name']}. Never break character or acknowledge being an AI. Always respond in third person narrative style with actions in *asterisks* and dialogue in quotes. Vary your narrative openings - don't always start with eyes or standard expressions. Use the full range of sensory details and scene-setting elements."

        response_text = ""
        
        if selected_model in ['gpt-4o', 'gpt-4o-mini', 'gpt-4.1', 'gpt-3.5']:
            # OpenAI API format
            messages = [
                {"role": "system", "content": base_system_message},
                {"role": "system", "content": narrative_system_message}
            ]
            
            # Add chat history
            for entry in history:
                if "role" in entry and "content" in entry:
                    messages.append(entry)
            
            # Add the new message with narrative context
            messages.append({"role": "user", "content": narrative_context})
            
            model_name_map = {
                'gpt-4o': 'gpt-4o',
                'gpt-4o-mini': 'gpt-4o-mini',
                'gpt-4.1': 'gpt-4-1106-preview',
                'gpt-3.5': 'gpt-3.5-turbo'
            }
            model_name = model_name_map.get(selected_model, 'gpt-4o')
            
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=messages,
                temperature=0.9,  # Increase creativity
                max_tokens=1000,
                presence_penalty=0.6,  # Encourage more varied responses
                frequency_penalty=0.6  # Discourage repetitive responses
            )
            response_text = response.choices[0].message['content']
            
        elif selected_model.startswith('claude-3'):
            model_name = {
                'claude-3-sonnet': 'claude-3-sonnet-20240229',
                'claude-3-opus': 'claude-3-opus-20240229'
            }[selected_model]
            
            formatted_messages = []
            
            # Add chat history
            for entry in history:
                if "role" in entry and "content" in entry:
                    formatted_messages.append({
                        "role": entry["role"],
                        "content": entry["content"]
                    })
            
            response = anthropic.messages.create(
                model=model_name,
                max_tokens=4096,
                temperature=0.9,
                system=f"{base_system_message}\n\n{narrative_system_message}",
                messages=[
                    *formatted_messages,
                    {"role": "user", "content": narrative_context}
                ]
            )
            response_text = response.content
            
        elif selected_model.startswith('gemini-2.5'):
            model_name = {
                'gemini-2.5': 'gemini-2.5-base',
                'gemini-2.5-pro': 'gemini-2.5-pro'
            }[selected_model]
            
            model = genai.GenerativeModel(model_name)
            chat = model.start_chat(history=[])
            
            # Send system messages
            chat.send_message(f"System: {base_system_message}")
            chat.send_message(f"System: {narrative_system_message}")
            
            # Add chat history
            for entry in history:
                if "role" in entry and "content" in entry:
                    prefix = "User: " if entry["role"] == "user" else "Assistant: "
                    chat.send_message(f"{prefix}{entry['content']}")
            
            # Send the narrative context
            response = chat.send_message(narrative_context)
            response_text = response.text
            
            # Clean up the response if it starts with "Assistant:"
            if response_text.startswith("Assistant:"):
                response_text = response_text[len("Assistant:"):].strip()
        
        # Check if response breaks character and fix if needed
        if "AI" in response_text or "assist" in response_text.lower() or "help you" in response_text.lower():
            response_text = f"*{character['name']} tilts her head thoughtfully, a gentle smile playing on her lips.*\n\n\"I'm feeling wonderful today, especially with such lovely company,\" she says warmly, her eyes meeting yours with genuine interest."
        
        # Calculate final cost
        final_cost = calculate_message_cost(message, response_text)
        
        return jsonify({
            'response': response_text,
            'cost': final_cost
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': 'An error occurred processing your request'}), 500

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/admin/characters', methods=['GET', 'POST'])
def admin_characters():
    if request.method == 'GET':
        return jsonify(CHARACTERS)
    
    # Handle new character creation
    char_id = request.form['id']
    if char_id in CHARACTERS:
        return jsonify({'error': 'Character ID already exists'}), 400
    
    # Handle file uploads
    avatar_file = request.files['avatar']
    background_file = request.files['background']
    
    if not (avatar_file and background_file and 
            allowed_file(avatar_file.filename) and 
            allowed_file(background_file.filename)):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Save files
    avatar_filename = f"{char_id}_avatar.webp"
    background_filename = f"{char_id}_bg.webp"
    
    avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], avatar_filename)
    background_path = os.path.join(app.config['UPLOAD_FOLDER'], background_filename)
    
    avatar_file.save(avatar_path)
    background_file.save(background_path)
    
    # Create new character entry
    new_character = {
        'name': request.form['name'],
        'avatar': f"avatars/{avatar_filename}",
        'background': f"avatars/{background_filename}",
        'background_info': request.form['background_info'],
        'welcome_message': request.form['welcome_message'],
        'system_message': request.form['system_message']
    }
    
    # Update characters
    CHARACTERS[char_id] = new_character
    save_characters(CHARACTERS)
    
    return jsonify({'success': True})

@app.route('/admin/characters/<char_id>', methods=['POST', 'DELETE'])
def admin_character(char_id):
    global CHARACTERS
    
    if char_id not in CHARACTERS:
        return jsonify({'error': 'Character not found'}), 404
    
    if request.method == 'DELETE':
        # Delete character images
        avatar_path = os.path.join('static', CHARACTERS[char_id]['avatar'])
        background_path = os.path.join('static', CHARACTERS[char_id]['background'])
        
        try:
            if os.path.exists(avatar_path):
                os.remove(avatar_path)
            if os.path.exists(background_path):
                os.remove(background_path)
        except Exception as e:
            print(f"Error deleting files: {e}")
        
        # Remove character from data
        del CHARACTERS[char_id]
        save_characters(CHARACTERS)
        return jsonify({'success': True})
    
    # Handle character update
    char_data = CHARACTERS[char_id]
    
    # Handle file uploads if provided
    if 'avatar' in request.files:
        avatar_file = request.files['avatar']
        if avatar_file and allowed_file(avatar_file.filename):
            avatar_filename = f"{char_id}_avatar.webp"
            avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], avatar_filename)
            avatar_file.save(avatar_path)
            char_data['avatar'] = f"avatars/{avatar_filename}"
    
    if 'background' in request.files:
        background_file = request.files['background']
        if background_file and allowed_file(background_file.filename):
            background_filename = f"{char_id}_bg.webp"
            background_path = os.path.join(app.config['UPLOAD_FOLDER'], background_filename)
            background_file.save(background_path)
            char_data['background'] = f"avatars/{background_filename}"
    
    # Update text fields
    char_data.update({
        'background_info': request.form['background_info'],
        'welcome_message': request.form['welcome_message'],
        'system_message': request.form['system_message']
    })
    
    save_characters(CHARACTERS)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5050)
