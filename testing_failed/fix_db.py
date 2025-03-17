# from firebase_config import init_firebase

# db = init_firebase()

# #add a new collection to the database
# db.collection("test").add({"test": "test"})  # Test connection to Firebase


# # import firebase_admin
# # from firebase_admin import credentials, firestore
# # print(firebase_admin._apps)  # Should show at least one app

# import firebase_admin
# from firebase_admin import credentials, firestore

# if not firebase_admin._apps:
#     try:
#         cred = credentials.Certificate("firebase_credentials.json")  # Make sure the path is correct
#         firebase_admin.initialize_app(cred)
#         print("✅ Firebase initialized successfully!")
#     except Exception as e:
#         print(f"❌ Error initializing Firebase: {e}")

# db = firestore.client()  # Get Firestore client
# print("✅ Firestore connection successful!")

import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

def init_firebase():
    if not firebase_admin._apps:  # Prevent duplicate initialization
        cred = credentials.Certificate("firebase_credentials.json")
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firebase()

# Read the Excel file (adjust the filename and sheet name as needed)
df = pd.read_excel('questions_bank.xlsx', sheet_name='Sheet1')

# Name of the new Firestore collection
collection_name = "questions_bank"

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    # Convert the row to a dictionary
    data_dict = row.to_dict()
    
    # Add the dictionary as a new document in the collection
    db.collection(collection_name).add(data_dict)
    
print("Data has been successfully added to Firestore.")
