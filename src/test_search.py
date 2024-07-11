from reddit_client import RedditClient
from search import search_reddit

# Initialize the Reddit client
reddit_client = RedditClient()

# Define a test query
test_query = 'example search query'

# Perform the search
results = search_reddit(reddit_client, test_query)

# Print the results
for idx, post in enumerate(results):
    print(f'{idx + 1}: {post.title} (Comments: {post.num_comments}, Score: {post.score})')
