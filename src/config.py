# config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Reddit API credentials
    REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')

    # OpenAI API key
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # Application settings
    DEFAULT_SUBREDDIT = None  # Front page
    DEFAULT_POST_LIMIT = 10
    DEFAULT_POST_SORT = 'hot'
    DEFAULT_COMMENT_SORT = 'best'

    # Feature flags
    USE_AI_FEATURES = bool(OPENAI_API_KEY)

    @classmethod
    def is_reddit_api_configured(cls):
        return all([cls.REDDIT_CLIENT_ID, cls.REDDIT_CLIENT_SECRET, cls.REDDIT_USER_AGENT])

config = Config()