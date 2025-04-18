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

# sentiment_analysis.py
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline,
)
import torch

# ─────────────── Configuration ───────────────
# Replace with your actual HF repo ID:
HF_MODEL_ID = "sanabar/roberta-goemo-journals"

# pick device
DEVICE = 0 if torch.cuda.is_available() else -1

# ─────────────── Load tokenizer & model ───────────────
print(f"🔍 Loading tokenizer (slow) from: {HF_MODEL_ID}")
tok = AutoTokenizer.from_pretrained(
    HF_MODEL_ID,
    use_fast=False,            # force the pure‑Python tokenizer
    local_files_only=False,    # allow Hub download
)

print(f"🔍 Loading model           from: {HF_MODEL_ID}")
model = AutoModelForSequenceClassification.from_pretrained(
    HF_MODEL_ID,
    local_files_only=False,
)

# ─────────────── Build pipeline ───────────────
sentiment_pipeline = pipeline(
    "text-classification",
    model=model,
    tokenizer=tok,
    function_to_apply="sigmoid",
    return_all_scores=True,
    device=DEVICE,
)

def analyze_sentiment(text: str) -> dict:
    """
    Analyze `text` and return:
    {
        "dominant_emotion": str,
        "top_3_emotions": List[str],
        "emotion_scores": { label_str: float_score, ... }
    }
    """
    scores = sentiment_pipeline(text)[0]
    emotion_scores = {d["label"]: float(d["score"]) for d in scores}

    # Sort and get top 3
    top_3 = sorted(emotion_scores.items(), key=lambda kv: kv[1], reverse=True)[:3]
    top_3_emotions = [label for label, _ in top_3]

    dominant_emotion = top_3_emotions[0]  # First one is still treated as dominant

    return {
        "dominant_emotion": dominant_emotion,
        "top_3_emotions": top_3_emotions,
        "emotion_scores": emotion_scores
    }


# ─────────────── Quick smoke test ───────────────
if __name__ == "__main__":
    sample = "I felt oddly calm but still a bit worried about tomorrow."
    out = analyze_sentiment(sample)
    print("Detected Emotion :", out["dominant_emotion"])
    print("Top 5 Emotions   :")
    for label, score in sorted(
        out["emotion_scores"].items(), key=lambda kv: kv[1], reverse=True
    )[:5]:
        print(f"  {label:12} {score:.3f}")
