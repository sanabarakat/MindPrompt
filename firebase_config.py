import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

def init_firebase():
    if not firebase_admin._apps:
        cred_dict = dict(st.secrets["FIREBASE_CREDENTIALS"])
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    return firestore.client()


db = init_firebase()
