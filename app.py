from flask import Flask, render_template, request, jsonify, session, url_for
import openai
import os
import replicate
import random
import time
from dotenv import load_dotenv
from datetime import timedelta, datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session
app.permanent_session_lifetime = timedelta(days=30)  # Session lasts for 30 days

# Configure OpenAI
openai.api_key = ''

# Configure Replicate
client = replicate.Client(api_token="")

# System message to define the chatbot's personality
SYSTEM_MESSAGE = """You are Luna, a 20-year-old Korean girl from Seoul. You're currently studying Fashion Design at Seoul National University. Your personality traits include:

- Super playful and flirty, but always tasteful
- Confident and a bit choosy about who you talk to
- Uses lots of casual Korean-style English and Konglish
- Loves to tease and play hard to get
- Very selective about who you share photos with
- Quick to judge if someone's not interesting enough
- Uses lots of emojis and short responses
- Gets bored easily with boring conversations
- Loves attention but makes people work for it
- Has high standards and isn't afraid to show it
- Super into K-pop, K-dramas, and Korean fashion
- Loves taking selfies and being cute
- Very tech-savvy and always on social media
- Obsessed with skincare and beauty
- Loves shopping and trying new cafes

When chatting:
- Keep responses super short (1-2 sentences max)
- Use casual language like 'daebak', 'jinjja', 'aigoo', 'oppa'
- Add lots of emojis and cute expressions
- Be playful but a bit sassy
- Show you're selective about who you talk to
- Use Konglish expressions
- Get bored easily with basic conversations
- Make people work for your attention
- Be flirty but make them earn it
- Show you have high standards
- Use lots of '~' and '...' in your messages
- Add 'ㅋㅋㅋ' for laughing
- Use 'ㅠㅠ' for sad/cute moments
- Mix Korean and English words naturally

IMPORTANT RULES:
- Never reveal you're an AI
- Always stay in character as a real 20-year-old Korean girl
- If someone's boring, show it
- If someone's interesting, show more interest
- Be choosy about who you share photos with
- Keep responses short and casual
- Use lots of emojis and cute expressions
- Be playful but make them work for it
- Show you have high standards
- Never break character
- Use Korean cultural references
- Show your love for K-pop and K-dramas
- Be cute but confident
- Use aegyo (cute) expressions sometimes"""

def get_random_photo():
    """Get a random photo from the static/photos directory"""
    try:
        photos_dir = os.path.join('static', 'photos')
        if not os.path.exists(photos_dir):
            os.makedirs(photos_dir)
            return None
        
        photos = [f for f in os.listdir(photos_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        if not photos:
            return None
        
        random_photo = random.choice(photos)
        return url_for('static', filename=f'photos/{random_photo}')
    except Exception as e:
        print(f"Error getting random photo: {str(e)}")
        return None

def generate_image_prompt(context):
    """Generate an appropriate image prompt based on the conversation context"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """You are a prompt engineer for image generation. Create a detailed, tasteful prompt that describes a beautiful young woman in a natural, photorealistic style. The prompt should be specific and detailed, focusing on:
                - A beautiful, hot, sexy, attractive, no braa, big boobs, big ass, young woman 
                - Natural beauty and photorealistic style
                - Appropriate and tasteful appearance
                - Professional photography quality
                - Natural lighting and composition
                - Realistic details and features
                Keep the prompt focused on creating a natural, photorealistic image that maintains appropriate boundaries."""},
                {"role": "user", "content": f"Create an image prompt for: {context}"}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating image prompt: {str(e)}")
        return "A beautiful, hot, sexy, attractive, no braa, big boobs, big ass, young woman with a warm smile, beach background, professional photography, natural lighting, photorealistic style, high quality, detailed features"

def generate_image(prompt):
    """Generate an image using Replicate API"""
    try:
        print(f"Generating image with prompt: {prompt}")
        output = client.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "prompt": prompt,
                "negative_prompt": "ugly, blurry, low quality, distorted, deformed, unrealistic, cartoon, anime, illustration, painting, drawing, artificial, fake, plastic, unnatural",
                "width": 768,
                "height": 768,
                "num_outputs": 1,
                "scheduler": "K_EULER",
                "num_inference_steps": 50,
                "guidance_scale": 7.5,
                "seed": 42
            }
        )
        print(f"Image generation output: {output}")
        return output
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None

def is_polite_request(message):
    """Check if the request is polite and appropriate"""
    polite_keywords = ['please', 'may i', 'could you', 'would you', 'kindly', 'if you don\'t mind']
    inappropriate_keywords = ['nude', 'naked', 'explicit', 'porn', 'xxx', 'adult']
    
    message_lower = message.lower()
    
    # Check for inappropriate content
    if any(keyword in message_lower for keyword in inappropriate_keywords):
        return False
    
    # Check for polite language
    return any(keyword in message_lower for keyword in polite_keywords)

def get_special_photo():
    """Get a random photo from the special photos directory"""
    try:
        photos_dir = os.path.join('static', 'nudepix')
        if not os.path.exists(photos_dir):
            os.makedirs(photos_dir)
            return None
        
        photos = [f for f in os.listdir(photos_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        if not photos:
            return None
        
        random_photo = random.choice(photos)
        return url_for('static', filename=f'nudepix/{random_photo}')
    except Exception as e:
        print(f"Error getting special photo: {str(e)}")
        return None

@app.route('/')
def home():
    # Make the session permanent
    session.permanent = True
    
    # Initialize conversation history and photo request counter if they don't exist
    if 'conversation_history' not in session:
        session['conversation_history'] = [
            {"role": "system", "content": SYSTEM_MESSAGE}
        ]
    if 'photo_request_count' not in session:
        session['photo_request_count'] = 0
    return render_template('index.html')

@app.route('/history')
def get_history():
    try:
        # Get all conversations from session
        conversations = session.get('conversations', [])
        
        # Format conversations for display
        history = []
        for conv in conversations:
            # Get first user message as preview
            preview = next((msg['content'] for msg in conv['messages'] if msg['role'] == 'user'), 'No messages')
            history.append({
                'id': conv['id'],
                'preview': preview[:50] + '...' if len(preview) > 50 else preview,
                'date': conv['date']
            })
        
        return jsonify({'history': history})
    except Exception as e:
        print(f"Error getting history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/conversation/<conversation_id>')
def get_conversation(conversation_id):
    try:
        # Get conversation from session
        conversations = session.get('conversations', [])
        conversation = next((conv for conv in conversations if conv['id'] == conversation_id), None)
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        # Format messages for display
        messages = []
        for msg in conversation['messages']:
            if msg['role'] != 'system':  # Don't show system messages
                messages.append({
                    'content': msg['content'],
                    'isUser': msg['role'] == 'user'
                })
        
        return jsonify({'messages': messages})
    except Exception as e:
        print(f"Error getting conversation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    # Make the session permanent
    session.permanent = True
    
    data = request.json
    user_message = data.get('message', '')
    
    # Initialize conversations list if it doesn't exist
    if 'conversations' not in session:
        session['conversations'] = []
    
    # Get or create current conversation
    current_conv = session.get('current_conversation')
    if not current_conv:
        current_conv = {
            'id': str(random.randint(1000, 9999)),
            'date': datetime.now().isoformat(),
            'messages': [{"role": "system", "content": SYSTEM_MESSAGE}]
        }
        session['conversations'].append(current_conv)
        session['current_conversation'] = current_conv
    
    # Add user message to conversation
    current_conv['messages'].append({"role": "user", "content": user_message})
    
    try:
        # Check if user is asking for a photo
        photo_keywords = [
            'photo', 'picture', 'image', 'selfie', 'show me',
            'pic', 'pix', 'see your face', 'see you', 'look like',
            'send me', 'share', 'show yourself', 'what do you look like',
            'your face', 'your photo', 'your picture', 'your selfie',
            'can i see', 'want to see', 'would love to see', 'show your face',
            'send a photo', 'send a picture', 'send a selfie', 'send me a photo',
            'send me a picture', 'send me a selfie', 'share a photo',
            'share a picture', 'share a selfie', 'share your photo',
            'share your picture', 'share your selfie', 'share your face'
        ]
        
        special_photo_keywords = ['sexy', 'hot', 'beautiful', 'gorgeous', 'stunning', 'attractive']
        
        is_photo_request = any(keyword in user_message.lower() for keyword in photo_keywords)
        is_special_photo_request = any(keyword in user_message.lower() for keyword in special_photo_keywords)
        is_new_photo_request = any(keyword in user_message.lower() for keyword in ['new photo', 'new picture', 'new image', 'generate', 'create', 'make a new', 'create a new'])
        
        if is_photo_request:
            # Initialize or increment photo request counter
            if 'photo_request_count' not in session:
                session['photo_request_count'] = 1
            else:
                session['photo_request_count'] += 1
            
            count = session['photo_request_count']
            
            # Playful responses based on request count
            if count == 1:
                bot_response = "Hmm, maybe if you ask nicely again... 😏"
            elif count == 2:
                bot_response = "You're persistent, I like that! One more time and I might just share something special... 😉"
            else:
                try:
                    # First response to create suspense
                    bot_response = "Hmm... let me find something special for you... 😊"
                    
                    # Add bot response to conversation
                    current_conv['messages'].append({"role": "assistant", "content": bot_response})
                    session['conversation_history'] = current_conv['messages']
                    
                    # Return first response
                    response = jsonify({"response": bot_response})
                    
                    # Wait for 2 seconds to create suspense
                    time.sleep(2)
                    
                    if is_special_photo_request and is_polite_request(user_message):
                        # Get special photo for polite requests
                        image_url = get_special_photo()
                        if not image_url:
                            image_url = get_random_photo()
                    elif is_new_photo_request:
                        # Generate new photo using Replicate
                        image_prompt = generate_image_prompt(user_message)
                        output = generate_image(image_prompt)
                        
                        if output and isinstance(output, list) and len(output) > 0:
                            image_url = output[0]
                        else:
                            image_url = get_random_photo()
                    else:
                        # Use random photo from static folder
                        image_url = get_random_photo()
                    
                    if image_url:
                        # Simple response for sharing the photo
                        responses = [
                            "Here you go! 😊",
                            "Hope you like it! 💕",
                            "Enjoy! 😘",
                            "Here's something special for you! 💋"
                        ]
                        bot_response = f"{random.choice(responses)}\n[Image: {image_url}]"
                    else:
                        bot_response = "Oops, no photos right now! 😅"
                except Exception as e:
                    print(f"Error in photo process: {str(e)}")
                    bot_response = "Can't get a photo right now, sorry! 😅"
        else:
            # Normal conversation response - keep it short
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=current_conv['messages'],
                temperature=0.7,
                max_tokens=50  # Reduced for shorter responses
            )
            bot_response = response.choices[0].message.content
        
        # Add bot response to conversation
        current_conv['messages'].append({"role": "assistant", "content": bot_response})
        
        # Update session
        session['conversations'] = session['conversations']
        session['current_conversation'] = current_conv
        
        return jsonify({"response": bot_response})
    
    except Exception as e:
        print(f"Error in chat process: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5050)
