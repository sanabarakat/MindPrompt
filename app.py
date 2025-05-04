import os
os.environ["STREAMLIT_ENV"] = "production"

import streamlit as st
import datetime
import uuid  
import bcrypt
import pandas as pd
from firebase_config import init_firebase
from first_prompt import generate_first_prompt
from followup_prompt import generate_followup_prompt
from generate_summary import generate_session_summary  
from sentiment_analysis import analyze_sentiment
from firebase_utils import get_latest_journal_entry, save_journal_entry, delete_user_data
from emotion_trends import plot_emotion_trends
from topic_classification import classify_topics  


# Initialize Firebase
db = init_firebase()

st.markdown("""
    <style>
        .main-title { font-size: 32px; font-weight: bold; color: #F4A261; text-align: center; }
        .sub-title { font-size: 20px; color: #E9C46A; text-align: center; }
        .chat-container { padding: 15px; border-radius: 10px; background-color: #2c2c2c; color: white; margin-bottom: 10px; }
        .chat-user { color: #2A9D8F; font-weight: bold; }
        .chat-ai { color: #E76F51; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>📝 MindPrompt - AI Journaling</h1>", unsafe_allow_html=True)
st.markdown("<h2 class='sub-title'>Where AI meets self-reflection!</h2>", unsafe_allow_html=True)

def show_page_intro(title, description):
    st.markdown(f"### 📘 {title}")
    st.markdown(f"<div style='color: gray; font-size: 15px;'>{description}</div>", unsafe_allow_html=True)

def show_chat():
    for sender, msg in st.session_state.chat_history:
        css = "chat-user" if sender == "User" else "chat-ai"
        st.markdown(f"<div class='chat-container {css}'><strong>{sender}:</strong> {msg}</div>", unsafe_allow_html=True)

def reset_to_main_menu():
    st.session_state.page_state = "mode_selection"
    for key in ["chat_history", "session_entries", "first_prompt", "feeling", "awaiting_response"]:
        st.session_state.pop(key, None)
    st.rerun()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "session_entries" not in st.session_state:
    st.session_state.session_entries = []
if "awaiting_response" not in st.session_state:
    st.session_state.awaiting_response = None
if "user_id" not in st.session_state:
    st.session_state.page_state = "home"
if "page_state" not in st.session_state:
    st.session_state.page_state = "home"
if "session_ended" not in st.session_state:   
    st.session_state.session_ended = False

# home page
if st.session_state.page_state == "home":
    user_choice = st.radio("Are you an existing user or joining for the first time?", ["Returning User", "New User"])

    if user_choice == "New User":
        st.subheader("Create Your MindPrompt Account")
        name = st.text_input("Enter your name:")
        email = st.text_input("Email")
        password = st.text_input("Create a password", type="password")
        age = st.number_input("Age", step=1)
        gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
        occupation = st.text_input("Occupation")
        personality = st.radio("Are you more of an introvert or extrovert?", ["Introvert", "Extrovert"])
        country = st.text_input("Which Country do you live in?")
        hobbies = st.text_area("Enter your hobbies (comma-separated):")
        journaling_frequency = st.radio("How often do you journal?", ["Daily", "Couple of Days a Week", "Weekly", "Occasionally", "Never"])
        journaling_time = st.radio("What time of day do you prefer to journal?", ["Morning", "Afternoon", "Evening"])
        question_pattern = st.radio("What pattern of journaling prompts do you prefer?", ["Traditional Journaling Questions tailored to your personality", "AI-Generated Personalized Reflections"])
        question_format = st.multiselect("What category of journaling prompts do you prefer? (select all that apply)", ["Gratitude", "Daily Reflection", "Understanding Emotions", "Personal Growth", "Stress Management", "Coping & Relaxing"])
        expression = st.selectbox("How do you usually express yourself?", ["Writing", "Drawing", "Talking to someone", "keeping it to yourself", "Other"])
        stress = st.radio("Do you experience frequent stress or anxiety?", ["Yes", "No", "Sometimes"])
        stress_reason = st.multiselect("What stresses you out the most? (select all that apply)", ["Work", "Relationships", "Health", "Family", "Personal Issues and Thoughts", "Finances", "Prefer not to say", "Other"])

        agree_to_terms = st.checkbox("I agree to the [terms and conditions](https://www.consilium.europa.eu/en/policies/data-protection-regulation/#:~:text=The%20GDPR%20lists%20the%20rights,his%20or%20her%20personal%20data)")

        if st.button("Create Account"):
            if name.strip() and agree_to_terms:
                existing_user = db.collection("users").where("email", "==", email).stream()
                if any(existing_user):
                    st.error("An account with this email already exists.")
                else:
                    user_id = str(uuid.uuid4())
                    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
                    user_data = {
                        "user_id": user_id,
                        "name": name,
                        "email": email,
                        "password": hashed_password,
                        "age": age,
                        "gender": gender,
                        "occupation": occupation,
                        "personality": personality,
                        "hobbies": hobbies.split(","),
                        "frequency": journaling_frequency,
                        "time": journaling_time,
                        "question_format": question_format,
                        "question_pattern": question_pattern,
                        "expression": expression,
                        "stress": stress,
                        "stress_reason": stress_reason,
                    }
                db.collection("users").document(user_id).set(user_data)
                st.session_state.user_id = user_id
                st.session_state.name = name
                st.session_state.page_state = "mode_selection"
                st.rerun()
            else:
                st.warning("Please enter all details and agree to the terms.")

    elif user_choice == "Returning User":
        st.subheader("Log in to Your Account")
        email = st.text_input("Enter your email:")
        password = st.text_input("Enter your password:", type="password")

        if st.button("Log In"):
            if email.strip() and password.strip():
                query = db.collection("users").where("email", "==", email).limit(1).get()
                if query:
                    user_data = query[0].to_dict()
                    stored_hash = user_data["password"]

                    if bcrypt.checkpw(password.encode(), stored_hash.encode('utf-8')):
                        st.session_state.user_id = user_data["user_id"]
                        st.session_state.name = user_data["name"]
                        st.session_state.page_state = "mode_selection"
                        st.success("✅ Logged in successfully!")
                        st.rerun()

                    else:
                        st.error("❌ Incorrect password.")

                else:
                    st.error("❌ Email not found.")
            else:
                st.warning("⚠️ Please enter your email and password.")



#main menus page
elif st.session_state.page_state == "mode_selection":
    st.markdown(f"<h2 class='sub-title'>Welcome, {st.session_state['name']}! 🌟</h2>", unsafe_allow_html=True)
    st.write("Did you know? Journaling for just a few minutes a day can improve your mental clarity, emotional well-being, and self-awareness. Whether you're processing your thoughts, managing stress, or celebrating moments of gratitude — this space is yours. There’s no right or wrong way to begin, just start where you are.")
    st.write("What would you like to do today?")
    if st.button("🌿 Guided Journaling (Traditional)"):
        st.session_state.page_state = "traditional"
        st.rerun()
    if st.button("🔮 Personalized AI Reflection"):
        st.session_state.page_state = "personalized"
        st.rerun()
    if st.button("📊 View Emotional Trends"):
        st.session_state.page_state = "trends"
        st.rerun()
    if st.button("⚙️ Edit Profile"):
        st.session_state.page_state = "edit_profile"
        st.rerun()
    if st.button("🚪 Log Out"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# emotional trends page
if st.session_state.page_state == "trends":
    st.subheader("📊 Track Your Emotional Trends")
    if st.button("🔙 Back"):
        st.session_state.page_state = "mode_selection"
        st.rerun()
    time_range = st.selectbox("Select Time Range", ["Last 7 Days", "Last 30 Days", "All Time"])
    emotional_data = get_latest_journal_entry(st.session_state.user_id)
    if emotional_data:
        today = datetime.datetime.now(datetime.timezone.utc)
        if time_range == "Last 7 Days":
            start_date = today - datetime.timedelta(days=7)
        elif time_range == "Last 30 Days":
            start_date = today - datetime.timedelta(days=30)
        else:
            start_date = None
        if start_date:
            filtered_data = [entry for entry in emotional_data if "timestamp" in entry and pd.to_datetime(entry["timestamp"], utc=True) >= start_date]
        else:
            filtered_data = emotional_data
        plot_emotion_trends(filtered_data)
    else:
        st.warning("No emotional data available. Start journaling to track trends!")

#editing profile 
elif st.session_state.page_state == "edit_profile":
    user_id = st.session_state.user_id
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()

    if user_doc.exists:
        user_data = user_doc.to_dict()
        st.subheader("Edit Your Profile")

        available_categories = ["Gratitude", "Daily Reflection", "Understanding Emotions", "Personal Growth", "Stress Management", "Coping & Relaxing"]
        user_selected_categories = user_data.get("question_format", [])
        filtered_categories = [c for c in user_selected_categories if c in available_categories]

        available_stressors = ["Work", "Relationships", "Health", "Family", "Personal Issues and Thoughts", "Finances", "Prefer not to say", "Other"]
        user_selected_stressors = user_data.get("stress_reason", [])
        filtered_stressors = [s for s in user_selected_stressors if s in available_stressors]

        with st.form("edit_profile_form"):
            name = st.text_input("Name", value=user_data.get("name", ""))
            password = st.text_input("New Password (leave blank to keep current)", type="password")             
            age = st.number_input("Age", step=1, value=user_data.get("age", 18))
            gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"], index=["Male", "Female", "Other", "Prefer not to say"].index(user_data.get("gender", "Other")))
            occupation = st.text_input("Occupation", value=user_data.get("occupation", ""))
            personality = st.radio("Are you more of an introvert or extrovert?", ["Introvert", "Extrovert"], index=["Introvert", "Extrovert"].index(user_data.get("personality", "Introvert")))
            hobbies = st.text_area("Hobbies (comma-separated)", value=", ".join(user_data.get("hobbies", [])))
            journaling_frequency = st.radio("How often do you journal?", ["Daily", "Couple of Days a Week", "Weekly", "Occasionally"], index=["Daily", "Couple of Days a Week", "Weekly", "Occasionally"].index(user_data.get("frequency", "Weekly")))
            journaling_time = st.radio("Preferred journaling time", ["Morning", "Afternoon", "Evening"], index=["Morning", "Afternoon", "Evening"].index(user_data.get("time", "Morning")))
            question_pattern = st.radio("Prompt Type", ["Traditional Journaling Questions tailored to your personality", "AI-Generated Personalized Reflections"], index=["Traditional Journaling Questions tailored to your personality", "AI-Generated Personalized Reflections"].index(user_data.get("question_pattern", "Traditional Journaling Questions tailored to your personality")))
            question_format = st.multiselect(
                "Prompt Category (you can select multiple)",
                available_categories,
                default=filtered_categories
            )          
            expression = st.selectbox("How do you express yourself?", ["Writing", "Drawing", "Talking to someone", "keeping it to yourself", "Other"], index=["Writing", "Drawing", "Talking to someone", "keeping it to yourself", "Other"].index(user_data.get("expression", "Writing")))
            stress = st.radio("Do you experience frequent stress?", ["Yes", "No", "Sometimes"], index=["Yes", "No", "Sometimes"].index(user_data.get("stress", "Sometimes")))
            stress_reason = st.multiselect(
                "What stresses you out the most? (select all that apply)",
                available_stressors,
                default=filtered_stressors
            )
                
            submitted = st.form_submit_button("Update Profile")
            if submitted:
                updated_data = {
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "occupation": occupation,
                    "personality": personality,
                    "hobbies": hobbies.split(","),
                    "frequency": journaling_frequency,
                    "time": journaling_time,
                    "question_format": question_format,
                    "question_pattern": question_pattern,
                    "expression": expression,
                    "stress": stress,
                    "stress_reason": stress_reason,
                }
                if password.strip():
                    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
                    updated_data["password"] = hashed_password
                user_ref.update(updated_data)
                st.success("Profile updated successfully!")
                st.session_state.name = name  
                st.session_state.page_state = "mode_selection"
                st.rerun()
    else:
        st.error("User not found.")

    st.warning("Deleting your account will permanently erase your data.")
    delete_confirm = st.checkbox("I understand and want to delete my account")

    if st.button("Delete Account") and delete_confirm:
        user_id = st.session_state.user_id
        delete_user_data(user_id)
        st.success("Your account has been deleted.")
        st.session_state.clear()
        st.rerun()

    if st.button("🔙 Back"):
        st.session_state.page_state = "mode_selection"
        st.rerun()

 
# personalized journaling page
elif st.session_state.page_state == "personalized":
    show_page_intro("Personalized Journaling", "Let AI guide your self-reflection based on how you feel.")

    if "feeling" not in st.session_state:
        feeling = st.text_area("How are you feeling today?")

        if st.button("Submit Feeling") and feeling.strip():
            sentiment_score = analyze_sentiment(feeling)
            topics = classify_topics(feeling)
            st.session_state.chat_history.append(("User", feeling))
            followup_prompt = generate_followup_prompt(
                st.session_state.user_id,
                feeling,
                st.session_state.session_entries
            )
            st.session_state.chat_history.append(("AI", followup_prompt))
            st.session_state.session_entries.append({
                "question": "How are you feeling today?",
                "answer": feeling,
                "sentiment": {
                    "dominant_emotion": sentiment_score["dominant_emotion"],
                    "top_3_emotions": sentiment_score["top_3_emotions"],
                    "emotion_scores": sentiment_score["emotion_scores"]
                },
                "topics": topics
            })
            st.session_state.session_entries.append({"question": followup_prompt, "answer": None})
            st.session_state.feeling = feeling
            st.session_state.awaiting_response = "user_journal_entry"
            st.rerun()

    elif st.session_state.get("awaiting_response") == "user_journal_entry":
        st.text_area("Your response:", key="journal_input")

    if st.button("🔙 Back"):
        reset_to_main_menu()


# traditional journaling page
elif st.session_state.page_state == "traditional":
    show_page_intro("Traditional Journaling", "Answer thought-provoking questions tailored to your personality.")
    adapted_prompt = generate_first_prompt(st.session_state.user_id)
    if "first_prompt" not in st.session_state:
        traditional = st.write("Reflect on this prompt....")        
        first_prompt = adapted_prompt
        st.session_state.first_prompt = first_prompt

        st.session_state.chat_history.append(("AI", first_prompt))
        st.session_state.session_entries.append({"question": first_prompt, "answer": None})
        st.session_state.awaiting_response = "user_journal_entry"
        st.rerun()

    if st.button("🔙 Back"):
        reset_to_main_menu()



if "chat_history" in st.session_state:
    for role, message in st.session_state["chat_history"]:
        if role == "User":
            st.markdown(f"<div class='chat-container'><span class='chat-user'>👤 {role}:</span> {message}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-container'><span class='chat-ai'>🤖 {role}:</span> {message}</div>", unsafe_allow_html=True)

if st.session_state.get("awaiting_response") == "user_journal_entry":
    if not st.session_state.get("session_ended", False):
        journal_entry = st.text_area("Your response:", key="journal_input")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Move to the next Question") and journal_entry.strip():
                sentiment_score = analyze_sentiment(journal_entry)
                topics = classify_topics(journal_entry)
                st.session_state.chat_history.append(("User", journal_entry))
                st.session_state.session_entries[-1]["answer"] = journal_entry
                st.session_state.session_entries[-1]["topics"] = topics
                st.session_state.session_entries[-1]["sentiment"] = {
                    "dominant_emotion": sentiment_score["dominant_emotion"],
                    "top_3_emotions": sentiment_score["top_3_emotions"],
                    "emotion_scores": sentiment_score["emotion_scores"]
                }

                st.session_state.pop("journal_input", None)

                if st.session_state.page_state == "traditional":
                    next_prompt = generate_first_prompt(st.session_state.user_id)
                else:
                    next_prompt = generate_followup_prompt(
                        st.session_state.user_id,
                        journal_entry,
                        st.session_state.session_entries
                    )

                st.session_state.chat_history.append(("AI", next_prompt))
                st.session_state.session_entries.append({"question": next_prompt, "answer": None})
                st.rerun()

        with col2:
            if st.button("Submit Answer and End Session") and journal_entry.strip():
                sentiment_score = analyze_sentiment(journal_entry)
                topics = classify_topics(journal_entry)
                st.session_state.chat_history.append(("User", journal_entry))
                st.session_state.session_entries[-1]["answer"] = journal_entry
                st.session_state.session_entries[-1]["topics"] = topics
                st.session_state.session_entries[-1]["sentiment"] = {
                    "dominant_emotion": sentiment_score["dominant_emotion"],
                    "top_3_emotions": sentiment_score["top_3_emotions"],
                    "emotion_scores": sentiment_score["emotion_scores"]
                }

                st.session_state["session_ended"] = True

                summary = generate_session_summary(st.session_state["session_entries"], st.session_state["user_id"])
                st.session_state["chat_history"].append(("AI", f"📌 **Reflection Summary**: {summary}"))

                save_journal_entry(st.session_state["user_id"], st.session_state["session_entries"])

                st.success("Session saved! 🌟")
                st.markdown(f"**Reflection Summary:** {summary}")


