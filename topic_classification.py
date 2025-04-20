# topic_classification.py
from transformers import pipeline

# Load topic classification pipeline
topic_pipeline = pipeline(
    "text-classification",
    model="sanabar/roberta-topic-head",  # use your fine-tuned HF model
    function_to_apply="sigmoid",
    return_all_scores=True,
    top_k=None,
    framework="pt"
)

def classify_topics(text):

    threshold = 0.3
    top_k = 2
    scores = topic_pipeline(text)[0]
    
    # Filter by score threshold
    filtered = [d["label"] for d in scores if d["score"] >= threshold]
    
    # Optional: ensure at least one topic is returned
    if not filtered:
        top = sorted(scores, key=lambda x: x["score"], reverse=True)[:top_k]
        filtered = [d["label"] for d in top]
    
    return filtered
