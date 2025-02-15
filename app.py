import streamlit as st
import datetime
import uuid  # For generating unique User IDs
from firebase_config import init_firebase
from model import generate_personalized_prompt  

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
        age = st.number_input("Age", min_value=13, max_value=100, step=1)
        gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
        occupation = st.text_input("Occupation")
        personality = st.radio("Are you more of an introvert or extrovert?", ["Introvert", "Extrovert"])
        hobbies = st.text_area("Enter your hobbies (comma-separated):")
        journaling_freq = st.selectbox("How often do you journal?", ["Daily", "Weekly", "Occasionally"])

        if st.button("Create Account"):
            if name.strip():
                user_id = str(uuid.uuid4())  # Generate a unique User ID
                user_data = {
                    "user_id": user_id,
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "occupation": occupation,
                    "personality": personality,
                    "hobbies": hobbies.split(","),
                    "frequency": journaling_freq
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

#Journaling Section (Only Show if Logged In)
if "user_id" in st.session_state:
    st.subheader(f"🖊️ Welcome, {st.session_state['name']}! Start Journaling")

    # Add a session state variable to store the prompt
    if "generated_prompt" not in st.session_state:
        st.session_state["generated_prompt"] = None  # Initialize it

    if st.button("Generate AI Prompt"):
        st.session_state["generated_prompt"] = generate_personalized_prompt(st.session_state["user_id"])  # Generate only on click

    # Display the prompt only if it exists
    if st.session_state["generated_prompt"]:
        st.write(f"💡 **Personalized Journaling Prompt:**\n\n{st.session_state['generated_prompt']}")
    
    journal_entry = st.text_area("Write your thoughts here:")


    if st.button("Save Entry"):
        if journal_entry.strip():
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
            
            journal_data = {
                "user_id": st.session_state["user_id"],
                "entry": journal_entry,
                "timestamp": timestamp  
            }
            db.collection("journals").add(journal_data)
            st.success(f"✅ Journal entry saved! ({timestamp})")
        else:
            st.warning("⚠️ Please write something before saving.")
