#  Trending Now Dashboard

A real-time dashboard that tracks trending content from Reddit, Hacker News, and GitHub, with sentiment analysis and keyword extraction.

##  Live Demo
[View the Live Dashboard]([https://trending-now-dashboard-lqxsbj98m8rxfm8qhdfnvs.streamlit.app/](https://trending-now-dashboard-hb7b3wecn2vnw73zsdjqk9.streamlit.app/))

##  Features

- **Real-time Data**: Fetches trending posts from Reddit, Hacker News, and GitHub
- **Sentiment Analysis**: Analyzes post titles to determine positive/negative sentiment
- **Keyword Extraction**: Identifies trending topics and keywords
- **Interactive Visualizations**: Bar charts, pie charts, and word clouds
- **Auto-refresh**: Data updates every 10 minutes
- **Responsive Design**: Works on desktop and mobile

##  Technologies Used

- **Python** - Core programming language
- **Streamlit** - Web app framework
- **Plotly** - Interactive charts and visualizations
- **Pandas** - Data manipulation and analysis
- **VADER** - Sentiment analysis
- **Requests** - API calls to Reddit, Hacker News, GitHub
- **WordCloud** - Visual text analysis

##  Installation

```bash
# Clone the repository
git clone https://github.com/dhaouadieee-sketch/trending-now-dashboard.git

# Navigate to project directory
cd trending-now-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the app locally
streamlit run dashboard/app.py
