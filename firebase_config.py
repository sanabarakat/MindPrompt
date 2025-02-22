# import firebase_admin
# from firebase_admin import credentials, firestore

# def init_firebase():
#     cred = credentials.Certificate("firebase_credentials.json")
#     firebase_admin.initialize_app(cred)
#     db = firestore.client()
#     return db

import firebase_admin
from firebase_admin import credentials, firestore

def init_firebase():
    if not firebase_admin._apps:  # Prevent duplicate initialization
        cred = credentials.Certificate("firebase_credentials.json")
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firebase()
