from transformers import pipeline

topic_pipeline = pipeline(
    "text-classification",
    model="sanabar/roberta-topic-head",  
    function_to_apply="sigmoid",
    return_all_scores=True,
    top_k=None,
    framework="pt"
)

def classify_topics(text):

    threshold = 0.3
    top_k = 2
    scores = topic_pipeline(text)[0]
    
    filtered = [d["label"] for d in scores if d["score"] >= threshold]
    
    if not filtered:
        top = sorted(scores, key=lambda x: x["score"], reverse=True)[:top_k]
        filtered = [d["label"] for d in top]
    
    return filtered
