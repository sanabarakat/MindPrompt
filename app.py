import streamlit as st
import datetime
import uuid  
from firebase_config import init_firebase
import firebase_admin
from firebase_admin import credentials, firestore
from generate_prompt import generate_personalized_prompt
from sentiment_analysis import analyze_sentiment
from generate_summary import generate_session_summary  


db = init_firebase()

st.title("📝 MindPrompt - AI Journaling")
st.header("Where AI meets self-reflection!")

# Prevent login section from showing after user logs in
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
        reason = st.selectbox("What would you say is the main reason you want to journal?", 
                              ["Daily Reflection",  "Personal Growth", "Coping & Relaxing", 
                               "Understanding Emotions", "Gratitude", "Stress Managamenet","Other"])
        expression = st.selectbox("How do you usually express yourself?", 
                                  ["Writing", "Drawing", "Talking", "keeping it to yourself", "Other"])
        stress = st.radio("Do you experience frequent stress or anxiety?", ["Yes", "No", "Sometimes"])
        stress_reason = st.selectbox("What stresses you out the most?", 
                                     ["Work", "Relationships", "Health", "Family", "Personal Issues and Thoughts", 
                                      "Finances", "Prefer not to say", "Other"])
        question_format = st.radio("What format of journaling questions do you prefer?", 
                                   ["open-ended questions", "structured reflection prompts"])
        
        agree_to_terms = st.checkbox(
            "I agree to the [terms and conditions](https://www.consilium.europa.eu/en/policies/data-protection-regulation/#:~:text=The%20GDPR%20lists%20the%20rights,his%20or%20her%20personal%20data)")
        
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
                    "reason": reason,
                    "expression": expression,
                    "stress": stress,
                    "stress_reason": stress_reason,
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
                # Search for user in Firebase
                user_doc = db.collection("users").document(user_id).get()

                if user_doc.exists:
                    user_data = user_doc.to_dict()

                    # Store session state
                    st.session_state["user_id"] = user_data["user_id"]
                    st.session_state["name"] = user_data["name"]

                    st.success(f"👋 Welcome back, {user_data['name']}!")
                else:
                    st.error("❌ User ID not found. Please check and try again.")
            else:
                st.warning("⚠️ Please enter your User ID.")

# **Journaling Section (Only Show if Logged In)**
if "user_id" in st.session_state:
    st.subheader(f"🖊️ Welcome, {st.session_state['name']}!")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
        st.session_state["session_entries"] = []  # Stores both questions & answers
        st.session_state["awaiting_response"] = "feeling_check"

    # **Display Chat History**
    for role, message in st.session_state["chat_history"]:
        st.write(f"**{role}:** {message}")

    # **Step 1: Ask User How They Feel**
    if st.session_state["awaiting_response"] == "feeling_check":
        user_feeling = st.text_area("How are you feeling today?")
        if st.button("Submit Feeling"):
            if user_feeling.strip():
                st.session_state["session_entries"].append({"question": "How are you feeling today?", "answer": user_feeling})
                st.session_state["chat_history"].append(("User", user_feeling))
                ai_response = "Thank you for sharing. It's important to acknowledge your emotions. Let's explore this further!"
                st.session_state["chat_history"].append(("AI", ai_response))
                st.session_state["awaiting_response"] = "generate_prompt"
                st.rerun()

    # **Step 2: Generate AI Prompt**
    if st.session_state["awaiting_response"] == "generate_prompt":
        last_feeling = st.session_state["session_entries"][0]["answer"]  # Extract feeling
        prompt = generate_personalized_prompt(st.session_state["user_id"], last_feeling, st.session_state["session_entries"])
        
        # **Store the AI-generated prompt**
        st.session_state["session_entries"].append({"question": prompt, "answer": None})  
        st.session_state["chat_history"].append(("AI", f"💡 **Journaling Prompt:** {prompt}"))
        st.session_state["awaiting_response"] = "user_journal_entry"
        st.rerun()

    # **Step 3: Journal Entry**
    if st.session_state["awaiting_response"] == "user_journal_entry":
        journal_entry = st.text_area("Write your journal entry:")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Submit Answer"):
                if journal_entry.strip():
                    # **Save answer to the last generated question**
                    if st.session_state["session_entries"][-1]["answer"] is None:
                        st.session_state["session_entries"][-1]["answer"] = journal_entry  
                    else:
                        st.session_state["session_entries"].append({"question": None, "answer": journal_entry})
                    
                    st.session_state["chat_history"].append(("User", journal_entry))
                    st.session_state["awaiting_response"] = "generate_prompt"
                    st.rerun()

        with col2:
            if st.button("Submit Answer and End Session"):
                if journal_entry.strip():
                    # **Save final answer before ending session**
                    if st.session_state["session_entries"][-1]["answer"] is None:
                        st.session_state["session_entries"][-1]["answer"] = journal_entry
                    else:
                        st.session_state["session_entries"].append({"question": None, "answer": journal_entry})

                    # **Generate final session summary**
                    summary = generate_session_summary(st.session_state["session_entries"])
                    st.session_state["chat_history"].append(("AI", f"📌 **Final Reflection**:\n\n{summary}"))

                    # **Save entire conversation in Firebase (all Q&A pairs)**
                    db.collection("journals").add({
                        "user_id": st.session_state["user_id"],
                        "session_entries": st.session_state["session_entries"],
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

                    st.session_state["awaiting_response"] = "session_summary"
                    st.rerun()

    # **Step 4: Show Final Summary**
    if st.session_state["awaiting_response"] == "session_summary":
        st.subheader("📌 **Final Reflection from Your Journaling Session**")
        st.write(st.session_state["chat_history"][-1][1])  # Show only final reflection
        if st.button("Close Session"):
            st.session_state.clear()
            st.rerun()