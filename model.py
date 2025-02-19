import os
import openai
from retrieval import retrieve_user_data
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_personalized_prompt(user_id, user_feeling):
    """Fetch user data & generate a personalized journaling prompt."""
    user_data, past_entries = retrieve_user_data(user_id)

    if not user_data:
        return "Welcome! Since you're new, start by writing about how you're feeling today."

    # Format user preferences
    hobbies = ", ".join(user_data.get("hobbies", [])) or "various interests"
    personality = user_data.get("personality", "a unique perspective")
    stress_level = user_data.get("stress", "uncertain")
    stress_reason = user_data.get("stress_reason", "various challenges")
    journaling_frequency = user_data.get("journaling_frequency", "Occasionally")
    journaling_time = user_data.get("journaling_time", "unspecified times")
    journaling_reason = user_data.get("journaling_reason", "self-reflection")
    expression_preference = user_data.get("expression_preference", "writing")
    question_format = user_data.get("question_format", "open-ended questions")

    # Format past journal entries
    past_journals = " | ".join(past_entries) if past_entries else "No past entries found."

    # Construct an intelligent prompt for ChatGPT
    prompt = f"""
    You are an AI journaling assistant. Generate a {question_format} journaling prompt for {user_data['name']},
    who is a {personality} and expresses themselves best through {expression_preference}. 
    They usually journal {journaling_frequency} in the {journaling_time}, mainly for {journaling_reason}. 
    They enjoy hobbies such as {hobbies}, and experience stress {stress_level} due to {stress_reason}. 
    
    The user has shared how they are feeling today: "{user_feeling}".
    
    This is what they've journaled in the past so take it into consideration to reach a deeper level of understanding:
    {past_journals}
    
    Generate a thought-provoking yet approachable question that encourages self-reflection 
    and connects with their personal interests and current emotions.
    """

    # Get AI-generated prompt
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are an intelligent journaling assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=200
    )
    
    prompt_question = response.choices[0].message.content.strip()

    # Generate a response based on the user's entry
    motivation_prompt = f"""
    Based on the user's past journaling experience and personal profile, generate a short but uplifting motivational message.
    Ensure the message is encouraging and aligns with their personality type and journaling habits.
    """

    motivation_response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a supportive AI journaling assistant."},
            {"role": "user", "content": motivation_prompt}
        ],
        max_tokens=100
    )

    motivation_message = motivation_response.choices[0].message.content.strip()

    return {prompt_question}
