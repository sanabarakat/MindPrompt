from openai import OpenAI
import os
from dotenv import load_dotenv
import openai
from firebase_utils import get_latest_journal_entry

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_api_key)

def generate_followup_prompt(user_id, user_feeling):
    """Generates a follow-up question based on the user's latest journal entry."""
    last_entry = get_latest_journal_entry(user_id)

    prompt = f"""
    the user is feeling this way:
    "{user_feeling}"
    and they wrote: 
    "{last_entry}"

    Now, generate a thoughtful follow-up question to help them reflect deeper.
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are a reflective AI journaling assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=100
    )

    return response.choices[0].message.content.strip()
