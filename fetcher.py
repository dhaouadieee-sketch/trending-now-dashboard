"""
fetcher.py
----------
Fetches live data from Reddit, Hacker News, and GitHub.

KEY FIX: Reddit frequently blocks cloud server IPs (Streamlit Cloud included).
We now safely check response content BEFORE calling .json() so we never
get a JSONDecodeError crash. If Reddit blocks us, we silently use sample data.
"""

import requests
import pandas as pd
import streamlit as st


# ─────────────────────────────────────────────
#  HELPER — safe JSON parser
# ─────────────────────────────────────────────

def _safe_json(response):
    """
    Tries to parse a requests Response as JSON.
    Returns the parsed dict/list on success, or None on failure.

    Why: Reddit (and sometimes GitHub) returns an HTML error page or
    empty body instead of JSON when they block/rate-limit a request.
    Calling .json() on HTML raises JSONDecodeError and crashes the app.
    """
    try:
        # Check Content-Type header — JSON responses say "application/json"
        content_type = response.headers.get("Content-Type", "")
        if "json" not in content_type and "javascript" not in content_type:
            # Response is HTML or something else — not parseable as JSON
            return None

        return response.json()   # parse and return the dict/list

    except Exception:
        # Catches JSONDecodeError, ValueError, etc.
        return None


# ─────────────────────────────────────────────
#  1. REDDIT
# ─────────────────────────────────────────────

def fetch_reddit():
    """
    Fetches top 25 posts of the day from r/all.

    Reddit blocks many cloud datacenter IPs. When that happens the response
    is an HTML page (not JSON), so _safe_json() returns None and we fall
    back to sample data — the app keeps running normally.
    """
    headers = {
        # Reddit requires a descriptive User-Agent or it returns 429/403
        "User-Agent": "Mozilla/5.0 (compatible; TrendingDashboard/1.0)"
    }
    url = "https://www.reddit.com/r/all/top.json?t=day&limit=25"

    try:
        response = requests.get(url, headers=headers, timeout=10)

        # _safe_json returns None if response isn't valid JSON
        data = _safe_json(response)

        if data is None:
            # Reddit blocked us or returned garbage — use sample data silently
            st.info("📋 Reddit data: showing curated sample (live API restricted on cloud)")
            return _sample_reddit()

        posts = data.get("data", {}).get("children", [])

        if not posts:
            return _sample_reddit()

        reddit_data = []
        for post in posts:
            pd_ = post.get("data", {})
            reddit_data.append({
                "title":        pd_.get("title", ""),
                "score":        pd_.get("score", 0),
                "subreddit":    pd_.get("subreddit", ""),
                "url":          pd_.get("url", ""),
                "num_comments": pd_.get("num_comments", 0)
            })

        return pd.DataFrame(reddit_data)

    except requests.exceptions.Timeout:
        st.info("📋 Reddit timed out — showing sample data.")
        return _sample_reddit()
    except Exception as e:
        st.info(f"📋 Reddit unavailable ({type(e).__name__}) — showing sample data.")
        return _sample_reddit()


# ─────────────────────────────────────────────
#  2. HACKER NEWS
# ─────────────────────────────────────────────

def fetch_hackernews():
    """
    Fetches top 20 stories from Hacker News Firebase API.
    HN's API is very reliable and rarely blocks cloud IPs.
    """
    try:
        # Step 1: get list of top story IDs
        id_resp = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10
        )
        ids = _safe_json(id_resp)

        if not ids:
            st.info("📋 HN unavailable — showing sample data.")
            return _sample_hackernews()

        story_ids = ids[:20]   # only fetch top 20 to keep it fast

        hn_data = []
        for story_id in story_ids:
            item_resp = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                timeout=5
            )
            story = _safe_json(item_resp)

            # Only include actual story items (not jobs, polls, comments)
            if story and story.get("type") == "story" and story.get("title"):
                hn_data.append({
                    "title": story.get("title", ""),
                    "score": story.get("score", 0),
                    "url":   story.get("url", "https://news.ycombinator.com"),
                    "by":    story.get("by", "anonymous"),
                    "time":  story.get("time", 0)
                })

        return pd.DataFrame(hn_data) if hn_data else _sample_hackernews()

    except Exception as e:
        st.info(f"📋 HN unavailable ({type(e).__name__}) — showing sample data.")
        return _sample_hackernews()


# ─────────────────────────────────────────────
#  3. GITHUB TRENDING
# ─────────────────────────────────────────────

def fetch_github_trending():
    """
    Uses GitHub's public search API to find repos created in the last 7 days,
    sorted by stars — this mimics the official GitHub Trending page.

    GitHub's API is generous with unauthenticated requests (60/hour).
    """
    try:
        from datetime import datetime, timedelta

        # Repos created after this date (7 days ago)
        since = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")

        url = (
            "https://api.github.com/search/repositories"
            f"?q=created:>{since}&sort=stars&order=desc&per_page=25"
        )
        headers = {"Accept": "application/vnd.github.v3+json"}

        response = requests.get(url, headers=headers, timeout=10)
        data = _safe_json(response)

        if not data or "items" not in data:
            st.info("📋 GitHub API unavailable — showing sample data.")
            return _sample_github()

        repos = data["items"]

        github_data = []
        for repo in repos:
            github_data.append({
                "name":        repo.get("name", ""),
                "full_name":   repo.get("full_name", ""),
                "description": repo.get("description") or "No description",
                "stars":       repo.get("stargazers_count", 0),
                "forks":       repo.get("forks_count", 0),
                "language":    repo.get("language") or "Unknown",
                "url":         repo.get("html_url", "")
            })

        return pd.DataFrame(github_data)

    except Exception as e:
        st.info(f"📋 GitHub unavailable ({type(e).__name__}) — showing sample data.")
        return _sample_github()


# ─────────────────────────────────────────────
#  SAMPLE / FALLBACK DATA
# ─────────────────────────────────────────────
# Used whenever a live API is blocked or unavailable.
# Realistic enough to make the dashboard look great for demos.

def _sample_reddit():
    return pd.DataFrame({
        "title": [
            "AI agents are now writing 25% of Google's code",
            "Python 3.14 drops the GIL by default",
            "SpaceX Starship completes first full orbital mission",
            "New study: 4-day work week increases output by 22%",
            "Open-source LLM beats GPT-4 on coding benchmarks",
            "NASA confirms liquid water lake beneath Mars surface",
            "Rust overtakes C++ in Linux kernel contributions",
            "France bans TikTok on all government devices",
            "Scientists grow functional human kidney in lab",
            "Europe's AI Act enforcement begins — what it means",
        ],
        "score":        [98400, 74200, 61300, 52100, 44800, 38600, 31200, 27900, 24500, 19800],
        "subreddit":    ["technology","python","space","science","MachineLearning",
                         "space","programming","worldnews","science","technology"],
        "num_comments": [3420, 2180, 1940, 1620, 1380, 1100, 890, 760, 640, 510],
        "url":          ["https://reddit.com"] * 10
    })

def _sample_hackernews():
    return pd.DataFrame({
        "title": [
            "Show HN: I built a terminal-native code review tool",
            "The unreasonable effectiveness of just showing up",
            "Why I rewrote our backend in Go (from Node.js)",
            "SQLite is not a toy database",
            "Ask HN: How do you structure a 1-person startup?",
            "Htmx 2.0 released",
            "The future of the web is local-first",
            "Anthropic's new paper on long-context reasoning",
            "Postgres full-text search is good enough",
            "I quit FAANG after 8 years. Here's what I learned.",
        ],
        "score": [1240, 987, 834, 756, 698, 612, 589, 534, 498, 445],
        "by":    ["user1","user2","user3","user4","user5",
                  "user6","user7","user8","user9","user10"],
        "url":   ["https://news.ycombinator.com"] * 10,
        "time":  [1700000000] * 10
    })

def _sample_github():
    return pd.DataFrame({
        "name":      ["ollama","open-interpreter","surya","screenshot-to-code","fabric"],
        "full_name": ["ollama/ollama","KillianLucas/open-interpreter",
                      "VikParuchuri/surya","abi/screenshot-to-code","danielmiessler/fabric"],
        "description": [
            "Run Llama 3, Mistral, Gemma locally",
            "A natural language interface for your computer",
            "OCR and layout analysis for any language",
            "Turn screenshots into clean HTML/Tailwind/React",
            "Augmenting humans using AI patterns"
        ],
        "stars":    [52000, 43000, 38000, 31000, 27000],
        "forks":    [4100, 3800, 2900, 2400, 1800],
        "language": ["Go","Python","Python","TypeScript","Go"],
        "url":      [
            "https://github.com/ollama/ollama",
            "https://github.com/KillianLucas/open-interpreter",
            "https://github.com/VikParuchuri/surya",
            "https://github.com/abi/screenshot-to-code",
            "https://github.com/danielmiessler/fabric"
        ]
    })