import streamlit as st
import firebase_admin
from firebase_config import init_firebase
from testing_failed.test_huggingface import generate_prompt  

# Initialize Firebase
db = init_firebase()

st.title("MindPrompt")
st.header("Where AI meets optimal self-reflection!")

# User input for journaling
journal_entry = st.text_area("Write your journal entry here:")

# Generate AI-powered journaling prompts
if st.button("Generate AI Prompt"):
    prompt = generate_prompt()
    st.write("Suggested Prompt:", prompt)

# Save the journal entry to Firebase Firestore
if st.button("Save Entry"):
    if journal_entry.strip():
        db.collection("journals").add({"entry": journal_entry})
        st.success("Journal entry saved successfully!")
    else:
        st.warning("Please write something before saving.")
