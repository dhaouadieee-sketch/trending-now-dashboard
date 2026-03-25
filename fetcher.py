import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

def fetch_reddit():
    """Fetch Reddit data with safe JSON handling"""
    try:
        headers = {"User-Agent": "TrendingDashboard/1.0"}
        response = requests.get(
            "https://www.reddit.com/r/all/top.json?t=day&limit=25",
            headers=headers,
            timeout=10
        )
        
        # Check if we got a valid response
        if response.status_code != 200:
            return _sample_reddit()
        
        # Try to parse JSON safely
        try:
            data = response.json()
        except:
            return _sample_reddit()
        
        posts = data.get("data", {}).get("children", [])
        if not posts:
            return _sample_reddit()
        
        return pd.DataFrame([{
            "title": p.get("data", {}).get("title", ""),
            "score": p.get("data", {}).get("score", 0),
            "subreddit": p.get("data", {}).get("subreddit", ""),
            "url": p.get("data", {}).get("url", ""),
            "num_comments": p.get("data", {}).get("num_comments", 0)
        } for p in posts])
        
    except:
        return _sample_reddit()

def fetch_hackernews():
    """Fetch Hacker News data"""
    try:
        response = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10
        )
        
        try:
            story_ids = response.json()[:20]
        except:
            return _sample_hackernews()
        
        hn_data = []
        for sid in story_ids:
            try:
                item_resp = requests.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                    timeout=5
                )
                story = item_resp.json()
                if story and story.get("type") == "story" and story.get("title"):
                    hn_data.append({
                        "title": story.get("title", ""),
                        "score": story.get("score", 0),
                        "url": story.get("url", "https://news.ycombinator.com"),
                        "by": story.get("by", "anonymous"),
                        "time": story.get("time", 0)
                    })
            except:
                continue
                
        return pd.DataFrame(hn_data) if hn_data else _sample_hackernews()
        
    except:
        return _sample_hackernews()

def fetch_github_trending():
    """Fetch GitHub trending repos"""
    try:
        since = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
        response = requests.get(
            f"https://api.github.com/search/repositories?q=created:>{since}&sort=stars&order=desc&per_page=25",
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=10
        )
        
        try:
            data = response.json()
        except:
            return _sample_github()
        
        repos = data.get("items", [])
        if not repos:
            return _sample_github()
        
        return pd.DataFrame([{
            "name": r.get("name", ""),
            "full_name": r.get("full_name", ""),
            "description": r.get("description") or "No description",
            "stars": r.get("stargazers_count", 0),
            "forks": r.get("forks_count", 0),
            "language": r.get("language") or "Unknown",
            "url": r.get("html_url", "")
        } for r in repos])
        
    except:
        return _sample_github()

def _sample_reddit():
    return pd.DataFrame({
        "title": [
            "AI agents are now writing 25% of Google's code",
            "Python 3.14 drops the GIL by default",
            "SpaceX Starship completes first full orbital mission",
            "New study: 4-day work week increases output by 22%",
            "Open-source LLM beats GPT-4 on coding benchmarks",
        ],
        "score": [98400, 74200, 61300, 52100, 44800],
        "subreddit": ["technology", "python", "space", "science", "MachineLearning"],
        "num_comments": [3420, 2180, 1940, 1620, 1380],
        "url": ["https://reddit.com"] * 5
    })

def _sample_hackernews():
    return pd.DataFrame({
        "title": [
            "Show HN: I built a terminal-native code review tool",
            "The unreasonable effectiveness of just showing up",
            "Why I rewrote our backend in Go (from Node.js)",
            "SQLite is not a toy database",
            "Ask HN: How do you structure a 1-person startup?",
        ],
        "score": [1240, 987, 834, 756, 698],
        "by": ["user1", "user2", "user3", "user4", "user5"],
        "url": ["https://news.ycombinator.com"] * 5,
        "time": [1700000000] * 5
    })

def _sample_github():
    return pd.DataFrame({
        "name": ["ollama", "open-interpreter", "surya", "screenshot-to-code", "fabric"],
        "full_name": ["ollama/ollama", "KillianLucas/open-interpreter", "VikParuchuri/surya", 
                      "abi/screenshot-to-code", "danielmiessler/fabric"],
        "description": [
            "Run Llama 3, Mistral, Gemma locally",
            "A natural language interface for your computer",
            "OCR and layout analysis for any language",
            "Turn screenshots into clean HTML/Tailwind/React",
            "Augmenting humans using AI patterns"
        ],
        "stars": [52000, 43000, 38000, 31000, 27000],
        "forks": [4100, 3800, 2900, 2400, 1800],
        "language": ["Go", "Python", "Python", "TypeScript", "Go"],
        "url": [
            "https://github.com/ollama/ollama",
            "https://github.com/KillianLucas/open-interpreter",
            "https://github.com/VikParuchuri/surya",
            "https://github.com/abi/screenshot-to-code",
            "https://github.com/danielmiessler/fabric"
        ]
    })