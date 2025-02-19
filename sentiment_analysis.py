from textblob import TextBlob


def analyze_sentiment(text):
    analysis = TextBlob(text)
    sentiment = analysis.sentiment.polarity
    if sentiment > 0.5:
        return "Very Positive"
    elif sentiment > 0.1:
        return "Positive"
    elif sentiment < -0.5:
        return "Very Negative"
    elif sentiment < -0.1:
        return "Negative"
    else:
        return "Neutral"



