# FantasyChat

A Flask-based chatbot application featuring Luna, a friendly AI companion.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/FantasyChat.git
cd FantasyChat
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your API keys:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     REPLICATE_API_TOKEN=your_replicate_api_token_here
     ```

5. Run the application:
```bash
python app.py
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `REPLICATE_API_TOKEN`: Your Replicate API token
- `FLASK_SECRET_KEY`: (Optional) Flask secret key for session management

## Security Notes

- Never commit your `.env` file to version control
- Keep your API keys secure and don't share them
- The `.env` file is already in `.gitignore`

## Features

- Interactive chat interface
- Image generation capabilities
- Conversation history
- Responsive design

## License

MIT License 