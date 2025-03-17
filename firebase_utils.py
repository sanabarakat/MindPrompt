from firebase_admin import firestore
from firebase_config import init_firebase

# Initialize Firebase
try:
    db = init_firebase()
except Exception as e:
    print(f"🔥 Firebase Initialization Error: {e}")

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
#         print(f"🔥 Firestore Query Error: {e}")
#         return None

def get_latest_journal_entry(user_id):
    """Retrieve past journal entries and attach the session's timestamp."""
    try:
        print(f"🛠️ Debug: get_latest_journal_entry called with user_id: {user_id}")

        journals_ref = db.collection("journals").stream()  # Fetch all journal sessions
        entries = []

        for journal in journals_ref:
            journal_data = journal.to_dict()

            # **Skip if user_id does not match**
            if journal_data.get("user_id") != user_id:
                continue

            # **Get session timestamp (from Firestore)**
            session_timestamp = journal_data.get("timestamp")

            # **Attach timestamp to each journal entry**
            for entry in journal_data.get("entries", []):
                entry["timestamp"] = session_timestamp  # Assign session timestamp
                entries.append(entry)

        print(f"✅ Retrieved {len(entries)} journal entries for user {user_id}")
        return entries if entries else None  # Return full list of past entries

    except Exception as e:
        print(f"🔥 Firestore Query Error: {e}")
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
                "sentiment": entry.get("sentiment", "")  # Ensure sentiment is stored
            })

        db.collection("journals").add(structured_data)
        print("✅ Journal session saved successfully!")
    except Exception as e:
        print(f"🔥 Firestore Save Error: {e}")


