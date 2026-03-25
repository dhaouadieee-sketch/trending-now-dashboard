import streamlit as st
import plotly.express as px
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from fetcher import fetch_reddit, fetch_hackernews, fetch_github_trending
from analyzer import add_sentiment, get_top_keywords

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

tab1, tab2, tab3 = st.tabs(["Reddit", "Hacker News", "GitHub Trending"])

# ── Reddit Tab ───────────────────────────────────────────
with tab1:
    st.subheader("Top Reddit Posts Today")
    col1, col2 = st.columns(2)

    with col1:
        keywords = get_top_keywords(reddit_df)
        kw_df = pd.DataFrame(keywords, columns=["keyword", "count"])
        fig = px.bar(kw_df, x="count", y="keyword", orientation="h",
                     title="Top Keywords", color="count",
                     color_continuous_scale="Reds")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        sentiment_counts = reddit_df["sentiment"].value_counts()
        fig2 = px.pie(values=sentiment_counts.values,
                      names=sentiment_counts.index,
                      title="Sentiment of Post Titles",
                      color_discrete_map={"Positive":"#2ecc71",
                                          "Negative":"#e74c3c",
                                          "Neutral":"#95a5a6"})
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(reddit_df[["title","score","subreddit","sentiment"]],
                 use_container_width=True)

# ── Hacker News Tab ──────────────────────────────────────
with tab2:
    st.subheader("Top Hacker News Stories")
    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(hn_df.head(15), x="score", y="title", orientation="h",
                     title="Top Stories by Score",
                     color="score", color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        sentiment_counts = hn_df["sentiment"].value_counts()
        fig2 = px.pie(values=sentiment_counts.values,
                      names=sentiment_counts.index,
                      title="Sentiment Analysis",
                      color_discrete_map={"Positive":"#2ecc71",
                                          "Negative":"#e74c3c",
                                          "Neutral":"#95a5a6"})
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(hn_df[["title","score","sentiment"]], use_container_width=True)

# ── GitHub Tab ───────────────────────────────────────────
with tab3:
    st.subheader("GitHub Trending Repositories")

    all_text = " ".join(github_df["description"].dropna().tolist())
    if all_text.strip():
        wc = WordCloud(width=800, height=400,
                       background_color="white",
                       colormap="viridis").generate(all_text)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

    st.dataframe(github_df, use_container_width=True)