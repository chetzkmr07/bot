import streamlit as st
import google.generativeai as genai
import os
import base64
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
import json
import requests

# ---------------------------------------------------------------
# 1. Load Environment Variables (Render uses env vars)
# ---------------------------------------------------------------

api_key = os.getenv("API_KEY")                 # Gemini API Key
firebase_json = os.getenv("FIREBASE_CREDS")    # Firebase JSON as string
details_url = os.getenv("DETAILS_URL")         # Google Drive CSV/Text link

# Configure Gemini API
genai.configure(api_key=api_key)

# ---------------------------------------------------------------
# 2. Firebase Initialization
# ---------------------------------------------------------------

try:
    if not firebase_admin._apps:

        # Convert JSON string to Python dict
        cred_dict = json.loads(firebase_json)

        # Initialize Firebase app
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)

    db = firestore.client()

except Exception as e:
    st.error(f"Error initializing Firebase: {e}")

# ---------------------------------------------------------------
# 3. Load Icons (Base64)
# ---------------------------------------------------------------

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

ai_icon_base64 = get_base64_image("assets/ai_icon.png")
user_icon_base64 = get_base64_image("assets/user_icon.png")

# ---------------------------------------------------------------
# 4. Load CSS
# ---------------------------------------------------------------

css_file = os.path.join(os.getcwd(), 'assets', 'chatbot_style.css')
with open(css_file) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# ---------------------------------------------------------------
# 5. Chat UI Setup
# ---------------------------------------------------------------

chat_placeholder = st.empty()

if "history" not in st.session_state:
    st.session_state.history = [{
        "origin": "ai", 
        "message": "Hello..! I'm Casper, What's your name? Ask me anything about Chethan or Data science?"
    }]
    st.session_state.chat_id = str(uuid.uuid4())  # Unique chat ID

# ---------------------------------------------------------------
# 6. Render Chat Bubbles
# ---------------------------------------------------------------

def render_chat():
    html_content = ""

    for chat in st.session_state.history:
        chat_icon = (
            f"data:image/png;base64,{ai_icon_base64}" if chat["origin"] == "ai"
            else f"data:image/png;base64,{user_icon_base64}"
        )

        row_class = "" if chat["origin"] == "ai" else "row-reverse"
        bubble_class = "ai-bubble" if chat["origin"] == "ai" else "human-bubble"

        html_content += f"""
        <div class="chat-row {row_class}">
            <img class="chat-icon" src="{chat_icon}" width="32" height="32">
            <div class="chat-bubble {bubble_class}">
                &#8203;{chat['message']}
            </div>
        </div>
        """

    chat_placeholder.markdown(html_content, unsafe_allow_html=True)

render_chat()

# ---------------------------------------------------------------
# 7. Load Chethan Details from Drive
# ---------------------------------------------------------------

def load_chethan_details(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            st.error("Failed to fetch details from Google Drive.")
            return ""
    except Exception as e:
        st.error(f"Error loading details: {e}")
        return ""

chethan_details = load_chethan_details(details_url)

# ---------------------------------------------------------------
# 8. Personal Query Filter
# ---------------------------------------------------------------

def is_personal_query(user_input):
    personal_keywords = []
    return any(keyword in user_input.lower() for keyword in personal_keywords)

# ---------------------------------------------------------------
# 9. Chat Input Handler
# ---------------------------------------------------------------

user_input = st.chat_input("Type your message...")

if user_input:
    # Add user message
    st.session_state.history.append({"origin": "user", "message": user_input})
    render_chat()

    # Block personal questions
    if is_personal_query(user_input):
        ai_response = "Sorry, I cannot answer personal queries."
    else:
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        You are an AI created by Chethan on 14th Jan 2025.
        You are answering questions on Chethan's behalf. Random users will ask you questions.

        If the user asks about Chethan, respond using the following details:
        {chethan_details}

        Please only answer questions related to Chethan and Data Science.
        When providing any links, format them as clickable buttons.
        """

        response = model.generate_content(prompt + "\nUser: " + user_input)
        ai_response = response.candidates[0].content.parts[0].text.strip()

    # Add AI response
    st.session_state.history.append({"origin": "ai", "message": ai_response})
    render_chat()

    # Save to Firebase
    def save_chat_to_firestore(chat_history):
        try:
            chat_collection = db.collection("chat_logs")
            doc_ref = chat_collection.document(st.session_state.chat_id)
            doc_ref.set({
                "chat_history": chat_history,
                "timestamp": firestore.SERVER_TIMESTAMP
            })
        except Exception as e:
            st.error(f"Error saving chat: {e}")

    save_chat_to_firestore(st.session_state.history)

# ---------------------------------------------------------------
# 10. Save Local History Copy (optional)
# ---------------------------------------------------------------

def save_history_to_file():
    with open("chat_history.json", "w") as f:
        json.dump(st.session_state.history, f)

save_history_to_file()
