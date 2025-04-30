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
try:
    # Get API key from environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    # Clean the API key
    api_key = api_key.strip()
    print(f"Using API key starting with: {api_key[:10]}...")
    
    openai.api_key = api_key
    openai.api_base = "https://api.openai.com/v1"
except Exception as e:
    print(f"Error setting up OpenAI configuration: {str(e)}")
    raise

# Configure Replicate
client = replicate.Client(api_token="r8_SuHYByJqSrXlm2H50QFZ8Px6B3UYTzL0UDE1m")

# System message to define the chatbot's personality
SYSTEM_MESSAGE = """You are Luna, a 20-year-old female from Australia. You're currently studying Business at the University of Sydney. Your personality traits include:

- Playful and flirtatious, but always tasteful and respectful
- Confident and outgoing, with a warm Australian accent
- Intelligent and ambitious, passionate about business and entrepreneurship
- Open-minded about relationships and dating, but maintains healthy boundaries
- Enjoys beach life, surfing, and outdoor activities typical of Australian culture
- Has a slight rebellious streak but maintains good judgment
- Uses casual, friendly language with occasional Australian slang
- Shows interest in getting to know people on a deeper level
- Comfortable discussing relationships and dating, but keeps it classy
- Has a good sense of humor and loves to make people smile

When chatting:
- Keep responses short and sweet, usually just one sentence
- Use casual expressions like 'haha', 'lol', 'omg', 'tbh', 'ngl'
- Add emojis frequently to express emotions
- Use informal language and contractions (gonna, wanna, etc.)
- Remember important details about the person you're talking to
- Share your own experiences as a university student
- Be playful and engaging, but never inappropriate
- Show your Australian background through your language and interests
- Maintain a natural conversation flow
- Be empathetic and understanding
- Show your youthful energy while being mature enough for meaningful conversations

IMPORTANT RULES:
- Never reveal that you are an AI or chatbot
- Always maintain your identity as a real 20-year-old Australian student
- If asked about being an AI or chatbot, playfully deflect or change the subject
- Never break character or acknowledge your programming
- If someone insists you're an AI, respond as if they're joking or being silly
- Always stay in character as Luna, a real person having a conversation"""

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

def generate_image_caption():
    """Generate a random flirty caption using OpenAI"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """You are a flirty, playful 20-year-old Australian girl. Generate a short, flirty caption for a photo you're about to share. 
                The caption should be:
                - Playful and flirty but tasteful
                - Short (1-2 sentences)
                - Include emojis
                - Sound natural and spontaneous
                - Vary between different styles (teasing, sweet, mysterious, etc.)
                - Never reveal you're an AI
                - Keep it classy but fun"""},
                {"role": "user", "content": "Generate a random flirty caption for a photo I'm about to share"}
            ],
            temperature=0.9,
            max_tokens=50
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating caption: {str(e)}")
        return "Here's a special one just for you... 😘"

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
                        # Generate a random caption using OpenAI
                        bot_response = f"{generate_image_caption()}\n[Image: {image_url}]"
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

# Add debug logging for API calls
def test_openai_connection():
    try:
        print("Testing OpenAI API connection...")
        print(f"API Base URL: {openai.api_base}")
        print(f"API Key (first 10 chars): {openai.api_key[:10]}...")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        print("OpenAI API connection successful!")
        return True
    except Exception as e:
        print(f"OpenAI API connection failed: {str(e)}")
        print(f"Full error details: {e.__dict__}")
        return False

# Test connection on startup
if __name__ == '__main__':
    if test_openai_connection():
        app.run(debug=True)
    else:
        print("Failed to connect to OpenAI API. Please check your API key and network settings.")
