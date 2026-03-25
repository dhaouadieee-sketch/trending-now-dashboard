import requests
import pandas as pd
import streamlit as st

def fetch_reddit():
    """Fetch trending posts from Reddit"""
    try:
        # Reddit API headers (required for all requests)
        headers = {
            'User-Agent': 'TrendingNowDashboard/1.0 (by /u/trendingdashboard)'
        }
        
        # Try to get from Reddit's public JSON endpoint
        url = "https://www.reddit.com/r/all/top.json?t=day&limit=25"
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get("data", {}).get("children", [])
            
            reddit_data = []
            for post in posts:
                post_data = post.get("data", {})
                reddit_data.append({
                    "title": post_data.get("title", ""),
                    "score": post_data.get("score", 0),
                    "subreddit": post_data.get("subreddit", ""),
                    "url": post_data.get("url", ""),
                    "num_comments": post_data.get("num_comments", 0)
                })
            
            return pd.DataFrame(reddit_data)
        else:
            st.warning(f"Reddit API returned status {response.status_code}. Using sample data.")
            return get_sample_reddit_data()
            
    except Exception as e:
        st.error(f"Error fetching Reddit data: {str(e)}")
        return get_sample_reddit_data()

def fetch_hackernews():
    """Fetch top stories from Hacker News"""
    try:
        # Get top stories IDs
        response = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        
        if response.status_code == 200:
            story_ids = response.json()[:25]  # Get top 25
            
            hn_data = []
            for story_id in story_ids:
                story_response = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=10)
                if story_response.status_code == 200:
                    story = story_response.json()
                    if story:
                        hn_data.append({
                            "title": story.get("title", ""),
                            "score": story.get("score", 0),
                            "url": story.get("url", ""),
                            "by": story.get("by", ""),
                            "time": story.get("time", 0)
                        })
            
            return pd.DataFrame(hn_data)
        else:
            st.warning("Hacker News API error. Using sample data.")
            return get_sample_hackernews_data()
            
    except Exception as e:
        st.error(f"Error fetching Hacker News data: {str(e)}")
        return get_sample_hackernews_data()

def fetch_github_trending():
    """Fetch trending repositories from GitHub"""
    try:
        url = "https://api.github.com/search/repositories?q=stars:>100&sort=stars&order=desc&per_page=25"
        headers = {'Accept': 'application/vnd.github.v3+json'}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            repos = response.json().get("items", [])
            
            github_data = []
            for repo in repos:
                github_data.append({
                    "name": repo.get("name", ""),
                    "full_name": repo.get("full_name", ""),
                    "description": repo.get("description", ""),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "language": repo.get("language", ""),
                    "url": repo.get("html_url", "")
                })
            
            return pd.DataFrame(github_data)
        else:
            st.warning("GitHub API error. Using sample data.")
            return get_sample_github_data()
            
    except Exception as e:
        st.error(f"Error fetching GitHub data: {str(e)}")
        return get_sample_github_data()

def get_sample_reddit_data():
    """Return sample Reddit data for testing"""
    return pd.DataFrame({
        "title": [
            "Amazing AI breakthrough in 2024",
            "Python 3.13 released with major improvements",
            "New framework for data visualization",
            "Machine Learning trends to watch",
            "Open source community growing rapidly"
        ],
        "score": [15420, 8920, 5430, 3210, 2100],
        "subreddit": ["technology", "python", "datascience", "machinelearning", "opensource"],
        "num_comments": [450, 230, 120, 89, 67]
    })

def get_sample_hackernews_data():
    """Return sample Hacker News data for testing"""
    return pd.DataFrame({
        "title": [
            "Show HN: A new way to build web apps",
            "The future of programming",
            "Understanding Large Language Models",
            "Why Python dominates data science",
            "Open source sustainability"
        ],
        "score": [342, 289, 245, 198, 167],
        "by": ["user1", "user2", "user3", "user4", "user5"],
        "time": [1700000000, 1700000100, 1700000200, 1700000300, 1700000400]
    })

def get_sample_github_data():
    """Return sample GitHub data for testing"""
    return pd.DataFrame({
        "name": ["awesome-project", "ml-library", "web-framework", "data-tools", "devops-tools"],
        "full_name": ["user/awesome-project", "user/ml-library", "user/web-framework", "user/data-tools", "user/devops-tools"],
        "description": [
            "A collection of awesome resources",
            "Machine learning library for Python",
            "Modern web framework",
            "Data analysis tools",
            "DevOps automation tools"
        ],
        "stars": [12500, 8900, 7600, 5400, 4300],
        "forks": [2300, 1450, 1200, 890, 670],
        "language": ["Python", "Python", "JavaScript", "Python", "Go"]
    })