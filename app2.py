import streamlit as st
import datetime
import uuid  
from firebase_config import init_firebase
import firebase_admin


# Initialize Firebase
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
                              ["Self-reflection", "Mental health", "Productivity", "Creativity", 
                               "Tracking personal growth", "Practice Gratitude", "Other"])
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




