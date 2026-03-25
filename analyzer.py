import pandas as pd
from textblob import TextBlob
from collections import Counter
import re

def get_sentiment(text):
    score = TextBlob(str(text)).sentiment.polarity
    if score > 0.1:
        return "Positive"
    elif score < -0.1:
        return "Negative"
    else:
        return "Neutral"

def add_sentiment(df, column="title"):
    df["sentiment"] = df[column].apply(get_sentiment)
    return df

def get_top_keywords(df, column="title", top_n=20):
    stopwords = {"the","a","an","is","in","of","to","and","for",
                 "with","on","at","by","from","this","that","it","as"}
    all_words = []
    for title in df[column].dropna():
        words = re.findall(r'\b[a-zA-Z]{4,}\b', title.lower())
        all_words.extend([w for w in words if w not in stopwords])
    return Counter(all_words).most_common(top_n)