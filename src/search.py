# search.py

from concurrent.futures import ThreadPoolExecutor, as_completed

def search_reddit(reddit_client, query, subreddit=None, time_filter='all', min_comments=0, min_score=0):
    if reddit_client.use_api:
        if subreddit:
            results = list(reddit_client.reddit.subreddit(subreddit).search(query, time_filter=time_filter, limit=50))
        else:
            results = list(reddit_client.reddit.subreddit('all').search(query, time_filter=time_filter, limit=50))
        
        filtered_results = [
            post for post in results
            if post.num_comments >= min_comments and post.score >= min_score
        ]
        return filtered_results[:5]
    else:
        print("Search functionality not available without API access.")
        return []

def fetch_post_comments(post):
    post.comments.replace_more(limit=0)
    return [comment.body for comment in post.comments.list() if len(comment.body) > 50]

def search_and_summarize(reddit_client, ai_client, query, subreddit=None):
    if subreddit and subreddit.lower() != 'askreddit':
        print("This feature is currently optimized for AskReddit but will perform a global search.")
    
    posts = search_reddit(reddit_client, query, subreddit)
    if not posts:
        print("No relevant posts found.")
        return

    print(f"\nTop 5 relevant posts for '{query}':\n")

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_post = {executor.submit(fetch_post_comments, post): post for post in posts[:5]}
        for future in as_completed(future_to_post):
            post = future_to_post[future]
            try:
                comments = future.result()
                summary = ai_client.summarize_comments(comments, post.title, subreddit or 'all')
                print(f"Title: {post.title}")
                print(f"Summary: {summary}\n")
                rating = get_feedback()
                print(f"Received rating: {rating}")
                topics = ai_client.extract_topics(comments)
                display_topics(topics)
            except Exception as exc:
                print(f"An error occurred while processing a post: {exc}")

def get_feedback():
    while True:
        feedback = input("Rate this summary (1-5): ")
        try:
            rating = int(feedback)
            if 1 <= rating <= 5:
                return rating
            else:
                print("Please enter a rating between 1 and 5.")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 5.")

def display_topics(topics):
    for idx, topic in enumerate(topics):
        print(f"Topic {idx+1}: {', '.join(topic)}")