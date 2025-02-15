import firebase_admin
from firebase_admin import credentials, firestore
from firebase_config import init_firebase

db = init_firebase()

def retrieve_user_data(user_id):
    """Fetch user profile and past journal entries from Firebase"""
    user_doc = db.collection("users").document(user_id).get()
    journals_ref = db.collection("journals").where("user_id", "==", user_id).order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).stream()

    if user_doc.exists:
        user_data = user_doc.to_dict()
        past_entries = [journal.to_dict()["entry"] for journal in journals_ref]
        
        return user_data, past_entries
    else:
        return None, None
