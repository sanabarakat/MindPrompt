# import firebase_admin
# from firebase_admin import firestore

# # Initialize Firestore DB
# db = firestore.client()

# def retrieve_user_data(user_id):
#     """Retrieve user profile data and past journal entries."""
#     user_ref = db.collection("users").document(user_id)
#     user_doc = user_ref.get()
    
#     if user_doc.exists:
#         user_data = user_doc.to_dict()
#     else:
#         return None, []

#     # Retrieve past journal entries
#     journals_ref = db.collection("journals").where("user_id", "==", user_id).stream()
    
#     past_entries = []
#     for journal in journals_ref:
#         journal_data = journal.to_dict()
        
#         # Only add journal entries that contain an "entry"
#         if "entry" in journal_data:
#             past_entries.append(journal_data["entry"])
#         else:
#             past_entries.append("[No journal entry recorded]")  # Avoid KeyError

#     return user_data, past_entries


from firebase_config import init_firebase

def get_firestore_client():
    """Ensure Firebase is initialized before getting Firestore client."""
    return init_firebase()

def retrieve_user_data(user_id):
    """Retrieve user data and past journal entries from Firestore."""
    db = get_firestore_client()  # Ensure Firebase is initialized

    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        return None, []

    user_data = user_doc.to_dict()

    # Retrieve past journal entries
    journals_ref = db.collection("users").document(user_id).collection("journals").stream()
    past_entries = [{"question": j.to_dict().get("question"), "answer": j.to_dict().get("answer")} for j in journals_ref]

    return user_data, past_entries

