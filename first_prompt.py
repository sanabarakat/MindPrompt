import random
from firebase_utils import get_firestore_client, get_latest_journal_entry
from openai import OpenAI
import os
from dotenv import load_dotenv
from firebase_admin import firestore

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_api_key)


def generate_first_prompt(user_id):
    db = get_firestore_client()

    print("🔍 Debug: Fetching user's preferred category...")

    # Fetch user preferences
    user_doc = db.collection("users").document(user_id).get()
    if not user_doc.exists:
        print("Debug: User does not exist!")
        return "Welcome! Let's start by writing about how you're feeling today."

    user_data = user_doc.to_dict()
    preferred_category = user_data.get("question_format")

    print(f"✅ Debug: User's preferred category is '{preferred_category}'.")

    # Fetch questions from Firebase based on user's category
    try:
        questions_ref = db.collection("questions_bank").where(
            filter=firestore.FieldFilter("Category", "==", preferred_category)
        ).stream()
        all_questions = [q.to_dict() for q in questions_ref]

        if not all_questions:
            return "There are no questions available in this category. Try choosing a different topic."
    except Exception as e:
        print("🔥 Error retrieving questions from Firebase:", e)
        return "There was an error fetching questions. Please try again."

    # Retrieve previously asked questions
    past_entries = get_latest_journal_entry(user_id)
    asked_questions = {entry["question"] for entry in past_entries}

    print("📌 Debug: Previously asked questions:", asked_questions)

    # **Filter Out Questions That Are Too Generic & Ensure They Are From The User’s Category**
    meaningful_questions = [
        q for q in all_questions
        if len(q["Question"]) > 10 and q["Question"] not in asked_questions
    ]

    print(f"✅ Debug: Filtered meaningful questions ({len(meaningful_questions)})")

    if not meaningful_questions:
        return "It seems you've answered all questions in this category! Let's reflect on today's experiences instead."

    # Randomly select a new question
    selected_question = random.choice(meaningful_questions)["Question"]

    print(f"🎯 Debug: Selected Question: {selected_question}")

    # **Use AI to Personalize the Question**
    personalized_prompt = personalize_prompt(user_id, selected_question, preferred_category)

    return personalized_prompt  # No automatic saving

def personalize_prompt(user_id, question, question_format):
    """Uses AI to refine the question based on the user's past responses."""
    past_entries = get_latest_journal_entry(user_id)
    past_responses = "\n".join(entry["answer"] for entry in past_entries if entry["answer"])[:500]

    print("📌 Debug: Past responses retrieved for personalization:", past_responses)

    prompt = f"""
    You are an expert in personalized self-reflection.
    Your task is to refine a journaling prompt based on the user's past responses.
    
    **User's past reflections:**
    {past_responses}

    Given this context, improve the following question so that:
    - It is deeply thought-provoking.
    - It builds on past themes without being repetitive.
    - It encourages meaningful introspection.

    Original question: "{question}"

    remember that they are journaling for: {question_format}
    """

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You refine journaling prompts for deeper self-reflection."},
                      {"role": "user", "content": prompt}],
            max_tokens=150
        )

        personalized_question = response.choices[0].message.content.strip()
        print(f"🎯 Debug: Personalized Question: {personalized_question}")
        return personalized_question
    except Exception as e:
        print("🔥 Error generating personalized prompt:", e)
        return question  # Fallback to original question if AI fails
