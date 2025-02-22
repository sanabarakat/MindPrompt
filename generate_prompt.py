import os
from dotenv import load_dotenv
import openai

load_dotenv()  

openai.api_key = os.getenv("OPENAI_API_KEY") 
from retrieval import retrieve_user_data

def generate_personalized_prompt(user_id, user_feeling, session_entries):
    """Generate a unique, evolving journaling prompt based on past reflections."""
    
    user_data, past_entries = retrieve_user_data(user_id)

    if not user_data:
        return "Welcome! Since you're new, start by writing about how you're feeling today."

    # Compile past journal responses dynamically
    recent_entries = " | ".join(entry["entry"] for entry in session_entries if "entry" in entry)

    # Construct an intelligent prompt for ChatGPT
    prompt = f"""
    You are a compassionate AI journaling assistant helping {user_data['name']} explore their thoughts and emotions.
    
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
            {"role": "system", "content": "You are a thoughtful AI journaling assistant helping users self-reflect deeply."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
    )

    return response.choices[0].message.content.strip()



