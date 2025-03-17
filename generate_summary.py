from openai import OpenAI
import os
from dotenv import load_dotenv
import openai

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_api_key)

def generate_session_summary(session_entries):
    """Generates a final session summary based on the user's journal entries."""
    journal_content = "\n".join(entry["answer"] for entry in session_entries if entry["answer"])

    prompt = f"""
    The user has just completed a journaling session. Their responses are:

    {journal_content}

    in 3-4 sentences, Please generate a **thoughtful summary** that includes:
    - Key emotions and themes from their writing.
    - Insights they seem to have gained.
    - A motivating closing remark to encourage future journaling.
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You generate insightful journal summaries."},
                  {"role": "user", "content": prompt}],
        max_tokens=200
    )

    return response.choices[0].message.content.strip()
