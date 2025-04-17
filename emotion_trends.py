import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from wordcloud import WordCloud
import stopwords

def plot_emotion_trends(emotional_data):
    """Generate multiple insightful visualizations based on user journaling data."""

    if not emotional_data or len(emotional_data) == 0:
        st.warning("⚠️ No emotional data available. Start journaling to track trends!")
        return

    # Convert to DataFrame
    df = pd.DataFrame(emotional_data)

    # ✅ **Ensure timestamp exists**
    if "timestamp" not in df.columns:
        st.warning("⚠️ No timestamp found in journal entries.")
        return

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    if df["timestamp"].isna().all():
        st.warning("⚠️ All timestamps are invalid. Check Firestore data.")
        return

    # ✅ **Ensure sentiment exists**
    if "sentiment" not in df.columns:
        st.warning("⚠️ No sentiment data found in journal entries.")
        return

    # Extract dominant emotion
    df["dominant_emotion"] = df["sentiment"].apply(lambda x: x.get("dominant_emotion", "neutral") if isinstance(x, dict) else "neutral")

    # Extract individual emotion scores
    df["joy"] = df["sentiment"].apply(lambda x: x["emotion_scores"].get("joy", 0) if isinstance(x, dict) else 0)
    df["sadness"] = df["sentiment"].apply(lambda x: x["emotion_scores"].get("sadness", 0) if isinstance(x, dict) else 0)
    df["anger"] = df["sentiment"].apply(lambda x: x["emotion_scores"].get("anger", 0) if isinstance(x, dict) else 0)
    df["neutral"] = df["sentiment"].apply(lambda x: x["emotion_scores"].get("neutral", 0) if isinstance(x, dict) else 0)
    df["surprise"] = df["sentiment"].apply(lambda x: x["emotion_scores"].get("surprise", 0) if isinstance(x, dict) else 0)

    # **Word Cloud for Most Used Words**
    st.subheader("☁️ Most Frequent Words in Journal Entries")

    all_text = " ".join(entry["answer"] for entry in emotional_data if "answer" in entry)

    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    all_text = " ".join(word for word in all_text.split() if word.lower() not in stop_words)



    if all_text:
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color="#1E1E1E",  # Dark background
            colormap="cool",  # Use a cool tone for words
            contour_color="white",  # White outline for clarity
            contour_width=1,  # Slight outline
            max_words=100,
            font_path=None,  # Optional: You can specify a font file path for more styling
        ).generate(all_text)

        plt.figure(figsize=(10, 5), facecolor="#1E1E1E")  # Match Streamlit's dark mode
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")  # Remove grid lines
        plt.tight_layout(pad=0)
        st.pyplot(plt)
    else:
        st.warning("⚠️ Not enough journal entries to generate a word cloud.")

    # **Sentiment Distribution Pie Chart**
    st.subheader("📊 Sentiment Distribution")
    emotion_counts = df["dominant_emotion"].value_counts()

    plt.figure(figsize=(6, 6))
    plt.pie(emotion_counts, labels=emotion_counts.index, autopct="%1.1f%%", colors=sns.color_palette("pastel"))
    plt.title("Proportion of Different Emotions in Journal Entries")
    st.pyplot(plt)

    # **Journaling Frequency Over Time**
    st.subheader("🕒 Journaling Frequency Over Time")
    df["date"] = df["timestamp"].dt.date
    journal_counts = df["date"].value_counts().sort_index()

    plt.figure(figsize=(12, 6))
    sns.barplot(x=journal_counts.index, y=journal_counts.values, color="blue")
    plt.xticks(rotation=45)
    plt.xlabel("Date")
    plt.ylabel("Number of Journal Entries")
    plt.title("User Journaling Frequency Over Time")
    st.pyplot(plt)

    plot_weekly_emotion_trends(df)


def plot_weekly_emotion_trends(df):
    """Generates a bar chart showing dominant emotions by day of the week."""

    # Ensure timestamp and dominant emotion exist
    if "timestamp" not in df.columns or "dominant_emotion" not in df.columns:
        st.warning("⚠️ Not enough data to generate a weekly emotion trend.")
        return

    # Extract day of the week (0 = Monday, 6 = Sunday)
    df["day_of_week"] = df["timestamp"].dt.day_name()

    # Count dominant emotions per day
    emotion_counts = df.groupby("day_of_week")["dominant_emotion"].value_counts().unstack().fillna(0)

    # Sort by actual weekday order
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    emotion_counts = emotion_counts.reindex(weekday_order)

    # Plot the emotion distribution per day
    st.subheader("📅 Weekly Emotion Patterns")
    plt.figure(figsize=(12, 6))
    emotion_counts.plot(kind="bar", stacked=True, colormap="coolwarm", alpha=0.85)
    plt.xlabel("Day of the Week")
    plt.ylabel("Number of Entries")
    plt.title("Dominant Emotions by Day of the Week")
    plt.legend(title="Emotion", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.xticks(rotation=45)
    st.pyplot(plt)
