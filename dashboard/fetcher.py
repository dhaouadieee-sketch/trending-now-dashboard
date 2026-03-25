import requests          # sends HTTP requests to APIs
import pandas as pd      # stores data in table (DataFrame) format
import streamlit as st   # used only for st.warning() / st.error() messages in the UI

#  1. REDDIT

def fetch_reddit():
        headers = {
        # Reddit REQUIRES a User-Agent string or it blocks the request (429 error).
        # Format: AppName/Version (by /u/YourRedditUsername)
        'User-Agent': 'TrendingNowDashboard/1.0 (by /u/trendingdashboard)'
    }

    # ?t=day  → top posts of the last 24 hours
    # &limit=25 → fetch 25 posts max
    url = "https://www.reddit.com/r/all/top.json?t=day&limit=25"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        # timeout=10 → stop waiting after 10 seconds to avoid hanging the app

        if response.status_code == 200:          # 200 = HTTP "OK"
            data = response.json()               # parse JSON response into a Python dict
            posts = data.get("data", {}).get("children", [])
            # Reddit wraps posts inside data.children — each post is a dict called "data"

            reddit_data = []
            for post in posts:
                post_data = post.get("data", {})  # inner dict with all post fields
                reddit_data.append({
                    "title":        post_data.get("title", ""),
                    "score":        post_data.get("score", 0),        # upvotes
                    "subreddit":    post_data.get("subreddit", ""),
                    "url":          post_data.get("url", ""),
                    "num_comments": post_data.get("num_comments", 0)
                })

            return pd.DataFrame(reddit_data)   # convert list of dicts → DataFrame

        else:
            # API is up but returned an error code (e.g. 429 rate-limit)
            st.warning(f"⚠️ Reddit returned status {response.status_code}. Showing sample data.")
            return _sample_reddit()

    except Exception as e:
        # Network error, timeout, JSON parse failure, etc.
        st.error(f"❌ Reddit fetch failed: {e}")
        return _sample_reddit()

#  2. HACKER NEWS

def fetch_hackernews():
    """
    Fetches top 20 stories from Hacker News using its free Firebase API.
    Step 1: get list of top story IDs
    Step 2: fetch details for each ID individually

    Returns:
        pd.DataFrame with columns: title, score, url, by, time
    """
    try:
        # Step 1: get ordered list of top story IDs (returns a JSON array of integers)
        id_resp = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10
        )

        if id_resp.status_code != 200:
            st.warning("⚠️ HN top-stories list unavailable. Showing sample data.")
            return _sample_hackernews()

        story_ids = id_resp.json()[:20]   # keep only the first 20 IDs

        hn_data = []
        for story_id in story_ids:
            # Step 2: fetch the full item object for each story ID
            item_resp = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                timeout=5   # shorter timeout per item
            )
            if item_resp.status_code == 200:
                story = item_resp.json()
                if story and story.get("type") == "story":
                    # only include actual stories (not jobs/polls/comments)
                    hn_data.append({
                        "title": story.get("title", ""),
                        "score": story.get("score", 0),
                        "url":   story.get("url", "https://news.ycombinator.com"),
                        "by":    story.get("by", "anonymous"),
                        "time":  story.get("time", 0)   # Unix timestamp
                    })

        return pd.DataFrame(hn_data) if hn_data else _sample_hackernews()

    except Exception as e:
        st.error(f"❌ Hacker News fetch failed: {e}")
        return _sample_hackernews()

#  3. GITHUB TRENDING

def fetch_github_trending():
    """
    Uses GitHub's public search API to find the most-starred repos
    created in the last 7 days — this mimics the "trending" page.

    Returns:
        pd.DataFrame with columns: name, full_name, description, stars, forks, language, url
    """
    try:
        from datetime import datetime, timedelta

        # Calculate date 7 days ago in YYYY-MM-DD format (required by GitHub API)
        since = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")

        url = (
            f"https://api.github.com/search/repositories"
            f"?q=created:>{since}&sort=stars&order=desc&per_page=25"
        )
        # q=created:>DATE  → repos created after DATE
        # sort=stars        → rank by star count
        # per_page=25       → 25 results

        headers = {
            'Accept': 'application/vnd.github.v3+json'   # required GitHub API header
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            repos = response.json().get("items", [])

            github_data = []
            for repo in repos:
                github_data.append({
                    "name":        repo.get("name", ""),
                    "full_name":   repo.get("full_name", ""),
                    "description": repo.get("description", "No description") or "No description",
                    "stars":       repo.get("stargazers_count", 0),
                    "forks":       repo.get("forks_count", 0),
                    "language":    repo.get("language", "Unknown") or "Unknown",
                    "url":         repo.get("html_url", "")
                })

            return pd.DataFrame(github_data)

        else:
            st.warning(f"⚠️ GitHub API returned {response.status_code}. Showing sample data.")
            return _sample_github()

    except Exception as e:
        st.error(f"❌ GitHub fetch failed: {e}")
        return _sample_github()



#  FALLBACK SAMPLE DATA (used when APIs fail)

# These functions return realistic-looking placeholder data so the app
# never shows a blank screen or crashes during demos / rate-limiting.

def _sample_reddit():
    return pd.DataFrame({
        "title":        ["AI model beats human experts", "Python 3.13 is out",
                         "Open source project hits 100k stars", "New study on sleep & productivity",
                         "NASA reveals new Mars images"],
        "score":        [45200, 23100, 18400, 9800, 7600],
        "subreddit":    ["technology", "python", "programming", "science", "space"],
        "num_comments": [812, 430, 295, 178, 134],
        "url":          ["https://reddit.com"] * 5
    })

def _sample_hackernews():
    return pd.DataFrame({
        "title": ["Show HN: I built a self-hostable analytics tool",
                  "The death of the junior developer",
                  "Why Rust is eating C++",
                  "GPT-5 architecture leaked",
                  "Postgres is all you need"],
        "score": [892, 743, 612, 544, 489],
        "by":    ["hacker1", "hacker2", "hacker3", "hacker4", "hacker5"],
        "url":   ["https://news.ycombinator.com"] * 5,
        "time":  [1700000000] * 5
    })

def _sample_github():
    return pd.DataFrame({
        "name":        ["supermemory", "openui", "tldraw", "pipecat", "livekit"],
        "full_name":   ["user/supermemory", "user/openui", "user/tldraw",
                        "user/pipecat", "user/livekit"],
        "description": ["AI memory layer for LLMs", "Describe UI and it generates it",
                        "Infinite canvas drawing tool", "Real-time AI voice pipelines",
                        "Open source video/audio infra"],
        "stars":       [18200, 14500, 11300, 9700, 8100],
        "forks":       [980, 760, 620, 510, 430],
        "language":    ["TypeScript", "Python", "TypeScript", "Python", "Go"],
        "url":         ["https://github.com"] * 5
    })