import random
from firebase_utils import get_firestore_client, get_latest_journal_entry
from openai import OpenAI
import streamlit as st
from firebase_admin import firestore
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]
openai_client = OpenAI(api_key=openai.api_key)

def generate_first_prompt(user_id):
    db = get_firestore_client()

    # Fetch user preferences
    user_doc = db.collection("users").document(user_id).get()
    if not user_doc.exists:
        return "Welcome! Let's start by writing about how you're feeling today."

    user_data = user_doc.to_dict()
    preferred_categories = user_data.get("question_format", [])
    hobbies = ", ".join(user_data.get("hobbies", []))

    # Pick one preferred category randomly
    if isinstance(preferred_categories, list) and preferred_categories:
        preferred_category = random.choice(preferred_categories)
    else:
        preferred_category = preferred_categories

    # Fetch questions from Firebase based on selected category
    try:
        questions_ref = db.collection("questions_bank").where(
            filter=firestore.FieldFilter("Category", "==", preferred_category)
        ).stream()
        all_questions = [q.to_dict() for q in questions_ref]
        if not all_questions:
            return "There are no questions available in this category. Try choosing a different topic."
    except Exception:
        return "There was an error fetching questions. Please try again."

    # Filter out already asked questions
    past_entries = get_latest_journal_entry(user_id)
    asked_questions = {entry["question"] for entry in past_entries}
    meaningful_questions = [
        q for q in all_questions
        if len(q["Question"]) > 10 and q["Question"] not in asked_questions
    ]

    if not meaningful_questions:
        return "It seems you've answered all questions in this category! Let's reflect on today's experiences instead."

    selected_question = random.choice(meaningful_questions)["Question"]

    adapted_prompt = personalize_prompt(user_id, selected_question, preferred_category, hobbies)

    return adapted_prompt, selected_question   

def personalize_prompt(user_id, question, question_format, hobbies):
    """Uses AI to refine the question based on the user's past responses, goals, and hobbies."""
    past_entries = get_latest_journal_entry(user_id)
    past_responses = "\n".join(entry["answer"] for entry in past_entries if entry["answer"])[:500]

    prompt = f"""
    You are an expert in personalized journaling and psychology-based reflection.
    Your task is to refine a journaling question so that it supports the user's goals and personal interests.

    Journaling goal: {question_format}
    User hobbies: {hobbies}
    Past reflections: {past_responses}

    Refine the following journaling question to be:
    - Deeply thought-provoking
    - Relevant to the user's journaling goal and hobbies
    - Inspired by previous reflections (if available)
    - Focused on inner growth, gratitude, or stress relief (as appropriate)

    Original question: "{question}"

    give me a short question and only give me the pure question without any other information
    """

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You help people reflect more deeply by enhancing journaling prompts based on their personal goals and interests."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=180
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return question
