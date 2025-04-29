from firebase_admin import firestore
from firebase_config import init_firebase

# Initialize Firebase
try:
    db = init_firebase()
except Exception as e:
    print(f"Firebase Initialization Error: {e}")

def get_firestore_client():
    return db

# def get_latest_journal_entry(user_id):
#     """Retrieve all past journal entries for a user."""
#     try:
#         journals_ref = db.collection("journals").where("user_id", "==", user_id)\
#             .order_by("timestamp", direction=firestore.Query.DESCENDING).stream()

#         entries = []
#         for journal in journals_ref:
#             session_entries = journal.to_dict().get("entries", [])
#             entries.extend(session_entries)  # Collect all past questions & answers

#         return entries if entries else None  # Return full list of past entries

#     except Exception as e:
#         print(f"Firestore Query Error: {e}")
#         return None

def get_latest_journal_entry(user_id):
    """Retrieve past journal entries and attach the session's timestamp."""
    try:

        journals_ref = db.collection("journals").stream()  
        entries = []

        for journal in journals_ref:
            journal_data = journal.to_dict()

            if journal_data.get("user_id") != user_id:
                continue

            session_timestamp = journal_data.get("timestamp")

            for entry in journal_data.get("entries", []):
                entry["timestamp"] = session_timestamp  
                entries.append(entry)

        print(f"Retrieved {len(entries)} journal entries for user {user_id}")
        return entries if entries else []

    except Exception as e:
        print(f"Firestore Query Error: {e}")
        return None


def save_journal_entry(user_id, session_entries):
    """Save the entire journal session in the correct structured format."""
    try:
        structured_data = {
            "user_id": user_id,
            "entries": [],
            "timestamp": firestore.SERVER_TIMESTAMP
        }

        for entry in session_entries:
            structured_data["entries"].append({
                "question": entry.get("question", ""),
                "answer": entry.get("answer", ""),
                "topics": entry.get("topics", []),
                "sentiment": {
                    "dominant_emotion": entry.get("sentiment", {}).get("dominant_emotion", ""),
                    "top_3_emotions": entry.get("sentiment", {}).get("top_3_emotions", []),
                }
            })

        db.collection("journals").add(structured_data)
        print("Journal session saved successfully!")
    except Exception as e:
        print(f"Firestore Save Error: {e}")


def retrieve_user_data(user_id):
    """Retrieve user data and past journal entries from Firestore."""
    db = get_firestore_client()  

    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        return None, []

    user_data = user_doc.to_dict()

    journals_ref = db.collection("users").document(user_id).collection("journals").stream()
    past_entries = [{"question": j.to_dict().get("question"), "answer": j.to_dict().get("answer")} for j in journals_ref]

    return user_data, past_entries

def delete_user_data(user_id):
    db = get_firestore_client()  

    try:
        db.collection("users").document(user_id).delete()

        journals_ref = db.collection("journals").where("user_id", "==", user_id).stream()
        for journal in journals_ref:
            journal.reference.delete()

        print(f"User data and journal entries for {user_id} deleted successfully.")
    except Exception as e:
        print(f"Error deleting user data: {e}")


