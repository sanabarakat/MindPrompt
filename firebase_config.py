import firebase_admin
from firebase_admin import credentials, firestore

def init_firebase():
    # Check if a Firebase app has already been initialized
    if not firebase_admin._apps:
        
        # Initialize the Firebase app using credentials from a JSON file.
        cred = credentials.Certificate('credentials.json')
        firebase_admin.initialize_app(cred)
    
    # Return the Firestore client
    db = firestore.client()
    return db