import base64
import mimetypes
import os
import threading
import tkinter as tk
from tkinter import scrolledtext, Entry, Button, Frame, Label, END
from PIL import Image, ImageTk
import io
from google import genai
from google.genai import types
import time
import re
from dotenv import load_dotenv

class GeminiChatbotGUI:
    def __init__(self, root):
        # Load environment variables from .env file
        load_dotenv()
        
        # Initialize the API client
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Please set the GOOGLE_API_KEY in your .env file")
        
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash-preview-image-generation"  # Model that supports text and image generation
        self.conversation_history = []
        
        # Create output directory for images
        self.image_dir = "generated_images"
        os.makedirs(self.image_dir, exist_ok=True)
        
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
        
        # Keep track of displayed images
        self.displayed_images = []
        
        # Colors and styles
        self.bg_color = "#f5f5f7"
        self.header_color = "#4285F4"  # Google Blue
        self.chat_bg = "#ffffff"
        self.input_bg = "#ffffff"
        self.user_color = "#1a73e8"  # User message color
        self.bot_color = "#ea4335"    # Gemini message color
        self.text_color = "#202124"
        self.status_bg = "#f5f5f7"
        
        # Setup GUI
        self.root = root
        self.root.title("Gemini Chatbot")
        self.root.geometry("800x700")
        self.root.configure(bg=self.bg_color)
        
        # Header with logo
        self.header_frame = Frame(root, bg=self.header_color, height=60)
        self.header_frame.pack(fill=tk.X)
        
        # Try to load logo
        self.logo_img = None
        try:
            # Look for logo in the current directory
            for logo_file in ['logo.png', 'gemini_logo.png', 'chatbot_logo.png']:
                if os.path.exists(logo_file):
                    img = Image.open(logo_file)
                    img = img.resize((40, 40), Image.LANCZOS)
                    self.logo_img = ImageTk.PhotoImage(img)
                    break
                    
            # If no logo found, create a placeholder
            if not self.logo_img:
                self.logo_label = Label(self.header_frame, text="G", bg=self.header_color, 
                                        fg="white", font=("Arial", 24, "bold"))
                self.logo_label.pack(side=tk.LEFT, padx=15)
            else:
                self.logo_label = Label(self.header_frame, image=self.logo_img, bg=self.header_color)
                self.logo_label.pack(side=tk.LEFT, padx=15)
                
        except Exception as e:
            print(f"Error loading logo: {e}")
            self.logo_label = Label(self.header_frame, text="G", bg=self.header_color, 
                                    fg="white", font=("Arial", 24, "bold"))
            self.logo_label.pack(side=tk.LEFT, padx=15)
            
        # Title in header
        self.title_label = Label(self.header_frame, text="Gemini Chatbot", 
                            bg=self.header_color, fg="white", font=("Arial", 16, "bold"))
        self.title_label.pack(side=tk.LEFT, padx=10)
        
        # Main content area
        self.content_frame = Frame(root, bg=self.bg_color)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Chat area with rounded corners effect
        self.chat_container = Frame(self.content_frame, bg=self.bg_color, padx=2, pady=2)
        self.chat_container.pack(fill=tk.BOTH, expand=True)
        
        # Custom chat display with text and images
        self.chat_display = tk.Text(self.chat_container, wrap=tk.WORD, 
                                   font=("Segoe UI", 11), 
                                   padx=15, pady=15,
                                   bg=self.chat_bg,
                                   fg=self.text_color,
                                   relief=tk.FLAT,
                                   highlightthickness=1,
                                   highlightbackground="#e0e0e0")
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # Add scrollbar to chat display
        self.scrollbar = tk.Scrollbar(self.chat_display)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_display.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.chat_display.yview)
        
        # Input area at the bottom of window
        self.input_frame = Frame(root, bg=self.bg_color, pady=10)
        self.input_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Input with rounded corners effect
        self.user_input = Entry(self.input_frame, 
                               font=("Segoe UI", 12),
                               bg=self.input_bg,
                               relief=tk.FLAT,
                               highlightthickness=1,
                               highlightbackground="#e0e0e0",
                               insertbackground=self.text_color)
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=8)
        self.user_input.bind("<Return>", self.send_message_event)
        
        # Send button
        self.send_button = Button(self.input_frame, text="Send", 
                                 bg=self.header_color, fg="white",
                                 activebackground="#3367d6", activeforeground="white",
                                 relief=tk.FLAT, font=("Segoe UI", 10, "bold"),
                                 padx=15, pady=8, cursor="hand2",
                                 command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)
        
        # Status bar
        self.status_bar = Label(root, text="Ready", bd=1, relief=tk.FLAT, 
                               bg=self.status_bg, fg="#666666", 
                               anchor=tk.W, padx=15, pady=5,
                               font=("Segoe UI", 9))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Add initial greeting
        self.add_message("Gemini", "I'm a helpful assistant powered by Google's Gemini model. I can answer questions and generate images based on your requests. How can I help you today?")
        
        # Set focus to input box
        self.user_input.focus()

    def add_message(self, sender, message):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add the sender tag
        if sender == "You":
            self.chat_display.insert(tk.END, f"{sender}: ", "user_tag")
            self.chat_display.tag_configure("user_tag", foreground=self.user_color, font=("Segoe UI", 11, "bold"))
        else:
            self.chat_display.insert(tk.END, f"{sender}: ", "bot_tag")
            self.chat_display.tag_configure("bot_tag", foreground=self.bot_color, font=("Segoe UI", 11, "bold"))
        
        # Add the message content
        self.chat_display.insert(tk.END, f"{message}\n\n")
        
        # Scroll to the end
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def add_image_to_chat(self, image_path):
        """Add an image to the chat display"""
        try:
            # Open and resize the image
            img = Image.open(image_path)
            
            # Resize the image to fit in the chat
            max_width = 400  # Maximum width in the chat
            width, height = img.size
            
            if width > max_width:
                ratio = max_width / width
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Convert to PhotoImage and keep a reference
            photo = ImageTk.PhotoImage(img)
            self.displayed_images.append(photo)  # Keep reference to avoid garbage collection
            
            # Add the image to the chat
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, "\n")
            self.chat_display.image_create(tk.END, image=photo)
            self.chat_display.insert(tk.END, f"\n\n")
            self.chat_display.see(tk.END)
            self.chat_display.config(state=tk.DISABLED)
            
            return True
        except Exception as e:
            print(f"Error displaying image: {e}")
            return False

    def save_image(self, data, mime_type):
        """Save binary image data to a file and display it in chat"""
        timestamp = int(time.time())
        file_extension = mimetypes.guess_extension(mime_type) or ".png"
        file_name = f"{self.image_dir}/image_{timestamp}{file_extension}"
        
        with open(file_name, "wb") as f:
            f.write(data)
        
        # Add the image to the chat
        self.add_image_to_chat(file_name)
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
                    # Update the displayed text in real-time
                    self.chat_display.config(state=tk.NORMAL)
                    self.chat_display.insert(tk.END, part.text)
                    self.chat_display.see(tk.END)
                    self.chat_display.config(state=tk.DISABLED)
                    full_text += part.text
                
                elif hasattr(part, 'inline_data') and part.inline_data:
                    inline_data = part.inline_data
                    file_path = self.save_image(inline_data.data, inline_data.mime_type)
        
        # Add empty line after response
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Add model response to history
        self.conversation_history.append(
            types.Content(
                role="model",
                parts=[types.Part(text=full_text)],
            )
        )
        
        # Re-enable the input and button
        self.user_input.config(state=tk.NORMAL)
        self.send_button.config(state=tk.NORMAL)
        self.status_bar.config(text="Ready")
        
        # Set focus back to the input
        self.user_input.focus()

    def send_message_event(self, event):
        """Handle the enter key event"""
        self.send_message()

    def send_message(self):
        """Send a message to the Gemini model and get a response"""
        message = self.user_input.get().strip()
        if not message:
            return
            
        # Clear the input field
        self.user_input.delete(0, tk.END)
        
        # Disable input while processing
        self.user_input.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
        self.status_bar.config(text="Gemini is thinking...")
        
        # Display user message
        self.add_message("You", message)
        
        # Check if this is an image generation request
        is_image_request = bool(re.search(r'draw|create|generate.*image|picture|photo', message.lower()))
        
        # Add user message to history
        self.conversation_history.append(
            types.Content(
                role="user",
                parts=[types.Part(text=message)],
            )
        )
        
        # Update status
        if is_image_request:
            self.status_bar.config(text="Generating image...")
        
        # Display the start of Gemini's response
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "Gemini: ", "bot_tag")
        self.chat_display.tag_configure("bot_tag", foreground=self.bot_color, font=("Segoe UI", 11, "bold"))
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Process in a separate thread to keep the UI responsive
        threading.Thread(target=self.process_in_background, args=(message,), daemon=True).start()
    
    def process_in_background(self, message):
        """Process the message in a background thread to keep UI responsive"""
        try:
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
            
            # Process the response
            self.process_response(response)
            
        except Exception as e:
            # Handle errors
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, f"Error: {str(e)}\n\n")
            self.chat_display.see(tk.END)
            self.chat_display.config(state=tk.DISABLED)
            
            self.user_input.config(state=tk.NORMAL)
            self.send_button.config(state=tk.NORMAL)
            self.status_bar.config(text="Error occurred")
            self.user_input.focus()

def main():
    root = tk.Tk()
    app = GeminiChatbotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 