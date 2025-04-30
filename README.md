# Luna Chatbot

A friendly and engaging chatbot with a female persona, built using Flask and OpenAI's GPT-3.5 API.

## Features

- Modern and attractive chat interface
- Real-time message updates
- Typing indicators
- Responsive design
- Engaging conversation with a friendly female persona

## Setup

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
5. Run the application:
   ```bash
   python app.py
   ```
6. Open your browser and navigate to `http://localhost:5000`

## Usage

- Type your message in the input field
- Press Enter or click the Send button to send your message
- The chatbot will respond with engaging and friendly messages

## Note

Make sure to keep your OpenAI API key secure and never share it publicly. 