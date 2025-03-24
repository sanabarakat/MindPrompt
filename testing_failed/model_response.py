import os
import openai
from testing_failed.retrieval import retrieve_user_data
from dotenv import load_dotenv
from openai import OpenAI

import streamlit as st

openai_client = OpenAI(api_key=st.secrets["openai"]["api_key"])

def generate_reply(user_id, user_entry):
    """Generate a supportive AI response based on the user's journal entry."""
    user_data, past_entries = retrieve_user_data(user_id)

    if not user_data:
        return "Thank you for sharing your thoughts. You're taking a great step towards self-reflection!"

    # Format user preferences
    hobbies = ", ".join(user_data.get("hobbies", [])) or "various interests"
    personality = user_data.get("personality", "a unique perspective")
    stress_level = user_data.get("stress", "uncertain")
    stress_reason = user_data.get("stress_reason", "various challenges")
    journaling_reason = user_data.get("journaling_reason", "self-reflection")

    # Format past journal entries
    past_journals = " | ".join(past_entries) if past_entries else "No past entries found."

    # Construct AI prompt for supportive response
    ai_reply_prompt = f"""
    You are an empathetic AI journaling assistant. The user has just written a journal entry, and your task is to generate a thoughtful response.
    - If the user seems stressed or anxious, provide **a calming or motivational message**.
    - If they are feeling positive, **encourage them to build on this energy**.
    - If they mention a struggle, **suggest a simple coping strategy or an activity that aligns with their hobbies**.
    
    User Profile:
    - Name: {user_data['name']}
    - Personality: {personality}
    - Hobbies: {hobbies}
    - Journaling Reason: {journaling_reason}
    - Stress Level: {stress_level} (due to {stress_reason})
    
    Past Journal Entries:
    {past_journals}

    User's Latest Journal Entry:
    "{user_entry}"

    Generate a **short** but **meaningful** AI response, keeping the tone **supportive and encouraging**.
    """

    # Get AI-generated reply
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are a kind and encouraging AI assistant."},
                  {"role": "user", "content": ai_reply_prompt}],
        max_tokens=150
    )
    
    reply = response.choices[0].message.content.strip()
    
    return reply