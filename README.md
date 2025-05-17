# Gemini Chatbot

A local chatbot powered by Google's Gemini API that can answer questions and generate images.

## Features

- Text-based conversation with Gemini model
- Image generation based on text prompts
- Maintains conversation history for context
- Saves generated images to local directory
- GUI version with image display

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Set up your Gemini API key:

   a. Copy the example environment file:
   ```bash
   cp .env-example .env
   ```
   
   b. Edit the `.env` file and add your API key:
   ```
   GOOGLE_API_KEY="your-api-key-here"
   ```

3. Run the chatbot:

   a. Command-line version:
   ```bash
   python gemini_chatbot.py
   ```
   
   b. GUI version (recommended):
   ```bash
   python gemini_chatbot_gui.py
   ```

4. Optional environment:

   a. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

   b. run the virtual environment
   ```bash
   venv\Scripts\activate
   ```

## Usage

### Command Line Interface
- Type your messages after the "You:" prompt
- For image generation, include keywords like "draw", "create", "generate image", "picture", etc.
- Images will be saved in the "generated_images" directory
- Type 'exit' or 'quit' to end the conversation

### GUI Interface
- Type your message in the input box and press Enter or click Send
- Generated images will appear directly in the interface
- Images are also saved to the "generated_images" directory for later use

## Notes

- This chatbot uses the "gemini-2.0-flash-preview-image-generation" model
- Internet connection is required to communicate with the Gemini API
- API usage may be subject to rate limits or costs depending on your Google API plan 
