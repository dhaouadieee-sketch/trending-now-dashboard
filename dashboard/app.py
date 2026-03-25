import nltk
import streamlit as st
import os

# Download all required NLTK data
@st.cache_resource
def download_nltk_data():
    """Download required NLTK data packages"""
    try:
        # Create nltk data directory if needed
        nltk_data_dir = os.path.join(os.path.expanduser("~"), "nltk_data")
        if not os.path.exists(nltk_data_dir):
            os.makedirs(nltk_data_dir)
        
        # Download required packages
        nltk.download('vader_lexicon', quiet=True, download_dir=nltk_data_dir)
        nltk.download('punkt', quiet=True, download_dir=nltk_data_dir)
        nltk.download('punkt_tab', quiet=True, download_dir=nltk_data_dir)
        nltk.download('stopwords', quiet=True, download_dir=nltk_data_dir)
        
        # Add to nltk data path
        nltk.data.path.append(nltk_data_dir)
        
    except Exception as e:
        st.warning(f"NLTK download warning: {str(e)}")

# Download NLTK data before importing other modules
download_nltk_data()

# Now import other modules
import plotly.express as px
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from fetcher import fetch_reddit, fetch_hackernews, fetch_github_trending
from analyzer import add_sentiment, get_top_keywords

# Page configuration
st.set_page_config(page_title="Trending Now", page_icon="🔥", layout="wide")
st.title("🔥 Trending Now Dashboard")
st.caption("Live trends from Reddit · Hacker News · GitHub")

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

@st.cache_data(ttl=600)
def load_data():
    reddit = add_sentiment(fetch_reddit())
    hn = add_sentiment(fetch_hackernews())
    github = fetch_github_trending()
    return reddit, hn, github

with st.spinner("Fetching live data..."):
    reddit_df, hn_df, github_df = load_data()

# Check if data loaded successfully
if reddit_df.empty:
    st.warning("⚠️ Using sample data for Reddit")
if hn_df.empty:
    st.warning("⚠️ Using sample data for Hacker News")
if github_df.empty:
    st.warning("⚠️ Using sample data for GitHub")

# Rest of your code continues here...
tab1, tab2, tab3 = st.tabs(["Reddit", "Hacker News", "GitHub Trending"])

# ── Reddit Tab ───────────────────────────────────────────
with tab1:
    st.subheader("Top Reddit Posts Today")
    col1, col2 = st.columns(2)

    with col1:
        if not reddit_df.empty:
            keywords = get_top_keywords(reddit_df)
            if keywords:
                kw_df = pd.DataFrame(keywords, columns=["keyword", "count"])
                fig = px.bar(kw_df, x="count", y="keyword", orientation="h",
                             title="Top Keywords", color="count",
                             color_continuous_scale="Reds")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No keywords found")
        else:
            st.info("No Reddit data available")

    with col2:
        if not reddit_df.empty and "sentiment" in reddit_df.columns:
            sentiment_counts = reddit_df["sentiment"].value_counts()
            fig2 = px.pie(values=sentiment_counts.values,
                          names=sentiment_counts.index,
                          title="Sentiment of Post Titles",
                          color_discrete_map={"Positive":"#2ecc71",
                                              "Negative":"#e74c3c",
                                              "Neutral":"#95a5a6"})
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No sentiment data available")

    if not reddit_df.empty:
        st.dataframe(reddit_df[["title","score","subreddit","sentiment"]],
                     use_container_width=True)

# ── Hacker News Tab ──────────────────────────────────────
with tab2:
    st.subheader("Top Hacker News Stories")
    if not hn_df.empty:
        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(hn_df.head(15), x="score", y="title", orientation="h",
                         title="Top Stories by Score",
                         color="score", color_continuous_scale="Blues")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            if "sentiment" in hn_df.columns:
                sentiment_counts = hn_df["sentiment"].value_counts()
                fig2 = px.pie(values=sentiment_counts.values,
                              names=sentiment_counts.index,
                              title="Sentiment Analysis",
                              color_discrete_map={"Positive":"#2ecc71",
                                                  "Negative":"#e74c3c",
                                                  "Neutral":"#95a5a6"})
                st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(hn_df[["title","score","sentiment"]], use_container_width=True)
    else:
        st.info("No Hacker News data available")

# ── GitHub Tab ───────────────────────────────────────────
with tab3:
    st.subheader("GitHub Trending Repositories")
    if not github_df.empty:
        all_text = " ".join(github_df["description"].dropna().astype(str).tolist())
        if all_text.strip():
            wc = WordCloud(width=800, height=400,
                           background_color="white",
                           colormap="viridis").generate(all_text)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
        st.dataframe(github_df, use_container_width=True)
    else:
        st.info("No GitHub data available")