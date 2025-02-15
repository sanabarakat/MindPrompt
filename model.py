import openai
from retrieval import retrieve_user_data

openai.api_key = "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"  

def generate_personalized_prompt(user_id):
    """Fetch user data & generate a personalized journaling prompt."""
    user_data, past_entries = retrieve_user_data(user_id)

    if not user_data:
        return "Welcome! Since you're new, start by writing about how you're feeling today."

    # Format user preferences
    hobbies = ", ".join(user_data.get("hobbies", []))
    personality = user_data.get("personality", "Unknown")
    journaling_freq = user_data.get("frequency", "Occasionally")

    # Format past journal entries
    past_journals = " | ".join(past_entries) if past_entries else "No past entries found."

    # Construct LLM prompt
    prompt = f"""
    You are an AI journaling assistant. Generate a thoughtful journaling prompt for a user based on their profile and past journal entries.

    User Profile:
    - Name: {user_data['name']}
    - Age: {user_data['age']}
    - Personality: {personality}
    - Hobbies: {hobbies}
    - Journaling Frequency: {journaling_freq}

    Past Journal Entries:
    {past_journals}

    Generate a question that helps the user reflect based on their interests and past writing.
    """
    
    # Get AI-generated prompt
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are an intelligent journaling assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=200
    )
    
    return response.choices[0].message.content.strip()
