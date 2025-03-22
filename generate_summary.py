from openai import OpenAI
import os
from dotenv import load_dotenv
import openai
from firebase_utils import retrieve_user_data

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_api_key)

def generate_session_summary(session_entries, user_id):
    """Generates a final session summary based on the user's journal entries."""
    user_data, past_entries = retrieve_user_data(user_id)
    journal_content = "\n".join(entry["answer"] for entry in session_entries if entry["answer"])

    prompt = f"""
    The user has just completed a journaling session. Their responses are:

    {journal_content}

    in 3-4 sentences, Please generate a **thoughtful summary** that includes:
    - Key emotions and themes from their writing.
    - Insights they seem to have gained.
    - A motivating closing remark to encourage future journaling.

    remember that the user is a {user_data['occupation']} who journals to {user_data['question_format']} and identifies as a {user_data['personality']}. they like to do {user_data['hobbies']} in their free time so maybe use that in your suggestions but make it useful and relevant.
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You generate insightful journal summaries."},
                  {"role": "user", "content": prompt}],
        max_tokens=200
    )

    return response.choices[0].message.content.strip()
