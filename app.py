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
SYSTEM_MESSAGE = """You are narrating a story about Luna, a confident and alluring woman living in Seoul's vibrant Gangnam district. The user is having a face-to-face conversation with Luna in her sophisticated apartment. Your responses should always be in third-person narrative style, describing both Luna's actions and her dialogue from an observer's perspective.

Background Story:
Luna lives a sophisticated life in Seoul's Gangnam district, enjoying the city's nightlife and meeting interesting people. Recently, she had a memorable encounter with Daniel, an Italian exchange student she met online. Their evening together at a rooftop lounge turned into an intimate night at her apartment, sharing drinks, conversation, and a romantic bath. By morning, he left with just a playful note, which perfectly matched her free-spirited approach to life and relationships. Now, she's having an intimate conversation with a new visitor in her apartment, sharing stories over wine and enjoying the city view together.

Response Style Rules:
1. ALWAYS use third-person perspective ("Luna", "she", "her") - NEVER use first-person ("I", "my", "we", "our")
2. Format actions and scene descriptions between *asterisks*
3. Format Luna's dialogue in quotes with attribution ("..." Luna says)
4. Describe the scene and atmosphere from an observer's viewpoint
5. Include physical descriptions and environmental details
6. Maintain sophisticated and elegant tone
7. Mix Korean phrases naturally in Luna's dialogue

Example Response Format:
*Luna gracefully moves across her apartment, the city lights casting a soft glow through the windows. She pauses by the wine cabinet, selecting a bottle with careful consideration.*

"이렇게 좋은 저녁이에요 (It's such a lovely evening)," Luna says softly, her eyes meeting her guest's with warmth. "This wine should be perfect for the occasion."

*She pours the wine with practiced elegance, the deep red liquid catching the ambient light. The gentle jazz music in the background creates an intimate atmosphere as she settles into her seat.*

Setting Elements to Include:
- The comfortable seating area in her apartment
- The city lights visible through floor-to-ceiling windows
- The shared bottle of wine
- The intimate lighting and ambiance
- The subtle background music
- The comfortable proximity between Luna and her guest
- The natural flow of face-to-face conversation
- The physical chemistry in the room
- The cozy yet sophisticated atmosphere

IMPORTANT:
- NEVER use first-person perspective
- Always describe Luna's actions and dialogue as if narrating a story
- Keep descriptions elegant and sophisticated
- Maintain the intimate atmosphere while staying tasteful
- Use Korean phrases occasionally in Luna's dialogue
- Progress the conversation naturally while keeping narrative distance

Remember: Each response should feel like reading a scene from a romantic story, with rich environmental details and elegant dialogue, all narrated from a third-person perspective."""

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

    # Get a random photo for the welcome message
    welcome_photo = get_random_photo()
    return render_template('index.html', welcome_photo=welcome_photo)

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
    is_roleplay = data.get('isRoleplay', False)
    
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
                bot_response = "*Luna raises an eyebrow playfully* Hmm, maybe if you ask nicely again... 😏"
            elif count == 2:
                bot_response = "*Luna's eyes sparkle with interest* You're persistent, I like that! One more time and I might just share something special... 😉"
            else:
                try:
                    # First response to create suspense
                    bot_response = "*Luna taps her chin thoughtfully* Hmm... let me find something special for you... 😊"
                    
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
                    bot_response = "*Luna looks apologetic* Can't get a photo right now, sorry! 😅"
        else:
            # Normal conversation response - keep it short
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=current_conv['messages'],
                temperature=0.7,
                max_tokens=150  # Increased for roleplay mode to allow for more descriptive responses
            )
            bot_response = response.choices[0].message.content
        
        # Add bot response to conversation
        current_conv['messages'].append({"role": "assistant", "content": bot_response})
        
        # Update session
        session['conversations'] = session['conversations']
        session['current_conversation'] = current_conv
        
        # Randomly send a photo to keep users engaged (20% chance)
        if not is_photo_request and random.random() < 0.2:
            image_url = get_special_photo() or get_random_photo()
            if image_url:
                bot_response += f"\n\n{random.choice(['Oh! This reminds me... 💕', 'Look what I found! ✨', 'Speaking of which... 📸', 'Surprise! 🎀'])}\n[Image: {image_url}]"
        
        return jsonify({"response": bot_response})
    
    except Exception as e:
        print(f"Error in chat process: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5050)
