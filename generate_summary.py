import os
from dotenv import load_dotenv
import openai

load_dotenv() 

openai.api_key = os.getenv("OPENAI_API_KEY")  

def generate_session_summary(session_entries):
    """Generate a final session reflection based on the user's responses."""

    journal_content = "\n".join(entry["entry"] for entry in session_entries if "entry" in entry)

    prompt = f"""
    You are a compassionate AI journaling assistant.
    
    The user has just completed a journaling session. Here are their entries:
    
    {journal_content}
    
    Please generate a **thoughtful and encouraging summary** that highlights in 3-4 sentences:
    - Key emotions and patterns from their writing.
    - Any insights they seem to have gained.
    - A gentle, motivating closing remark to leave them feeling empowered.
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are a reflective AI journaling assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=200
    )

    return response.choices[0].message.content.strip()


