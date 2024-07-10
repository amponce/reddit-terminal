import os
import praw
import requests
from bs4 import BeautifulSoup
import prawcore
from dotenv import load_dotenv
from .models import Post

class RedditClient:
    def __init__(self):
        load_dotenv()
        self.use_api = all([os.getenv('REDDIT_CLIENT_ID'), os.getenv('REDDIT_CLIENT_SECRET'), os.getenv('REDDIT_USER_AGENT')])
        if self.use_api:
            self.reddit = self._authenticate()
        else:
            print("API credentials not found. Using web scraping.")

    def _authenticate(self):
        try:
            reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=os.getenv('REDDIT_USER_AGENT')
            )
            reddit.user.me()
            return reddit
        except prawcore.exceptions.ResponseException:
            print("Error authenticating with Reddit API. Falling back to web scraping.")
        except Exception as e:
            print(f"An error occurred: {e}. Falling back to web scraping.")
        self.use_api = False
        return None

    def get_posts(self, subreddit_name: str = None, sort: str = 'hot', limit: int = 10):
        try:
            if self.use_api:
                subreddit = self.reddit.subreddit(subreddit_name) if subreddit_name else self.reddit.front
                sorting = {
                    'hot': subreddit.hot,
                    'new': subreddit.new,
                    'top': subreddit.top
                }
                posts = sorting.get(sort, subreddit.hot)(limit=limit)
                return [Post(post.title, post.score, post.author.name if post.author else '[deleted]', post.num_comments, post.url, post.id, post.selftext) for post in posts]
            else:
                return self.scrape_posts(subreddit_name)
        except Exception as e:
            print(f"Error in get_posts: {e}")
            return []

    def scrape_posts(self, subreddit_name: str = None):
        url = f"https://www.reddit.com/r/{subreddit_name}/hot" if subreddit_name else "https://www.reddit.com/hot"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        posts = []
        for post in soup.find_all('div', class_='thing'):
            title = post.find('a', class_='title').text.strip()
            score = post.find('div', class_='score unvoted').text.strip()
            score = 0 if score == '' else int(score)  # Ensure score is parsed correctly
            author = post.find('a', class_='author').text.strip()
            num_comments = post.find('a', class_='comments').text.split()[0]
            url = 'https://www.reddit.com' + post.find('a', class_='comments')['href']
            text = post.find('div', class_='expando').text.strip() if post.find('div', class_='expando') else ''
            posts.append(Post(title, score, author, num_comments, url, text=text))
        return posts[:10]

    def get_post_content(self, post):
        if self.use_api:
            full_post = self.reddit.submission(id=post.id)
            post.selftext = full_post.selftext
            post.score = full_post.score
            post.num_comments = full_post.num_comments
            post.created_utc = full_post.created_utc
        else:
            response = requests.get(post.url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.text, 'html.parser')
            post.selftext = soup.find('div', class_='usertext-body').text.strip() if soup.find('div', class_='usertext-body') else ''
            post.score = int(soup.find('div', class_='score unvoted').text.strip()) if soup.find('div', class_='score unvoted') else 0
            post.num_comments = int(soup.find('a', class_='comments').text.split()[0]) if soup.find('a', class_='comments') else 0
        return post