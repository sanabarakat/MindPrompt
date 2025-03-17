import streamlit as st
import datetime
import uuid  
from firebase_config import init_firebase
import firebase_admin
from firebase_admin import firestore
from first_prompt import generate_first_prompt
from followup_prompt import generate_followup_prompt
from generate_summary import generate_session_summary  
from sentiment_analysis import analyze_sentiment
from firebase_utils import get_latest_journal_entry, save_journal_entry
from emotion_trends import plot_emotion_trends
import datetime
import pandas as pd


# Initialize Firebase
db = init_firebase()

# Custom Styling for Chat Display
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

# Initialize session state variables if not set
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "session_entries" not in st.session_state:
    st.session_state["session_entries"] = []

# **User Login / Registration**
if "user_id" not in st.session_state:
    user_choice = st.radio("Are you an existing user or joining for the first time?", ["Returning User", "New User"])

    # **New User Registration**
    if user_choice == "New User":
        st.subheader("Create Your MindPrompt Account")
        name = st.text_input("Enter your name:")
        age = st.number_input("Age", step=1)
        gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
        occupation = st.text_input("Occupation")
        personality = st.radio("Are you more of an introvert or extrovert?", ["Introvert", "Extrovert"])
        hobbies = st.text_area("Enter your hobbies (comma-separated):")
        journaling_frequency = st.radio("How often do you journal?", ["Daily", "Weekly", "Occasionally"])
        journaling_time = st.radio("What time of day do you prefer to journal?", ["Morning", "Afternoon", "Evening"])
        question_format = st.selectbox("What category of journaling prompts do you prefer?", 
                                       ["Gratitude", "Daily Reflection", "Understanding Emotions", "Personal Growth", "Stress Management", "Coping & Relaxing"])
        
        agree_to_terms = st.checkbox("I agree to the Terms and Conditions")

        if st.button("Create Account"):
            if name.strip() and agree_to_terms:
                user_id = str(uuid.uuid4())  # Generate a unique User ID
                user_data = {
                    "user_id": user_id,
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "occupation": occupation,
                    "personality": personality,
                    "hobbies": hobbies.split(","),
                    "frequency": journaling_frequency,
                    "time": journaling_time,
                    "question_format": question_format
                }

                # Save user data in Firebase
                db.collection("users").document(user_id).set(user_data)

                # Store session state
                st.session_state["user_id"] = user_id
                st.session_state["name"] = name

                st.success(f"🎉 Account created successfully! Your User ID: `{user_id}`")
                st.info("📌 Save your User ID to log in next time.")  
            else:
                st.warning("⚠️ Please enter all details and agree to the terms.")

    # **Returning User Login**
    elif user_choice == "Returning User":
        st.subheader("Log in to Your Account")
        user_id = st.text_input("Enter your User ID:")

        if st.button("Log In"):
            if user_id.strip():
                user_doc = db.collection("users").document(user_id).get()
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    st.session_state["user_id"] = user_data["user_id"]
                    st.session_state["name"] = user_data["name"]
                    st.success(f"👋 Welcome back, {user_data['name']}!")
                else:
                    st.error("❌ User ID not found. Please check and try again.")
            else:
                st.warning("⚠️ Please enter your User ID.")

# **Journaling Session**
if "user_id" in st.session_state:
    st.markdown(f"<h2 class='sub-title'>Welcome, {st.session_state['name']}! 🌟</h2>", unsafe_allow_html=True)

    # **Chat History Display**
    for role, message in st.session_state.get("chat_history", []):
        if role == "User":
            st.markdown(f"<div class='chat-container'><span class='chat-user'>👤 {role}:</span> {message}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-container'><span class='chat-ai'>🤖 {role}:</span> {message}</div>", unsafe_allow_html=True)

    # **Journaling Mode Selection**
    if "journaling_mode" not in st.session_state:
        if st.button("🌿 Guided Journaling (Traditional)"):
            st.session_state["journaling_mode"] = "traditional"
            st.rerun()
        if st.button("🔮 Personalized AI Reflection"):
            st.session_state["journaling_mode"] = "personalized"
            st.rerun()

        if st.button("📊 View Emotional Trends"):
            st.session_state["journaling_mode"] = "trends"
            st.rerun()

    if "journaling_mode" in st.session_state:
        user_id = st.session_state["user_id"]

        # **Step 1: Ask How They Feel (For Personalized Mode)**
        if st.session_state["journaling_mode"] == "personalized" and "feeling" not in st.session_state:
            user_feeling = st.text_area("How are you feeling today?")
            if st.button("Submit Feeling") and user_feeling.strip():
                st.session_state["chat_history"].append(("User", user_feeling))
                followup_prompt = generate_followup_prompt(user_id, user_feeling)
                st.session_state["chat_history"].append(("AI", followup_prompt))
                st.session_state["session_entries"].append({"question": "How are you feeling today?", "answer": user_feeling})
                st.session_state["session_entries"].append({"question": followup_prompt, "answer": None})
                st.session_state["awaiting_response"] = "user_journal_entry"
                st.session_state["feeling"] = True  # Mark feeling as answered
                st.rerun()

        # **Step 2: Traditional Mode - Get First Prompt**
        elif st.session_state["journaling_mode"] == "traditional":
            if "first_prompt" not in st.session_state:
                first_prompt = generate_first_prompt(user_id)
                st.session_state["first_prompt"] = first_prompt  # Store the prompt to prevent regenerating it
                st.session_state["chat_history"].append(("AI", first_prompt))
                st.session_state["session_entries"].append({"question": first_prompt, "answer": None})
                st.session_state["awaiting_response"] = "user_journal_entry"
                st.rerun()


        elif st.session_state["journaling_mode"] == "trends":
            st.subheader("📊 Track Your Emotional Trends")
            time_range = st.selectbox("Select Time Range", ["Last 7 Days", "Last 30 Days", "All Time"])

            # Fetch emotional data from Firestore
            user_id = st.session_state["user_id"]
            emotional_data = get_latest_journal_entry(user_id)

            if emotional_data:
                # **Get today's date with timezone awareness**
                today = datetime.datetime.now(datetime.timezone.utc)  # Ensure timezone awareness

                if time_range == "Last 7 Days":
                    start_date = today - datetime.timedelta(days=7)
                elif time_range == "Last 30 Days":
                    start_date = today - datetime.timedelta(days=30)
                else:
                    start_date = None  # No filtering for "All Time"

                if start_date:
                    # **Ensure timestamps in data are also timezone-aware**
                    filtered_data = [
                        entry for entry in emotional_data 
                        if "timestamp" in entry 
                        and pd.to_datetime(entry["timestamp"], utc=True) >= start_date
                    ]
                else:
                    filtered_data = emotional_data  # Use all data for "All Time"

                st.write("🔍 Debug: Filtered Data Based on Time Range:", filtered_data)
                plot_emotion_trends(filtered_data)  # Pass filtered data
            else:
                st.warning("No emotional data available. Start journaling to track trends!")


        # **Step 3: Journal Entry Response**
        if st.session_state.get("awaiting_response") == "user_journal_entry":
            journal_entry = st.text_area("Your response:")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Submit Answer") and journal_entry.strip():
                    sentiment_score = analyze_sentiment(journal_entry)
                    st.session_state["chat_history"].append(("User", journal_entry))
                    st.session_state["session_entries"][-1]["answer"] = journal_entry
                    st.session_state["session_entries"][-1]["sentiment"] = sentiment_score
                    
                    # **Generate new question AFTER user answers**
                    next_prompt = generate_first_prompt(user_id)
                    st.session_state["chat_history"].append(("AI", next_prompt))
                    st.session_state["session_entries"].append({"question": next_prompt, "answer": None})

                    st.rerun()


            with col2:
                if st.button("Submit Answer and End Session") and journal_entry.strip():
                    sentiment_score = analyze_sentiment(journal_entry)

                    # Append final entry with sentiment
                    st.session_state["chat_history"].append(("User", journal_entry))
                    st.session_state["session_entries"][-1]["answer"] = journal_entry
                    st.session_state["session_entries"][-1]["sentiment"] = sentiment_score

                    # Generate summary before saving
                    summary = generate_session_summary(st.session_state["session_entries"])
                    st.session_state["chat_history"].append(("AI", f"📌 **Reflection Summary**: {summary}"))

                    # **Save structured session in Firebase**
                    save_journal_entry(st.session_state["user_id"], st.session_state["session_entries"])

                    # Display summary
                    st.success("Session saved! 🌟")
                    st.markdown(f"**Reflection Summary:** {summary}")

                    if st.button("Start New Session"):
                        st.session_state.clear()
                        st.rerun()
