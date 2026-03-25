import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

def add_sentiment(df, text_column='title'):
    """Add sentiment analysis to dataframe using VADER"""
    sentiments = []
    for text in df[text_column]:
        if pd.isna(text):
            sentiments.append('Neutral')
        else:
            score = analyzer.polarity_scores(str(text))['compound']
            if score >= 0.05:
                sentiments.append('Positive')
            elif score <= -0.05:
                sentiments.append('Negative')
            else:
                sentiments.append('Neutral')
    
    df['sentiment'] = sentiments
    return df

def get_top_keywords(df, text_column='title', n=10):
    """Extract top keywords from text column"""
    # Combine all text
    all_text = ' '.join(df[text_column].dropna().astype(str))
    
    # Tokenize
    tokens = word_tokenize(all_text.lower())
    
    # Remove stopwords and non-alphabetic tokens
    stop_words = set(stopwords.words('english'))
    keywords = [word for word in tokens if word.isalpha() and word not in stop_words]
    
    # Count frequencies
    word_counts = Counter(keywords)
    
    # Return top n keywords
    return word_counts.most_common(n)