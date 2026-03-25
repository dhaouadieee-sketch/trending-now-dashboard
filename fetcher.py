import requests
import pandas as pd

def fetch_reddit(subreddit="all", limit=25):
    url = f"https://www.reddit.com/r/{subreddit}/top.json?limit={limit}&t=day"
    headers = {"User-Agent": "trending-dashboard/1.0"}
    response = requests.get(url, headers=headers)
    posts = response.json()["data"]["children"]
    data = []
    for post in posts:
        p = post["data"]
        data.append({
            "title": p["title"],
            "score": p["score"],
            "subreddit": p["subreddit"],
            "url": p["url"]
        })
    return pd.DataFrame(data)

# ── Hacker News ─────────────────────────────────────────
def fetch_hackernews(limit=25):
    top_ids = requests.get(
        "https://hacker-news.firebaseio.com/v0/topstories.json"
    ).json()[:limit]
    data = []
    for story_id in top_ids:
        story = requests.get(
            f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        ).json()
        if story and "title" in story:
            data.append({
                "title": story.get("title", ""),
                "score": story.get("score", 0),
                "url": story.get("url", "")
            })
    return pd.DataFrame(data)

# ── GitHub Trending ──────────────────────────────────────
def fetch_github_trending():
    from bs4 import BeautifulSoup
    url = "https://github.com/trending"
    headers = {"User-Agent": "trending-dashboard/1.0"}
    soup = BeautifulSoup(requests.get(url, headers=headers).text, "html.parser")
    repos = soup.select("article.Box-row")
    data = []
    for repo in repos:
        name = repo.select_one("h2 a")
        stars = repo.select_one("span.d-inline-block.float-sm-right")
        desc = repo.select_one("p")
        data.append({
            "repo": name.get_text(strip=True).replace("\n","").replace(" ","") if name else "",
            "stars": stars.get_text(strip=True) if stars else "0",
            "description": desc.get_text(strip=True) if desc else ""
        })
    return pd.DataFrame(data)