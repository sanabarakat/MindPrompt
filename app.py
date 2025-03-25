import os
os.environ["STREAMLIT_ENV"] = "production"

import streamlit as st
import datetime
import uuid  
import pandas as pd
from firebase_config import init_firebase
from firebase_admin import firestore
from firebase_admin import auth
from first_prompt import generate_first_prompt
from followup_prompt import generate_followup_prompt
from generate_summary import generate_session_summary  
from sentiment_analysis import analyze_sentiment
from firebase_utils import get_latest_journal_entry, save_journal_entry
from emotion_trends import plot_emotion_trends

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

# Initialize page state
if "page_state" not in st.session_state:
    st.session_state.page_state = "home"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "session_entries" not in st.session_state:
    st.session_state.session_entries = []

# === PAGE: HOME ===
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
        journaling_frequency = st.radio("How often do you journal?", ["Daily", "Couple of Days a Week", "Weekly", "Occasionally"])
        journaling_time = st.radio("What time of day do you prefer to journal?", ["Morning", "Afternoon", "Evening"])
        question_pattern = st.radio("What pattern of journaling prompts do you prefer?", ["Traditional Journaling Questions tailored to your personality", "AI-Generated Personalized Reflections"])
        question_format = st.selectbox("What category of journaling prompts do you prefer?", ["Gratitude", "Daily Reflection", "Understanding Emotions", "Personal Growth", "Stress Management", "Coping & Relaxing"])
        expression = st.selectbox("How do you usually express yourself?", ["Writing", "Drawing", "Talking to someone", "keeping it to yourself", "Other"])
        stress = st.radio("Do you experience frequent stress or anxiety?", ["Yes", "No", "Sometimes"])
        stress_reason = st.selectbox("What stresses you out the most?", ["Work", "Relationships", "Health", "Family", "Personal Issues and Thoughts", "Finances", "Prefer not to say", "Other"])

        agree_to_terms = st.checkbox("I agree to the [terms and conditions](https://www.consilium.europa.eu/en/policies/data-protection-regulation/#:~:text=The%20GDPR%20lists%20the%20rights,his%20or%20her%20personal%20data)")

        if st.button("Create Account"):
            if name.strip() and agree_to_terms:
                existing_user = db.collection("users").where("email", "==", email).stream()
                if any(existing_user):
                    st.error("❌ An account with this email already exists.")
                else:
                    user_id = str(uuid.uuid4())
                    user_data = {
                        "user_id": user_id,
                        "name": name,
                        "email": email,
                        "password": password,
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
                st.warning("⚠️ Please enter all details and agree to the terms.")

     # user login           
    elif user_choice == "Returning User":
        if "login_mode" not in st.session_state:
            st.session_state.login_mode = "normal"  # can be 'normal' or 'forgot'

        if st.session_state.login_mode == "normal":
            st.subheader("Log in to Your Account")
            email = st.text_input("Enter your email:")
            password = st.text_input("Enter your password:", type="password")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Log In"):
                    if email.strip() and password.strip():
                        users_ref = db.collection("users")
                        query = users_ref.where("email", "==", email).limit(1).get()
                        if query:
                            user_data = query[0].to_dict()
                            if user_data["password"] == password:
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

            with col2:
                if st.button("Forgot Password?"):
                    st.session_state.login_mode = "forgot"
                    st.rerun()

        # =============================
        # PASSWORD RESET FLOW
        # =============================
        elif st.session_state.login_mode == "forgot":
            st.subheader("🔐 Reset Your Password")
            reset_email = st.text_input("Enter your email to reset password:")
            if st.button("Send Reset Code"):
                if reset_email.strip():
                    reset_code = str(uuid.uuid4())[:8]
                    st.session_state["reset_code"] = reset_code
                    st.session_state["reset_email"] = reset_email
                    st.warning(f"A password reset code was generated: **{reset_code}** (in production, you'd email it!)")
                    st.session_state.page_state = "reset_password"
                    st.rerun()
                else:
                    st.warning("⚠️ Please enter your email.")

            if st.button("🔙 Back to Login"):
                st.session_state.login_mode = "normal"
                st.rerun()


elif st.session_state.page_state == "reset_password":
    st.subheader("Enter Your Reset Code")
    code = st.text_input("Reset Code:")
    new_password = st.text_input("New Password:", type="password")

    if st.button("Reset Password"):
        if code.strip() == st.session_state.get("reset_code", ""):
            email = st.session_state.get("reset_email")
            users_ref = db.collection("users")
            query = users_ref.where("email", "==", email).limit(1).get()
            if query:
                user_doc = query[0]
                user_doc.reference.update({"password": new_password})
                st.success("✅ Password updated successfully! You can now log in.")
                st.session_state.login_mode = "normal"
                st.session_state.page_state = "home"
                st.rerun()
            else:
                st.error("❌ User not found.")
        else:
            st.error("❌ Incorrect reset code.")

    if st.button("🔙 Back to Login"):
        st.session_state.login_mode = "normal"
        st.rerun()





# === PAGE: MODE SELECTION ===
elif st.session_state.page_state == "mode_selection":
    st.markdown(f"<h2 class='sub-title'>Welcome, {st.session_state['name']}! 🌟</h2>", unsafe_allow_html=True)
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

# === PAGE: PERSONALIZED JOURNALING ===
elif st.session_state.page_state == "personalized" and "feeling" not in st.session_state:
    user_feeling = st.text_area("How are you feeling today?", key="feeling_input")
    
    if st.button("Submit Feeling", key="submit_feeling") and user_feeling.strip():
        st.session_state.chat_history.append(("User", user_feeling))
        followup_prompt = generate_followup_prompt(
            st.session_state.user_id, user_feeling, st.session_state.session_entries
        )
        st.session_state.chat_history.append(("AI", followup_prompt))
        st.session_state.session_entries.append({"question": "How are you feeling today?", "answer": user_feeling})
        st.session_state.session_entries.append({"question": followup_prompt, "answer": None})
        st.session_state.awaiting_response = "user_journal_entry"
        st.session_state.feeling = user_feeling  # Save feeling for follow-up logic
        st.rerun()

    if st.button("🔙 Back", key="back_from_personalized"):
        st.session_state.page_state = "mode_selection"
        st.rerun()



elif st.session_state.page_state == "traditional":
    user_id = st.session_state.user_id
    if st.button("🔙 Back"):
        st.session_state.page_state = "mode_selection"
        st.rerun()
    if "first_prompt" not in st.session_state:
        first_prompt = generate_first_prompt(user_id)
        st.session_state.first_prompt = first_prompt
        st.session_state.chat_history.append(("AI", first_prompt))
        st.session_state.session_entries.append({"question": first_prompt, "answer": None})
        st.session_state.awaiting_response = "user_journal_entry"
        st.rerun()
    else:
        # Show the prompt if it's already stored
        st.markdown(f"**{st.session_state.first_prompt}**")
        st.session_state.awaiting_response = "user_journal_entry"


# === PAGE: EMOTIONAL TRENDS ===
elif st.session_state.page_state == "trends":
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

# === PAGE: EDIT PROFILE ===
elif st.session_state.page_state == "edit_profile":
    user_id = st.session_state.user_id
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()

    if user_doc.exists:
        user_data = user_doc.to_dict()
        st.subheader("Edit Your Profile")

        with st.form("edit_profile_form"):
            name = st.text_input("Name", value=user_data.get("name", ""))
            password = st.text_input("Password", type="password", value=user_data.get("password", ""))
            age = st.number_input("Age", step=1, value=user_data.get("age", 18))
            gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"], index=["Male", "Female", "Other", "Prefer not to say"].index(user_data.get("gender", "Other")))
            occupation = st.text_input("Occupation", value=user_data.get("occupation", ""))
            personality = st.radio("Are you more of an introvert or extrovert?", ["Introvert", "Extrovert"], index=["Introvert", "Extrovert"].index(user_data.get("personality", "Introvert")))
            hobbies = st.text_area("Hobbies (comma-separated)", value=", ".join(user_data.get("hobbies", [])))
            journaling_frequency = st.radio("How often do you journal?", ["Daily", "Couple of Days a Week", "Weekly", "Occasionally"], index=["Daily", "Couple of Days a Week", "Weekly", "Occasionally"].index(user_data.get("frequency", "Weekly")))
            journaling_time = st.radio("Preferred journaling time", ["Morning", "Afternoon", "Evening"], index=["Morning", "Afternoon", "Evening"].index(user_data.get("time", "Morning")))
            question_pattern = st.radio("Prompt Type", ["Traditional Journaling Questions tailored to your personality", "AI-Generated Personalized Reflections"], index=["Traditional Journaling Questions tailored to your personality", "AI-Generated Personalized Reflections"].index(user_data.get("question_pattern", "Traditional Journaling Questions tailored to your personality")))
            question_format = st.selectbox("Prompt Category", ["Gratitude", "Daily Reflection", "Understanding Emotions", "Personal Growth", "Stress Management", "Coping & Relaxing"], index=["Gratitude", "Daily Reflection", "Understanding Emotions", "Personal Growth", "Stress Management", "Coping & Relaxing"].index(user_data.get("question_format", "Gratitude")))
            expression = st.selectbox("How do you express yourself?", ["Writing", "Drawing", "Talking to someone", "keeping it to yourself", "Other"], index=["Writing", "Drawing", "Talking to someone", "keeping it to yourself", "Other"].index(user_data.get("expression", "Writing")))
            stress = st.radio("Do you experience frequent stress?", ["Yes", "No", "Sometimes"], index=["Yes", "No", "Sometimes"].index(user_data.get("stress", "Sometimes")))
            stress_reason = st.selectbox("What stresses you most?", ["Work", "Relationships", "Health", "Family", "Personal Issues and Thoughts", "Finances", "Prefer not to say", "Other"], index=["Work", "Relationships", "Health", "Family", "Personal Issues and Thoughts", "Finances", "Prefer not to say", "Other"].index(user_data.get("stress_reason", "Other")))

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
                user_ref.update(updated_data)
                st.success("✅ Profile updated successfully!")
                st.session_state.name = name  # Update UI name
                st.session_state.page_state = "mode_selection"
                st.rerun()
    else:
        st.error("User not found.")

    if st.button("🔙 Back"):
        st.session_state.page_state = "mode_selection"
        st.rerun()



# === JOURNALING RESPONSE ===
if st.session_state.get("awaiting_response") == "user_journal_entry":
    
    if st.session_state.page_state == "personalized":
        journal_entry = st.text_area("Your response:", key="personalized_response")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Submit Answer", key="submit_personalized_answer") and journal_entry.strip():
                sentiment_score = analyze_sentiment(journal_entry)
                st.session_state.chat_history.append(("User", journal_entry))
                st.session_state.session_entries[-1]["answer"] = journal_entry
                st.session_state.session_entries[-1]["sentiment"] = sentiment_score
                
                # Generate the next follow-up prompt
                followup_prompt = generate_followup_prompt(
                    st.session_state.user_id,
                    journal_entry,
                    st.session_state.session_entries
                )
                st.session_state.chat_history.append(("AI", followup_prompt))
                st.session_state.session_entries.append({"question": followup_prompt, "answer": None})
                st.rerun()

        with col2:
            if st.button("Submit Answer and End Session", key="end_personalized_session") and journal_entry.strip():
                sentiment_score = analyze_sentiment(journal_entry)
                st.session_state.chat_history.append(("User", journal_entry))
                st.session_state.session_entries[-1]["answer"] = journal_entry
                st.session_state.session_entries[-1]["sentiment"] = sentiment_score
                summary = generate_session_summary(st.session_state.session_entries)
                st.session_state.chat_history.append(("AI", f"📌 **Reflection Summary**: {summary}"))
                save_journal_entry(st.session_state.user_id, st.session_state.session_entries)
                st.success("Session saved! 🌟")
                st.markdown(f"**Reflection Summary:** {summary}")
                if st.button("Start New Session", key="restart_personalized"):
                    st.session_state.page_state = "mode_selection"
                    st.session_state.chat_history.clear()
                    st.session_state.session_entries.clear()
                    if "first_prompt" in st.session_state:
                        del st.session_state["first_prompt"]
                    if "feeling" in st.session_state:
                        del st.session_state["feeling"]
                    st.rerun()


