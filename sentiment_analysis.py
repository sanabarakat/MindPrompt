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

# # Test the function
# if __name__ == "__main__":
#     sample_text = "I'm feeling really happy and grateful today!"
#     sentiment = analyze_sentiment(sample_text)
#     print(f"Detected Emotion: {sentiment['dominant_emotion']}")
#     print(f"Emotion Scores: {sentiment['emotion_scores']}")

from transformers import pipeline

# ──────────────── Configuration ────────────────
# Replace with your actual Hub repo ID
HF_MODEL_ID = "sanabar/roberta-goemo-journal-adapted"

# ─────────────── Load the fine‑tuned model ───────────────
# multi‑label head uses sigmoid; return_all_scores gives all 28 emotions
sentiment_pipeline = pipeline(
    "text-classification",
    model=HF_MODEL_ID,
    function_to_apply="sigmoid",
    return_all_scores=True,
    framework="pt",
)

def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment/emotion of `text` using the fine‑tuned GoEmotions‑journal model.

    Returns:
      {
        "dominant_emotion": <label str>,
        "emotion_scores" : { label_str: float_score, … }
      }
    """
    # pipeline returns a list of lists (one inner list per input string)
    scores = sentiment_pipeline(text)[0]

    # convert to {label: score}
    emotion_scores = {d["label"]: float(d["score"]) for d in scores}

    # pick the highest‑scoring emotion
    dominant_emotion = max(emotion_scores, key=emotion_scores.get)

    return {
        "dominant_emotion": dominant_emotion,
        "emotion_scores": emotion_scores,
    }


# ─────────────── Quick smoke‑test ───────────────
if __name__ == "__main__":
    sample = "I'm feeling really happy and grateful today!"
    out = analyze_sentiment(sample)
    print("Detected Emotion :", out["dominant_emotion"])
    print("Top 5 Emotions   :")
    for label, score in sorted(out["emotion_scores"].items(), key=lambda kv: kv[1], reverse=True)[:5]:
        print(f"  {label:12} {score:.3f}")
