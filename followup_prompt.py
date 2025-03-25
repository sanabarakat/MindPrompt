from openai import OpenAI
import os
from dotenv import load_dotenv
import openai
from firebase_utils import get_latest_journal_entry, retrieve_user_data
import streamlit as st
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]

openai_client = OpenAI(api_key=openai.api_key)

def generate_followup_prompt(user_id, user_feeling, session_entries):
    """Generates a follow-up question based on the user's latest journal entry."""
    last_entry = get_latest_journal_entry(user_id)
    user_data, past_entries = retrieve_user_data(user_id)


    # Compile past journal responses dynamically
    recent_entries = " | ".join(entry["entry"] for entry in session_entries if "entry" in entry)

    prompt = f"""
    You are a compassionate AI journaling assistant helping {user_data['name']} explore their thoughts and emotions.

    remember that they usually journal in the {user_data['time']} for {user_data['question_format']} and they work as a {user_data['occupation']}. they identify their personality as a {user_data['personality']}. 
    and the following is their hobby: {user_data['hobbies']}. they usually express themselves through {user_data['expression']}. they experience {user_data['stress']} stress and the main reason is {user_data['stress_reason']}.
    
    The user has shared their current feelings: "{user_feeling}".

    Recent reflections from this session:
    {recent_entries}

    Past Journal Entries from previous sessions:
    {past_entries}

    Using these reflections, generate a **NEW AND UNIQUE** journaling question that helps them **dig deeper** into their thoughts.
    Ensure this question is NOT repetitive, expands on previous themes, and encourages further self-exploration.
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a thoughtful AI journaling assistant helping users self-reflect deeply. with one question at a time."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
    )

    return response.choices[0].message.content.strip()
