from openai import OpenAI
from firebase_utils import get_latest_journal_entry, retrieve_user_data
import streamlit as st
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]
openai_client = OpenAI(api_key=openai.api_key)

def generate_followup_prompt(user_id, user_feeling, session_entries):
    """Generates a unique follow-up question to deepen reflection."""

    # Load user data and past entries
    user_data, past_entries = retrieve_user_data(user_id)

    # Extract previous questions and responses from current session
    previous_questions = [entry["question"] for entry in session_entries if entry.get("question")]
    previous_responses = [entry["answer"] for entry in session_entries if entry.get("answer")]
    
    # Format previous questions as a block
    questions_block = "\n- " + "\n- ".join(previous_questions) if previous_questions else "None yet"

    # Format session responses
    session_summary = "\n".join(f"{q}\n→ {a}" for q, a in zip(previous_questions, previous_responses) if q and a)

    # Build the prompt
    prompt = f"""
You are a compassionate AI journaling assistant helping {user_data['name']} reflect.

Context:
- Journals in the {user_data['time']}
- Journaling Goal(s): {", ".join(user_data.get("question_format", []))}
- Works as a {user_data['occupation']}
- Personality: {user_data['personality']}
- Hobbies: {user_data['hobbies']}
- Expresses through: {user_data['expression']}
- Stress: {user_data['stress']} (due to {user_data['stress_reason']})

Current feeling: "{user_feeling}"

Session Reflections so far:
{session_summary}

Previous Questions in this session:
{questions_block}

Your task:
Generate a new, **non-repetitive**, personalized journaling question that builds on the user’s journey so far and encourages deeper emotional insight. Avoid rephrasing previous questions.
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a thoughtful AI journaling assistant. Respond only with one unique, deep question."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
    )

    return response.choices[0].message.content.strip()
