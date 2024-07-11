import os
import praw
import prawcore
from dotenv import load_dotenv
from .models import Post, Comment

class RedditClient:
    def __init__(self, use_api=True):
        self.use_api = use_api

        load_dotenv()
        self.reddit = self._authenticate()

    def _authenticate(self):
        try:
            reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=os.getenv('REDDIT_USER_AGENT')
            )
            reddit.user.me()
            return reddit
        except prawcore.exceptions.ResponseException as e:
            print(f"Error authenticating with Reddit API: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
        return None

    def get_posts(self, subreddit_name: str = None, sort: str = 'hot', limit: int = 10):
        try:
            if self.reddit:
                subreddit = self.reddit.subreddit(subreddit_name) if subreddit_name else self.reddit.front
                sorting = {
                    'hot': subreddit.hot,
                    'new': subreddit.new,
                    'top': subreddit.top
                }
                posts = sorting.get(sort, subreddit.hot)(limit=limit)
                return [Post(post.title, post.score, post.author.name if post.author else '[deleted]', post.num_comments, post.url, post.id, post.selftext) for post in posts]
            else:
                print("Reddit API not authenticated.")
                return []
        except prawcore.exceptions.RequestException as e:
            print(f"Error in get_posts: {e}. HTTP Status: {e.response.status_code}")
            return []
        except Exception as e:
            print(f"Error in get_posts: {e}")
            return []

    def get_post_content(self, post):
        if self.reddit:
            full_post = self.reddit.submission(id=post.id)
            post.selftext = full_post.selftext
            post.score = full_post.score
            post.num_comments = full_post.num_comments
            post.created_utc = full_post.created_utc
        return post

    def get_comments(self, post, max_comments=50):
        try:
            if self.reddit:
                submission = self.reddit.submission(id=post.id)
                submission.comments.replace_more(limit=0)  # Fetch all comments
                comments = []
                for top_level_comment in submission.comments[:max_comments]:
                    comments.append(Comment(
                        author=top_level_comment.author.name if top_level_comment.author else '[deleted]',
                        score=top_level_comment.score,
                        body=top_level_comment.body[:500],  # Truncate long comments
                        depth=top_level_comment.depth,
                        id=top_level_comment.id
                    ))
                return comments
            else:
                print("Reddit API not authenticated.")
                return []
        except Exception as e:
            print(f"Error in get_comments: {e}")
            return []