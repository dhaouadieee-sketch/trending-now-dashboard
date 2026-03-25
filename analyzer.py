import pandas as pd
import re
from collections import Counter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

def add_sentiment(df, text_column='title'):
    """Add sentiment analysis to dataframe using VADER"""
    if df.empty or text_column not in df.columns:
        df['sentiment'] = 'Neutral'
        return df
    
    sentiments = []
    for text in df[text_column]:
        if pd.isna(text) or text == '':
            sentiments.append('Neutral')
        else:
            try:
                score = analyzer.polarity_scores(str(text))['compound']
                if score >= 0.05:
                    sentiments.append('Positive')
                elif score <= -0.05:
                    sentiments.append('Negative')
                else:
                    sentiments.append('Neutral')
            except:
                sentiments.append('Neutral')
    
    df['sentiment'] = sentiments
    return df

def simple_tokenize(text):
    """Simple tokenizer that doesn't require NLTK data"""
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Split into words
    words = text.split()
    return words

def get_top_keywords(df, text_column='title', n=10):
    """Extract top keywords from text column using simple tokenization"""
    if df.empty or text_column not in df.columns:
        return []
    
    # Combine all text
    all_text = ' '.join(df[text_column].dropna().astype(str))
    
    if not all_text.strip():
        return []
    
    # Simple tokenization
    words = simple_tokenize(all_text)
    
    # Common English stopwords to filter out
    stop_words = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'for', 'from', 'has', 'he', 'in', 'is', 'it',
        'its', 'of', 'on', 'or', 'the', 'to', 'was', 'with', 'this', 'that', 'you', 'your', 'we', 'our', 'they',
        'their', 'i', 'me', 'my', 'mine', 'am', 'have', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'what', 'which', 'who', 'whom', 'where', 'when', 'why', 'how'
    }
    
    # Filter stopwords and short words
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Count frequencies
    word_counts = Counter(keywords)
    
    # Return top n keywords
    return word_counts.most_common(n)