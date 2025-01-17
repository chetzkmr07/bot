import streamlit as st
import google.generativeai as genai
import os
import base64
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
import json

# Load API key from Streamlit secrets
api_key = st.secrets["api_key"]
genai.configure(api_key=api_key)

# Firebase initialization using credentials from secrets.toml
try:
    if not firebase_admin._apps:
        firebase_credentials = {
            "type": st.secrets["firebase"]["type"],
            "project_id": st.secrets["firebase"]["project_id"],
            "private_key_id": st.secrets["firebase"]["private_key_id"],
            "private_key": st.secrets["firebase"]["private_key"].replace("\\n", "\n"),  # Handle newline in private_key
            "client_email": st.secrets["firebase"]["client_email"],
            "client_id": st.secrets["firebase"]["client_id"],
            "auth_uri": st.secrets["firebase"]["auth_uri"],
            "token_uri": st.secrets["firebase"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
            "universe_domain": st.secrets["firebase"]["universe_domain"]
        }
        cred = credentials.Certificate(firebase_credentials)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    st.error(f"Error initializing Firebase: {e}")

# Function to encode images in Base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Encode images
ai_icon_base64 = get_base64_image("assets/ai_icon.png")
user_icon_base64 = get_base64_image("assets/user_icon.png")

# Load and apply CSS
css_file = os.path.join(os.getcwd(), 'assets', 'chatbot_style.css')
with open(css_file) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Render chat
chat_placeholder = st.empty()

# Initialize session state if not already present
if "history" not in st.session_state:
    st.session_state.history = [{"origin": "ai", "message": "Hi there! Ask me anything about Chethan or Data science?"}]
    # Generate a unique chat ID for the session
    st.session_state.chat_id = str(uuid.uuid4())

# Function to render chat history
def render_chat():
    html_content = ""
    for chat in st.session_state.history:
        chat_icon = (
            f"data:image/png;base64,{ai_icon_base64}" if chat["origin"] == "ai" 
            else f"data:image/png;base64,{user_icon_base64}"
        )
        chat_bubble_class = "ai-bubble" if chat["origin"] == "ai" else "human-bubble"
        row_class = "" if chat["origin"] == "ai" else "row-reverse"
        html_content += f"""
<div class="chat-row {row_class}">
    <img class="chat-icon" src="{chat_icon}" width="32" height="32">
    <div class="chat-bubble {chat_bubble_class}">
        &#8203;{chat['message']}
    </div>
</div>
"""
    chat_placeholder.markdown(html_content, unsafe_allow_html=True)

render_chat()

# Function to check if it's a personal query
def is_personal_query(user_input):
    personal_keywords = []
    return any(keyword in user_input.lower() for keyword in personal_keywords)

# Handle user input
user_input = st.chat_input("Type your message...")
if user_input:
    st.session_state.history.append({"origin": "user", "message": user_input})
    render_chat()

    if is_personal_query(user_input):
        ai_response = "Sorry, I cannot answer personal queries."
    else:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        prompt = (
            """You are an AI Created by chethan on 14th jan 2025, 
            You are answering questions on chethan's behalf, random users will ask you questions.
            if user asks about me, tell them mainly about my professional details
              Please only answer questions related to chethan and Data Science.
            ..."""  # (Use your full prompt here)
        )
        response = model.generate_content(prompt + "\nUser: " + user_input)
        ai_response = response.candidates[0].content.parts[0].text.strip()

    # Append AI response to history and render chat
    st.session_state.history.append({"origin": "ai", "message": ai_response})
    render_chat()

    # Save chat to Firebase
    def save_chat_to_firestore(chat_history):
        try:
            chat_collection = db.collection("chat_logs")
            doc_ref = chat_collection.document(st.session_state.chat_id)  # Use the same chat_id for all interactions
            doc_ref.set({
                "chat_history": chat_history,
                "timestamp": firestore.SERVER_TIMESTAMP
            })
        except Exception as e:
            st.error(f"Error saving chat to Firestore: {e}")

    # Call the function to save chat history after each AI response
    save_chat_to_firestore(st.session_state.history)

# Function to save chat history to a local file (optional)
def save_history_to_file():
    file_path = "chat_history.json"
    with open(file_path, 'w') as f:
        json.dump(st.session_state.history, f)

# Call save_history_to_file after updating the history (optional for local storage)
save_history_to_file()
