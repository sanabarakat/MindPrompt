from transformers import pipeline

# Load EmoBERTa model from Hugging Face
sentiment_pipeline = pipeline("text-classification", model="tae898/emoberta-large", return_all_scores=True)

def analyze_sentiment(text):
    """Analyze sentiment using EmoBERTa and return scores."""
    results = sentiment_pipeline(text)
    
    # Extract scores for emotions
    emotion_scores = {res["label"]: res["score"] for res in results[0]}
    
    # Get the dominant emotion
    dominant_emotion = max(emotion_scores, key=emotion_scores.get)

    return {
        "dominant_emotion": dominant_emotion,
        "emotion_scores": emotion_scores
    }

# Test the function
if __name__ == "__main__":
    sample_text = "I'm feeling really happy and grateful today!"
    sentiment = analyze_sentiment(sample_text)
    print(f"Detected Emotion: {sentiment['dominant_emotion']}")
    print(f"Emotion Scores: {sentiment['emotion_scores']}")
