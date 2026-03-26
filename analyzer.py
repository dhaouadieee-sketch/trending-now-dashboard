import re                                           # built-in: regex for text cleaning
import pandas as pd                                 # data manipulation
from collections import Counter                     # built-in: counts occurrences efficiently
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
 
# Create ONE shared analyzer instance — creating it per-call would be slow
_vader = SentimentIntensityAnalyzer()
#  1. SENTIMENT ANALYSIS
def add_sentiment(df, text_column="title"):
    # Edge case: empty DataFrame or column doesn't exist → label everything Neutral
    if df.empty or text_column not in df.columns:
        df["sentiment"] = "Neutral"
        return df
 
    sentiments = []
    for text in df[text_column]:
        if pd.isna(text) or str(text).strip() == "":
            # Missing or blank text → default to Neutral
            sentiments.append("Neutral")
        else:
            try:
                # polarity_scores() returns dict: {"neg":…, "neu":…, "pos":…, "compound":…}
                # We only need "compound" — the overall score
                score = _vader.polarity_scores(str(text))["compound"]
 
                if score >= 0.05:
                    sentiments.append("Positive")
                elif score <= -0.05:
                    sentiments.append("Negative")
                else:
                    sentiments.append("Neutral")
 
            except Exception:
                # If VADER crashes on a weird character, just label it Neutral
                sentiments.append("Neutral")
 
    df["sentiment"] = sentiments   # attach the list as a new column
    return df
#  2. KEYWORD EXTRACTION
 
# Extended stop-word list — common English words that carry no meaning
_STOP_WORDS = {
    'a','an','and','are','as','at','be','been','but','by','for','from',
    'has','have','had','he','in','is','it','its','me','my','not','of',
    'on','or','the','this','that','to','was','with','you','your','we',
    'our','they','their','i','do','does','did','will','would','could',
    'should','may','might','can','what','which','who','whom','where',
    'when','why','how','just','also','about','into','than','more',
    'get','got','use','used','using','new','one','two','via','vs',
    'up','out','now','after','all','if','so','no','yes','how','then',
    'show','hn','ask'   # "Show HN" / "Ask HN" are HN post prefixes — not keywords
}
 
def get_top_keywords(df, text_column="title", n=10):
    
    if df.empty or text_column not in df.columns:
        return []
 
    # Join every title into one long string (drop NaN first)
    all_text = " ".join(df[text_column].dropna().astype(str))
 
    if not all_text.strip():
        return []

    all_text = all_text.lower()
    all_text = re.sub(r"[^a-z\s]", "", all_text)
    words = all_text.split()
    keywords = [w for w in words if w not in _STOP_WORDS and len(w) > 2]
    counts = Counter(keywords)
    return counts.most_common(n)
