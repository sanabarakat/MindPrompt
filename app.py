import streamlit as st
import datetime
import uuid  
from firebase_config import init_firebase
from model import generate_personalized_prompt
from sentiment_analysis import analyze_sentiment  
from model_response import generate_reply


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
        reason = st.selectbox("What would you say is the main reason you want to journal?", ["Self-reflection", "Mental health", "Productivity", "Creativity", "Tracking personal growth", "Practice Gratitude", "Other"])
        expression = st.selectbox("How do you usually express yourself?", ["Writing", "Drawing", "Talking", "Keeping it to yourself", "Other"])
        stress = st.radio("Do you experience frequent stress or anxiety?", ["Yes", "No", "Sometimes"])
        stress_reason = st.selectbox("What stresses you out the most?", ["Work", "Relationships", "Health", "Family", "Personal Issues and Thoughts", "Finances", "Prefer not to say", "Other"])
        question_format = st.radio("What format of journaling questions do you prefer?", ["Open-ended questions", "Structured reflection prompts"])

        # **GDPR Agreement Checkbox**
        gdpr_agreement = st.checkbox(
            'I agree to the [Terms & Conditions](https://www.consilium.europa.eu/en/policies/data-protection-regulation/#:~:text=The%20GDPR%20lists%20the%20rights,his%20or%20her%20personal%20data)',
            help="You must agree to our terms to create an account."
        )

        if st.button("Create Account"):
            if not gdpr_agreement:
                st.warning("⚠️ You must agree to the Terms & Conditions to continue.")
            elif name.strip():
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
                st.warning("⚠️ Please enter your name.")


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
        st.session_state["awaiting_response"] = "feeling_check"

    # **Display Chat History**
    for role, message in st.session_state["chat_history"]:
        st.write(f"**{role}:** {message}")

    # **Step 1: Ask User How They Feel**
    if st.session_state["awaiting_response"] == "feeling_check":
        user_feeling = st.text_area("How are you feeling today?")
        if st.button("Submit Feeling"):
            if user_feeling.strip():
                st.session_state["chat_history"].append(("User", user_feeling))
                st.session_state["latest_feeling"] = user_feeling

                # **Generate a short AI response to their feeling**
                ai_response = f"Thank you for sharing. It's important to acknowledge our emotions. I hear that what you're feeling. Let's explore this further!"
                st.session_state["chat_history"].append(("AI", ai_response))

                # **Generate first journaling prompt**
                prompt_response = generate_personalized_prompt(st.session_state["user_id"], user_feeling)
                st.session_state["chat_history"].append(("AI", prompt_response))

                st.session_state["awaiting_response"] = "user_journal_entry"
                st.rerun()

    # **Step 2: Display the Generated Prompt & Ask for Journal Entry**
    if st.session_state["awaiting_response"] == "user_journal_entry":
        st.write(f"💡 **Journaling Prompt:**\n\n{st.session_state['chat_history'][-1][1]}")  # Show last AI-generated question
        
        journal_entry = st.text_area("Write your journal entry:")
        
        if st.button("Submit Entry"):
            if journal_entry.strip():
                sentiment = analyze_sentiment(journal_entry)
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
                
                # **Save response in database**
                journal_data = {
                    "user_id": st.session_state["user_id"],
                    "feeling": st.session_state["latest_feeling"],
                    "prompt": st.session_state["chat_history"][-1][1],  # Store last AI question
                    "entry": journal_entry,
                    "sentiment": sentiment,
                    "timestamp": timestamp  
                }
                db.collection("journals").add(journal_data)

                # **AI Generates a Thoughtful Response**
                ai_feedback = generate_reply(st.session_state["user_id"], journal_entry)
                
                # **Append responses to chat history**
                st.session_state["chat_history"].append(("User", journal_entry))
                st.session_state["chat_history"].append(("AI", ai_feedback))  # AI-generated supportive message

                # Move to next step: Ask if they want another question
                st.session_state["awaiting_response"] = "ask_next_question"
                st.rerun()


    # **Step 3: Ask If User Wants Another Question**
    if st.session_state["awaiting_response"] == "ask_next_question":
        # **Display AI’s response before moving on**
        st.write(f"🤖 **AI:** {st.session_state['chat_history'][-1][1]}")

        user_choice = st.radio("Would you like another question?", ["Yes", "No"])
        
        if st.button("Continue"):
            if user_choice == "Yes":
                prompt_response = generate_personalized_prompt(st.session_state["user_id"], st.session_state["latest_feeling"])
                st.session_state["chat_history"].append(("AI", prompt_response))
                st.session_state["awaiting_response"] = "user_journal_entry"
            else:
                st.session_state["chat_history"].append(("AI", "Thank you for journaling today! See you next time."))
                st.session_state["awaiting_response"] = None
            st.rerun()
