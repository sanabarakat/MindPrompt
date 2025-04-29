# from transformers import pipeline

# # Load EmoBERTa model from Hugging Face
# sentiment_pipeline = pipeline("text-classification", model="tae898/emoberta-large", return_all_scores=True, framework="pt")

# def analyze_sentiment(text):
#     """Analyze sentiment using EmoBERTa and return scores."""
#     results = sentiment_pipeline(text)
    
#     # Extract scores for emotions
#     emotion_scores = {res["label"]: res["score"] for res in results[0]}
    
#     # Get the dominant emotion
#     dominant_emotion = max(emotion_scores, key=emotion_scores.get)

#     return {
#         "dominant_emotion": dominant_emotion,
#         "emotion_scores": emotion_scores
#     }

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline,
)
import torch
from huggingface_hub import login
import streamlit as st

login(token=st.secrets["HUGGINGFACE_TOKEN"])

tokenizer = AutoTokenizer.from_pretrained("sanabar/roberta-goemo-journals")
model = AutoModelForSequenceClassification.from_pretrained("sanabar/roberta-goemo-journals")

# ─────────────── Build pipeline ───────────────
sentiment_pipeline = pipeline(
    "text-classification",
    model=model,
    tokenizer=tokenizer,
    function_to_apply="sigmoid",
    return_all_scores=True,
    )

def analyze_sentiment(text: str) -> dict:
    scores = sentiment_pipeline(text)[0]
    emotion_scores = {d["label"]: float(d["score"]) for d in scores}
    top_3 = sorted(emotion_scores.items(), key=lambda kv: kv[1], reverse=True)[:3]
    top_3_emotions = [label for label, _ in top_3]
    dominant_emotion = top_3_emotions[0]
    return {
        "dominant_emotion": dominant_emotion,
        "top_3_emotions": top_3_emotions,
        "emotion_scores": emotion_scores
    }

