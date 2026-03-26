import streamlit as st          
import plotly.express as px     
import pandas as pd            
import matplotlib.pyplot as plt 
from wordcloud import WordCloud  

from fetcher import fetch_reddit, fetch_hackernews, fetch_github_trending
from analyzer import add_sentiment, get_top_keywords
import plotly.io as pio
pio.templates.default = "plotly_dark"
 

st.set_page_config(
    page_title="🔥 Trending Now",   
    page_icon="🔥",                  
    layout="wide",                   
    initial_sidebar_state="collapsed"
)
 
 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap');
 
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d0d0d !important;   /* near-black background */
    color: #f0f0f0;
}
 

h1 { font-family: 'Syne', sans-serif; font-size: 3rem !important; }
 

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #1a1a1a;
    padding: 8px;
    border-radius: 12px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    padding: 10px 20px;
    border-radius: 8px;
    color: #888;
}
.stTabs [aria-selected="true"] {
    background: #ff4500 !important;   /* Reddit orange as accent */
    color: white !important;
}
 

div[data-testid="metric-container"] {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 16px;
}
 
/*  Dataframe */
.stDataFrame { border-radius: 10px; overflow: hidden; }
 
/*  Buttons */
.stButton > button {
    background: #ff4500;
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    padding: 8px 20px;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }
 
/* --- Plotly chart container transparency --- */
.js-plotly-plot .plotly .main-svg { background: transparent !important; }
</style>
""", unsafe_allow_html=True)
 
st.markdown("# 🔥 Trending Now")
st.markdown(
    "<p style='color:#888; font-size:1.1rem; margin-top:-10px;'>"
    "Live pulse from Reddit · Hacker News · GitHub — refreshed every 10 min</p>",
    unsafe_allow_html=True
)

col_btn, col_time, _ = st.columns([1, 2, 5])
with col_btn:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()       
        st.rerun()                  
#  DATA LOADING  (cached for 10 minutes) 
@st.cache_data(ttl=600)    
def load_all_data():
    reddit = add_sentiment(fetch_reddit())          
    hn     = add_sentiment(fetch_hackernews())      
    github = fetch_github_trending()                
    return reddit, hn, github
with st.spinner("⏳ Fetching live data from Reddit, HN & GitHub…"):
    reddit_df, hn_df, github_df = load_all_data()
# Shows a quick summary of what was fetched — makes the dashboard feel alive
st.markdown("---")
m1, m2, m3, m4 = st.columns(4)
with m1:
    # len(reddit_df) = number of rows = number of posts fetched
    st.metric("Reddit Posts", len(reddit_df), "today's top")
with m2:
    # .sum() totals all values in the 'score' column; format with comma separator
    total_upvotes = int(reddit_df["score"].sum()) if not reddit_df.empty else 0
    st.metric("Total Upvotes", f"{total_upvotes:,}", "across all posts")
with m3:
    st.metric("HN Stories", len(hn_df), "top stories")
with m4:
    st.metric("GitHub Repos", len(github_df), "trending this week")
 
st.markdown("---")
 
# Every chart shares these settings so the look is consistent
 
CHART_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",     # transparent outer background
    plot_bgcolor="rgba(26,26,26,0.8)", # dark grey chart area
    font=dict(family="DM Sans", color="#f0f0f0"),
    margin=dict(l=10, r=10, t=40, b=10)
)
tab1, tab2, tab3 = st.tabs(["🟠 Reddit", "🟡 Hacker News", "⚫ GitHub"])
with tab1:
    st.subheader("🟠 Top Reddit Posts — Today")
 
    if reddit_df.empty:
        st.warning("No Reddit data available right now.")
    else:
        # ── Row 1: Keywords + Sentiment Pie ──────────────
        col1, col2 = st.columns(2)
 
        with col1:
            # get_top_keywords returns [(word, count), ...] — convert to DataFrame for plotly
            kw_list = get_top_keywords(reddit_df, n=12)
            if kw_list:
                kw_df = pd.DataFrame(kw_list, columns=["keyword", "count"])
                # Sort ascending so longest bar is at the top
                kw_df = kw_df.sort_values("count")
 
                fig = px.bar(
                    kw_df,
                    x="count",
                    y="keyword",
                    orientation="h",              # horizontal bar chart
                    title="🔑 Trending Keywords",
                    color="count",                # color intensity = count
                    color_continuous_scale="Oranges"
                )
                fig.update_layout(**CHART_THEME)
                fig.update_coloraxes(showscale=False)   # hide the color legend bar
                st.plotly_chart(fig, use_container_width=True)
 
        with col2:
            # value_counts() returns a Series: {"Positive": 12, "Neutral": 8, ...}
            sent = reddit_df["sentiment"].value_counts()
            fig2 = px.pie(
                values=sent.values,
                names=sent.index,
                title="😊 Sentiment of Post Titles",
                color=sent.index,
                color_discrete_map={
                    "Positive": "#27ae60",   # green
                    "Negative": "#e74c3c",   # red
                    "Neutral":  "#7f8c8d"    # grey
                },
                hole=0.45    # makes it a donut chart (more modern look)
            )
            fig2.update_layout(**CHART_THEME)
            st.plotly_chart(fig2, use_container_width=True)
        top_reddit = reddit_df.nlargest(10, "score")   # 10 highest-score posts
 
        # Truncate long titles so they fit on the chart
        top_reddit = top_reddit.copy()
        top_reddit["short_title"] = top_reddit["title"].str[:55] + "…"
 
        fig3 = px.bar(
            top_reddit,
            x="score",
            y="short_title",
            orientation="h",
            title="🏆 Top 10 Posts by Upvotes",
            color="score",
            color_continuous_scale="Reds",
            hover_data={"title": True, "subreddit": True, "num_comments": True}
        )
        fig3.update_layout(**CHART_THEME, height=420)
        fig3.update_coloraxes(showscale=False)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("#### 📋 All Posts")
        display_cols = [c for c in ["title","score","subreddit","num_comments","sentiment"]
                        if c in reddit_df.columns]
        st.dataframe(
            reddit_df[display_cols].sort_values("score", ascending=False),
            use_container_width=True,
            hide_index=True
        )
 
#  TAB 2 — HACKER NEWS
with tab2:
    st.subheader("🟡 Top Hacker News Stories")
 
    if hn_df.empty:
        st.warning("No Hacker News data available right now.")
    else:
        col1, col2 = st.columns(2)
 
        with col1:
            # Truncate titles to fit on horizontal bar chart
            hn_plot = hn_df.head(15).copy()
            hn_plot["short_title"] = hn_plot["title"].str[:50] + "…"
 
            fig = px.bar(
                hn_plot.sort_values("score"),    # sort ascending so top is highest
                x="score",
                y="short_title",
                orientation="h",
                title="📈 Top Stories by Points",
                color="score",
                color_continuous_scale="YlOrBr",
                hover_data={"title": True, "by": True}
            )
            fig.update_layout(**CHART_THEME)
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(fig, use_container_width=True)
 
        with col2:
            sent_hn = hn_df["sentiment"].value_counts()
            fig2 = px.pie(
                values=sent_hn.values,
                names=sent_hn.index,
                title="😐 HN Title Sentiment",
                color=sent_hn.index,
                color_discrete_map={
                    "Positive": "#f39c12",
                    "Negative": "#e74c3c",
                    "Neutral":  "#7f8c8d"
                },
                hole=0.45
            )
            fig2.update_layout(**CHART_THEME)
            st.plotly_chart(fig2, use_container_width=True)
 
        # ── HN Keyword Bar ────────────────────────────────
        kw_hn = get_top_keywords(hn_df, n=12)
        if kw_hn:
            kw_hn_df = pd.DataFrame(kw_hn, columns=["keyword", "count"]).sort_values("count")
            fig3 = px.bar(
                kw_hn_df, x="count", y="keyword", orientation="h",
                title="🔑 HN Trending Keywords",
                color="count", color_continuous_scale="YlOrBr"
            )
            fig3.update_layout(**CHART_THEME)
            fig3.update_coloraxes(showscale=False)
            st.plotly_chart(fig3, use_container_width=True)
        st.markdown("#### 📋 All Stories")
        display_hn = [c for c in ["title","score","by","sentiment"] if c in hn_df.columns]
        st.dataframe(
            hn_df[display_hn].sort_values("score", ascending=False),
            use_container_width=True,
            hide_index=True
        )
 
#  TAB 3 — GITHUB TRENDING
with tab3:
    st.subheader("⚫ GitHub — Trending This Week")
 
    if github_df.empty:
        st.warning("No GitHub data available right now.")
    else:
        col1, col2 = st.columns(2)
 
        with col1:
            # Top 15 repos by stars — horizontal bar chart
            top_gh = github_df.nlargest(15, "stars").copy()
            top_gh["label"] = top_gh["name"].str[:30]
 
            fig = px.bar(
                top_gh.sort_values("stars"),
                x="stars",
                y="label",
                orientation="h",
                title="⭐ Most Starred Repos",
                color="stars",
                color_continuous_scale="Greys",
                hover_data={"full_name": True, "description": True, "language": True}
            )
            fig.update_layout(**CHART_THEME)
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(fig, use_container_width=True)
 
        with col2:
            # Language distribution — how many trending repos per language
            lang_counts = (
                github_df["language"]
                .value_counts()
                .head(8)              # top 8 languages only
                .reset_index()
            )
            lang_counts.columns = ["language", "count"]
 
            fig2 = px.pie(
                lang_counts,
                values="count",
                names="language",
                title="💻 Language Breakdown",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Set3
                # Set3 = a nice palette of distinguishable colors
            )
            fig2.update_layout(**CHART_THEME)
            st.plotly_chart(fig2, use_container_width=True)
        all_desc = " ".join(github_df["description"].dropna().tolist())
 
        if all_desc.strip():
            st.markdown("#### ☁️ What Trending Repos Are About")
 
            wc = WordCloud(
                width=1200,
                height=400,
                background_color="#0d0d0d",   # match app dark background
                colormap="cool",               # blue-purple-cyan color gradient
                max_words=80,                  # limit word count for readability
                contour_width=1,
                contour_color="#333333"
            ).generate(all_desc)
 
            fig_wc, ax = plt.subplots(figsize=(14, 4))
            fig_wc.patch.set_facecolor("#0d0d0d")  # figure background = dark
            ax.set_facecolor("#0d0d0d")
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")   # hide axis lines and ticks
            st.pyplot(fig_wc, use_container_width=True)
            plt.close(fig_wc)   # free memory after rendering
        st.markdown("#### 📊 Stars vs Forks")
        fig3 = px.scatter(
            github_df,
            x="stars",
            y="forks",
            size="stars",              
            color="language",
            hover_name="full_name",
            hover_data={"description": True},
            title="Stars vs Forks (bubble size = stars)",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig3.update_layout(**CHART_THEME)
        st.plotly_chart(fig3, use_container_width=True)
 
        #  Full Table 
        st.markdown("#### 📋 All Trending Repos")
        st.dataframe(
            github_df[["full_name","description","stars","forks","language","url"]]
            .sort_values("stars", ascending=False),
            use_container_width=True,
            hide_index=True
        )
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#555; font-size:0.85rem;'>"
    "Built with ❤️ using Streamlit · Data from Reddit, Hacker News & GitHub APIs · "
    "Auto-refreshes every 10 minutes</p>",
    unsafe_allow_html=True
)
