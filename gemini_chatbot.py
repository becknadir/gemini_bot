import base64
import mimetypes
import os
from google import genai
from google.genai import types
import time
import re
from dotenv import load_dotenv

class GeminiChatbot:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Initialize the API client
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Please set the GOOGLE_API_KEY in your .env file")
        
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash-preview-image-generation"  # Model that supports text and image generation
        self.conversation_history = []
        
        # Add system message to set behavior
        self.conversation_history.append(
            types.Content(
                role="user",
                parts=[types.Part(text="You are a helpful assistant that can answer questions and generate images.")],
            )
        )
        self.conversation_history.append(
            types.Content(
                role="model",
                parts=[types.Part(text="I'm a helpful assistant powered by Google's Gemini model. I can answer questions and generate images based on your requests. How can I help you today?")],
            )
        )
        
        # Create output directory for images
        self.image_dir = "generated_images"
        os.makedirs(self.image_dir, exist_ok=True)

    def save_image(self, data, mime_type):
        """Save binary image data to a file"""
        timestamp = int(time.time())
        file_extension = mimetypes.guess_extension(mime_type) or ".png"
        file_name = f"{self.image_dir}/image_{timestamp}{file_extension}"
        
        with open(file_name, "wb") as f:
            f.write(data)
        
        print(f"Image saved to: {file_name}")
        return file_name

    def process_response(self, response_chunks):
        """Process the streaming response from Gemini"""
        full_text = ""
        
        for chunk in response_chunks:
            if (chunk.candidates is None or 
                chunk.candidates[0].content is None or 
                chunk.candidates[0].content.parts is None):
                continue
                
            for part in chunk.candidates[0].content.parts:
                if hasattr(part, 'text') and part.text:
                    print(part.text, end="", flush=True)
                    full_text += part.text
                
                elif hasattr(part, 'inline_data') and part.inline_data:
                    inline_data = part.inline_data
                    file_path = self.save_image(inline_data.data, inline_data.mime_type)
                    print(f"\n[Image generated: {file_path}]")
        
        print()  # New line after response
        
        # Add model response to history
        self.conversation_history.append(
            types.Content(
                role="model",
                parts=[types.Part(text=full_text)],
            )
        )

    def send_message(self, message):
        """Send a message to the Gemini model and get a response"""
        # Check if this is an image generation request
        is_image_request = bool(re.search(r'draw|create|generate.*image|picture|photo', message.lower()))
        
        # Add user message to history
        self.conversation_history.append(
            types.Content(
                role="user",
                parts=[types.Part(text=message)],
            )
        )
        
        # Configure response to include images
        # This model requires both IMAGE and TEXT modalities always
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
            response_mime_type="text/plain",
        )
        
        # Get response from model
        response = self.client.models.generate_content_stream(
            model=self.model,
            contents=self.conversation_history,
            config=generate_content_config,
        )
        
        self.process_response(response)

def main():
    print("Initializing Gemini Chatbot...")
    chatbot = GeminiChatbot()
    print("Chatbot ready! Type 'exit' to quit.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        print("\nGemini: ", end="")
        chatbot.send_message(user_input)

if __name__ == "__main__":
    main() 