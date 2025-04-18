import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from wordcloud import WordCloud
from transformers import pipeline
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

# —                     Setup NLTK                ————
nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("omw-1.4")

stop_words = set(stopwords.words("english"))
custom_stopwords = {
    "even","really","always","just","like","don’t","one","also","something",
    "get","got","thing","things","make","makes","much","many","could","would",
    "without","bit","way","lot","see","say","said","go","going"
}
all_stopwords = stop_words.union(custom_stopwords)
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\d+", "", text)
    tokens = text.split()
    cleaned = [
        lemmatizer.lemmatize(t)
        for t in tokens
        if t not in all_stopwords and len(t)>2
    ]
    return " ".join(cleaned)

# —                    Load your topic model              ————
topic_pipeline = pipeline(
    "text-classification",
    model="sanabar/roberta-topic-head",  # <-- replace with your HF repo
    function_to_apply="sigmoid",
    return_all_scores=True,
    top_k=None,
    framework="pt"
)

def plot_emotion_trends(emotional_data):
    if not emotional_data:
        st.warning("⚠️ No emotional data available.")
        return

    df = pd.DataFrame(emotional_data)
    if "timestamp" not in df.columns:
        st.warning("⚠️ Missing timestamps.")
        return


    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    if df["timestamp"].isna().all():
        st.warning("⚠️ Invalid timestamps.")
        return

    if "answer" not in df.columns or "sentiment" not in df.columns:
        st.warning("⚠️ Missing answers or sentiment.")
        return

    # —                    Get emotions & topics —            —
    # dominant_emotion already applies via sentiment_analysis
    df["dominant_emotion"] = df["sentiment"].apply(
        lambda x: x.get("dominant_emotion","neutral") if isinstance(x,dict) else "neutral"
    )

    # run topic pipeline on each answer (cache if you like)
    topics = []
    for txt in df["answer"]:
        # pipeline returns list of dicts [{label:,score:},…]
        scores = topic_pipeline(txt)[0]
        top = max(scores, key=lambda d: d["score"])["label"]
        topics.append(top)
    df["dominant_topic"] = topics

    # —                 Word Cloud —            ————
    st.subheader("☁️ Most Frequent Words in Journal Entries")
    all_text = " ".join(df["answer"].tolist())
    cleaned = preprocess_text(all_text)
    if cleaned:
        wc = WordCloud(
            width=800, height=400,
            background_color="#1E1E1E",
            colormap="cool",
            contour_color="white",
            contour_width=1,
            max_words=100
        ).generate(cleaned)
        plt.figure(figsize=(10,5),facecolor="#1E1E1E")
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        st.pyplot(plt)
    else:
        st.warning("⚠️ Not enough text for word cloud.")

    # —               📊 Emotion Distribution —       —
    st.subheader("📊 Emotion Distribution")
    emo_counts = df["dominant_emotion"].value_counts()
    plt.figure(figsize=(6,6))
    plt.pie(emo_counts, labels=emo_counts.index, autopct="%1.1f%%",
            colors=sns.color_palette("pastel"))
    plt.title("Emotions")
    st.pyplot(plt)

    # —               📊 Topic Distribution —     —
    st.subheader("📊 Topic Distribution")
    top_counts = df["dominant_topic"].value_counts()
    plt.figure(figsize=(6,6))
    plt.pie(top_counts, labels=top_counts.index, autopct="%1.1f%%",
            colors=sns.color_palette("bright"))
    plt.title("Journal Topics")
    st.pyplot(plt)

    # —               🗂️ Emotion × Topic Heatmap —    —
    st.subheader("💡 Emotion × Topic Co‑occurrence")
    cross = pd.crosstab(df["dominant_topic"], df["dominant_emotion"])
    plt.figure(figsize=(10,6))
    sns.heatmap(cross, annot=True, fmt="d", cmap="YlGnBu")
    plt.xlabel("Emotion")
    plt.ylabel("Topic")
    st.pyplot(plt)

    # —               🕒 Journaling Frequency —     —
    st.subheader("🕒 Journaling Frequency Over Time")
    df["date"] = df["timestamp"].dt.date
    counts = df["date"].value_counts().sort_index()
    plt.figure(figsize=(12,6))
    sns.barplot(x=counts.index, y=counts.values, color="skyblue")
    plt.xticks(rotation=45)
    plt.title("Entries per Day")
    st.pyplot(plt)

    # —               📅 Weekly Patterns —     —
    df["day_of_week"] = df["timestamp"].dt.day_name()
    weekly = pd.crosstab(df["day_of_week"], df["dominant_emotion"])
    weekday_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    weekly = weekly.reindex(weekday_order).fillna(0)
    st.subheader("📅 Weekly Emotion Patterns")
    plt.figure(figsize=(12,6))
    weekly.plot(kind="bar", stacked=True, ax=plt.gca(), colormap="coolwarm", alpha=0.8)
    plt.xticks(rotation=45)
    st.pyplot(plt)
