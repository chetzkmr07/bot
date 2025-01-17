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

# Firebase initialization using credentials from Streamlit secrets
try:
    if not firebase_admin._apps:
        # Get the firebase credentials from Streamlit secrets
        firebase_creds = st.secrets["firebase"]

        # Convert AttrDict to a regular dict
        cred_dict = dict(firebase_creds)

        # Initialize Firebase app with the credentials dictionary
        cred = credentials.Certificate(cred_dict)
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
        prompt = ("""You are an AI Created by chethan on 14th jan 2025, 
            You are answering questions on chethan's behalf, random users will ask you questions.
            if user asks about me, tell them mainly about my professional details
              Please only answer questions related to chethan and Data Science.
              and provide a clickable buttons instead of raw links

            Personal Information:
            - Name: Chethan
            - Location: Mangalore, Karnataka, India
            - Date of Birth: 19th May 1993
            - Age: 31
            - Hobbies: Watching movies & web series, being creative or doing creative things, reading,
              long drives, listening to music
            - Diet: Vegan
            - Belief: Believes in humanity as a religion, though born Hindu
            - Animal & Nature Lover
            - Favourite food: Veg koftha, aloo paratha
            - martial status unmarried
            - favourite movie: interstellar, megamind in animated movies
            - favourite fruit: apple, pineapple, watermelon
            - currently living in mangalore
            - sexual orientation: straight
            - favourite animal: tiger
            - favourite bird : vulture
            - not very religious
            - i live with my mom, dad, aunt, uncle
            - siblings: none

            other details:
            - willing to relocate for work
            - willing to relocate out of india as well
            - loves to travel
            - i play cricket, football, volleyball, chess, carrom, badminton, boardgames
            - i love techs
            - i cant work on night shifts
            - i have passport, pan, adhaar card
            - driving license: 2 wheeler and 4 wheeler light motor vehicles
            - commited crime or criminal record: never
            - police case: none
            - owns laptop, can work remotely or work from home
            - languages known: English, kannada, hindi, tulu, konkani
            

            Contact Details:
            - Mobile: +918553275796
            - Email: chethan.kmr07@gmail.com
            - LinkedIn: https://www.linkedin.com/in/chethankmr
            - GitHub: https://github.com/chetzkmr
            - Portfolio: https://chethan-kmr.web.app

            Professional Summary:
            I am a Data Science Enthusiast with an IBM-certified background in Data Analysis and Data Science. I specialize in transforming raw data into actionable insights through data manipulation, statistical analysis, and predictive modeling. Passionate about exploring patterns and trends to enable data-driven decision-making.

            Skills:
            - Python, SQL, Power BI, Tableau, MongoDB, Jupyter Notebook, data analysis, data wrangling, Advanced excel, MS Office
                Auto-cad.
            - Data Science: Machine Learning, Deep Learning, Predictive Modeling

            Work Experience:
            Learnbay (Remote) — Data Science Intern, 08/2023 - 08/2024
            - Improved dropout prediction model accuracy by 20% using SQL and Power BI.
            - Encoded 6 categorical variables, enhancing model performance and providing more meaningful insights for strategic
                planning.
            - Elevated model performance by 10% and reduced false positives by 25%, leading to more accurate predictions and cost
                savings.
            -  Provided actionable insights to academic advisors, enhancing 90% retention strategies.

            Shankar Sandwich Panel Pvt. Ltd. — Production In-Charge, tumkur, 10/2021 - 04/2023
            - Achieved 98% inspection accuracy, reducing defective products by 12%.
            - Guiding a team to achieve a 15% increase in production output, resulting in meeting customer demands and improving
                overall efficiency
            - Maintained optimal inventory levels, resulting in a 25% reduction in material waste and ensuring on-time production
                schedules.

            Winman llp - Assistance software developer, mangalore, 03/2020 - 03/2021
            - Coordinating with testing team to implement changes, resulting in a 18% decrease in software bugs and Streamlined
overall product quality.
            - Boosting efficiency and productivity by 20% by quickly implementing new client-requested changes, resulting in
increased client satisfaction and retention.
            - Developed efficient office software, increasing productivity by 10% and streamlining workflow processes for the entire
team
            -Improved product performance by 15% through the development and implementation of testing protocols, enhancing
reliability and meeting industry standards.


            Education:
            - SSLC/10th from Padua high school, secured 83.04%
            - Diploma in Automobile engineering, karnataka polytechnic mangalore, 2012-2014
            - B.Tech in Automobile Engineering, Srinivas Institute of Technology, 2014–2017

            Recent Projects:
            - AI Chatbot
            - Super Store Sales, power bi dashboard and forcast analysis project
            - Gameplay Analysis. github link - https://github.com/chetzkmr/Gameplay-Analysis
            - Particle Physics Event Classification. github link - https://github.com/chetzkmr/Particle-Physics-Events-Classification
            - Movie Recommendation System. github link - https://github.com/chetzkmr/Movie-recommendation-sysytem
            - Monitoring in Marine Systems. github link - https://github.com/chetzkmr/Monitoring-in-marine-system
            - Fraudulent ATM Transaction Detection. github link - https://github.com/chetzkmr/Fraudulent-ATM-transaction-Detection
            - AmbitionBox WebScarping
            - Apartment Price Predictor
            - Employee Management System, SQL project
            - Inventory Autoupdater, SQL project
            - Employee Attrition Analysis, SQL project
            - HR Analytics Dashboard, Power BI project
            - Data Professional Survey, Power BI project

            if any user asks more details of project, provide them chethans portfolio link

            Certifications:
            - Advanced Data Science and AI, Learnbay 2023-2024
            - Python for Data Science, IBM
            - Machine Learning with Python, IBM
            """
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
