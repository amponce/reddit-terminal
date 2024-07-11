
from reddit_client import RedditClient
from search import search_and_summarize
from ai_analysis import AIClient
from config import config
import builtins

# Mock input to automate feedback
original_input = builtins.input

def mock_input(prompt):
    print(prompt)
    return '5'

builtins.input = mock_input

# Initialize the Reddit and AI clients
reddit_client = RedditClient()
ai_client = AIClient(config.OPENAI_API_KEY) if config.USE_AI_FEATURES else None

# Define a test query
query = 'example search query'

# Perform the search with a specified subreddit
print('=== Search with specific subreddit (askreddit) ===')
search_and_summarize(reddit_client, ai_client, query, 'askreddit')

# Perform the search without specifying a subreddit
print('=== Search without specific subreddit ===')
search_and_summarize(reddit_client, ai_client, query)

# Restore original input
builtins.input = original_input
