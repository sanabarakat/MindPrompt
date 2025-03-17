import torch
from transformers import BertTokenizer, BertForSequenceClassification
import numpy as np

# Load trained model and tokenizer
MODEL_PATH = "bert-goemotions"
tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()  # Set model to evaluation mode

# Define emotions (same order as training)
emotions = ['admiration', 'amusement', 'anger', 'annoyance', 'approval',
            'caring', 'confusion', 'curiosity', 'desire', 'disappointment',
            'disapproval', 'disgust', 'embarrassment', 'excitement',
            'fear', 'gratitude', 'grief', 'joy', 'love', 'nervousness',
            'optimism', 'pride', 'realization', 'relief', 'remorse',
            'sadness', 'surprise', 'neutral']

# Function to predict emotions for a given text
def predict_emotions(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.sigmoid(logits).squeeze().numpy()  # Apply sigmoid activation
    
    # Get top emotions (above threshold)
    threshold = 0.3  # Adjust threshold if needed
    emotion_probs = {emotions[i]: probs[i] for i in range(len(emotions))}
    top_emotions = {k: v for k, v in emotion_probs.items() if v > threshold}

    return top_emotions if top_emotions else {"neutral": probs[-1]}  # Default to neutral if no strong emotion

# Example usage
if __name__ == "__main__":
    while True:
        text = input("\nEnter a sentence (or type 'exit' to quit): ")
        if text.lower() == "exit":
            break
        predictions = predict_emotions(text)
        print("\nPredicted Emotions:", predictions)
