import praw
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import prawcore
from rich import print
from rich.console import Console
from rich.table import Table
from rich.text import Text
import textwrap
import webbrowser
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class RedditClient:
    def __init__(self):
        self.console = Console()
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

    def color_score(self, score: int) -> Text:
        if score > 0:
            return Text(str(score), style="bold green")
        elif score < 0:
            return Text(str(score), style="bold red")
        else:
            return Text(str(score), style="bold yellow")

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
                return [Post(post.title, post.score, post.author.name if post.author else '[deleted]', post.num_comments, post.url, post.id) for post in posts]
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
            posts.append(Post(title, score, author, num_comments, url))
        return posts[:10]

    def display_posts(self, posts: list):
        table = Table(title="Reddit Posts")
        table.add_column("No.", style="cyan", no_wrap=True)
        table.add_column("Title", style="magenta")
        table.add_column("Score", style="bold")
        table.add_column("Author", style="yellow")
        table.add_column("Comments", style="blue")

        for i, post in enumerate(posts, 1):
            table.add_row(str(i), 
                          textwrap.shorten(post.title, width=60), 
                          self.color_score(post.score),
                          post.author, 
                          str(post.num_comments))

        self.console.print(table)

    def display_post_details(self, post):
        table = Table(title="Post Details")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")

        table.add_row("Title", post.title)
        table.add_row("Score", self.color_score(post.score))
        table.add_row("Author", post.author)
        table.add_row("Comments", str(post.num_comments))
        table.add_row("URL", post.url)

        self.console.print(table)


class Post:
    def __init__(self, title, score, author, num_comments, url, id=None):
        self.title = title
        self.score = score
        self.author = author
        self.num_comments = num_comments
        self.url = url
        self.id = id


class Comment:
    def __init__(self, author, score, body, depth=0, id=None):
        self.id = id
        self.author = author if author else '[deleted]'
        self.score = score
        self.body = body
        self.depth = depth
        self.children = []
        self.collapsed = False  # Start expanded by default
        self.has_more_replies = False
        self.is_root = depth == 0

def flatten_comments(comments):
    for comment in comments:
        yield comment
        yield from flatten_comments(comment.children)

def toggle_comment(action, comment_number):
    try:
        comment_index = int(comment_number) - 1
        if 0 <= comment_index < len(current_comments):
            comment = current_comments[comment_index]
            comment.collapsed = action == 'collapse'
            display_threaded_comments(current_comments, 0, 100, comment_sort_method)
        else:
            print("Invalid comment number.")
    except (ValueError, IndexError):
        print(f"Invalid {action} command. Use '{action[0]} <number>'.")

def display_comment(comment, console, number, comment_map):
    indent = "  " * comment.depth
    collapse_symbol = "[-]" if not comment.collapsed else "[+]"
    console.print(f"{indent}{collapse_symbol} [cyan]{number}.[/cyan] [yellow]{comment.author}[/yellow] [green](Score: {comment.score})[/green]")
    
    if not comment.collapsed:
        wrapped_body = textwrap.fill(comment.body, width=80-len(indent), initial_indent=indent, subsequent_indent=indent)
        console.print(wrapped_body)
    
    if comment.children:
        reply_count = sum(1 for _ in flatten_comments(comment.children))
        if comment.collapsed or comment.is_root:
            console.print(f"{indent}  [blue]{reply_count} repl{'y' if reply_count == 1 else 'ies'}[/blue]")
    
    if not comment.collapsed:
        for i, child in enumerate(comment.children, start=1):
            display_comment(child, console, f"{number}.{i}", comment_map)

def display_threaded_comments(comments, start=0, count=10, sort_method='best'):
    global current_comments
    current_comments = sort_comments(comments, sort_method)
    console = Console()
    displayed = 0
    comment_map = {i: comment for i, comment in enumerate(current_comments, start=1)}
    for i, comment in enumerate(current_comments[start:], start=1):
        if displayed >= count:
            break
        display_comment(comment, console, i, comment_map)
        displayed += 1
    console.print("\nEnter 'e <number>' to expand or 'c <number>' to collapse a comment thread.")
    return displayed

def view_post(post_index):
    global current_comments, comment_page, selected_post_index
    if 0 <= post_index < len(current_posts):
        post = current_posts[post_index]
        current_comments = get_comments(post)
        comment_page = 0
        selected_post_index = post_index
        reddit_client.display_post_details(post)
        display_post_and_comments(post)
    else:
        print(f"Invalid post number. Please enter a number between 1 and {len(current_posts)}.")

def get_comments(post):
    global reddit_client
    if reddit_client.use_api:
        praw_post = reddit_client.reddit.submission(id=post.id)
        praw_post.comments.replace_more(limit=0)
        comments = praw_post.comments.list()
        return [Comment(
            comment.author.name if comment.author else '[deleted]',
            comment.score,
            comment.body,
            comment.depth,
            comment.id
        ) for comment in comments]
    else:
        return scrape_comments(post.url)      

def scrape_comments(post_url):
    response = requests.get(post_url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')
    comments = []
    for comment in soup.find_all('div', class_='comment'):
        author = comment.find('a', class_='author').text.strip() if comment.find('a', class_='author') else '[deleted]'
        score = comment.find('span', class_='score unvoted').text.strip() if comment.find('span', class_='score unvoted') else '0'
        score = 0 if score == '' else int(score)  # Ensure score is parsed correctly
        body = comment.find('div', class_='md').text.strip() if comment.find('div', class_='md') else ''
        depth = len(comment.find_parents('div', class_='comment'))
        comments.append(Comment(author, score, body, depth))
    return comments  

def display_post_and_comments(post):
    console = Console()
    console.print(f"\n[bold magenta]Title:[/bold magenta] {post.title}")
    console.print(f"[bold yellow]Author:[/bold yellow] {post.author}")
    console.print(f"[bold green]Score:[/bold green] {reddit_client.color_score(post.score)}")
    console.print(f"[bold blue]URL:[/bold blue] {post.url}")
    console.print("\n[bold]Comments:[/bold]")
    display_threaded_comments(current_comments, comment_page * 10, 10)
    console.print("\nType 'n' for next page, 'p' for previous page, or 'b' to go back to posts.")

def navigate_comments(direction):
    global comment_page, selected_post_index
    if direction == 'next':
        comment_page += 1
    elif direction == 'prev' and comment_page > 0:
        comment_page -= 1
    display_post_and_comments(current_posts[selected_post_index])

def sort_comments(comments, method='best'):
    if method == 'best':
        return sorted(comments, key=lambda c: c.score, reverse=True)
    elif method == 'new':
        return comments  # Assuming comments are already in chronological order
    elif method == 'controversial':
        return sorted(comments, key=lambda c: abs(c.score), reverse=True)
    else:
        return comments

def search_reddit(query, subreddit=None, time_filter='all', min_comments=0, min_score=0):
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

def summarize_comments(comments, post_title, subreddit):
    prompt = (
        f"Summarize the following Reddit comments on the post titled '{post_title}' "
        f"in the subreddit '{subreddit}':\n\n"
        f"{' '.join(comments[:5])}\n\nSummary:"
    )
    response = client.chat.completions.create(model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=150,
    n=1,
    stop=None,
    temperature=0.7)
    return response.choices[0].message.content.strip()

def get_feedback():
    feedback = input("Rate this summary (1-5): ")
    try:
        rating = int(feedback)
        if 1 <= rating <= 5:
            return rating
        else:
            print("Please enter a rating between 1 and 5.")
            return get_feedback()
    except ValueError:
        print("Invalid input. Please enter a number between 1 and 5.")
        return get_feedback()

def extract_topics(comments):
    vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words='english')
    tfidf = vectorizer.fit_transform(comments)
    nmf = NMF(n_components=5, random_state=1).fit(tfidf)
    feature_names = vectorizer.get_feature_names_out()
    topics = []
    for topic_idx, topic in enumerate(nmf.components_):
        topic_keywords = [feature_names[i] for i in topic.argsort()[:-6:-1]]
        topics.append(topic_keywords)
    return topics

def display_topics(topics):
    console = Console()
    for idx, topic in enumerate(topics):
        console.print(f"Topic {idx+1}: {', '.join(topic)}")

def interactive_summary(query, subreddit):
    posts = search_reddit(query, subreddit)
    if not posts:
        print("No relevant posts found.")
        return

    console = Console()
    console.print(f"\n[bold]Top 5 relevant posts for '{query}':[/bold]\n")

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_post = {executor.submit(fetch_post_comments, post): post for post in posts[:5]}
        for future in as_completed(future_to_post):
            post = future_to_post[future]
            try:
                comments = future.result()
                summary = summarize_comments(comments, post.title, subreddit)
                display_interactive_summary(post, summary)
                command = input("Enter a command: ").lower()
                if command == 'details':
                    display_threaded_comments(comments)
                elif command == 'back':
                    console.clear()
                    break
            except Exception as exc:
                print(f"An error occurred while processing a post: {exc}")

def display_interactive_summary(post, summary):
    console = Console()
    console.print(f"[bold magenta]{post.title}[/bold magenta]")
    console.print(f"[italic]{summary}[/italic]\n")
    console.print(f"[blue]URL: {post.url}[/blue]")
    console.print("\n[bold]Type 'details' to see the full comments or 'back' to return to the post list.[/bold]")

def search_and_summarize(query, subreddit=None):
    if subreddit and subreddit.lower() != 'askreddit':
        print("This feature is currently optimized for AskReddit but will perform a global search.")
    
    posts = search_reddit(query, subreddit)
    if not posts:
        print("No relevant posts found.")
        return

    console = Console()
    console.print(f"\n[bold]Top 5 relevant posts for '{query}':[/bold]\n")

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_post = {executor.submit(fetch_post_comments, post): post for post in posts[:5]}
        for future in as_completed(future_to_post):
            post = future_to_post[future]
            try:
                comments = future.result()
                summary = summarize_comments(comments, post.title, subreddit or 'all')
                console.print(f"[bold magenta]{post.title}[/bold magenta]")
                console.print(f"[italic]{summary}[/italic]\n")
                rating = get_feedback()
                print(f"Received rating: {rating}")
                topics = extract_topics(comments)
                display_topics(topics)
            except Exception as exc:
                print(f"An error occurred while processing a post: {exc}")


# The main loop remains the same
def main():
    global reddit_client, current_subreddit, current_posts, current_comments, post_limit, post_sort_method, comment_sort_method, comment_page, selected_post_index
    reddit_client = RedditClient()
    current_subreddit = None
    current_posts = []
    current_comments = []
    post_limit = 10
    post_sort_method = 'hot'
    comment_sort_method = 'best'
    comment_page = 0
    selected_post_index = None

    def refresh_posts():
        global current_posts
        current_posts = reddit_client.get_posts(current_subreddit, post_sort_method, post_limit)
        reddit_client.display_posts(current_posts)

    def change_subreddit(new_subreddit: str):
        global current_subreddit
        current_subreddit = new_subreddit if new_subreddit else None
        refresh_posts()

    def change_post_sort(new_sort: str):
        global post_sort_method
        if new_sort in ['hot', 'new', 'top']:
            post_sort_method = new_sort
            refresh_posts()
        else:
            print("Invalid sort method. Use 'hot', 'new', or 'top'.")

    def change_post_limit(new_limit: str):
        global post_limit
        try:
            post_limit = int(new_limit)
            refresh_posts()
        except ValueError:
            print("Invalid limit. Please enter a number.")

    # Initial post fetch
    refresh_posts()

    while True:
        print(f"\nCurrent subreddit: {current_subreddit or 'Front Page'} | Post sort: {post_sort_method} | Limit: {post_limit}")
        command = input("Enter a command: ").lower().split()

        if not command:
            continue

        if command[0] == 'q':
            break
        elif command[0] == '/help':
            display_help()
        elif command[0] == '/sub':
            change_subreddit(command[1] if len(command) > 1 else None)
        elif command[0] == '/sort':
            change_post_sort(command[1] if len(command) > 1 else 'hot')
        elif command[0] == '/limit':
            change_post_limit(command[1] if len(command) > 1 else '10')
        elif command[0].isdigit():
            view_post(int(command[0]) - 1)
        elif command[0] == 'n':
            navigate_comments('next')
        elif command[0] == 'p':
            navigate_comments('prev')
        elif command[0] == 'b':
            refresh_posts()
        elif command[0] == 'o':
            if selected_post_index is not None and hasattr(current_posts[selected_post_index], 'url'):
                open_in_browser(current_posts[selected_post_index].url)
                print(f"Opening {current_posts[selected_post_index].url} in your default browser.")
            else:
                print("No post selected or URL available.")
        elif command[0] in ['e', 'c']:
            toggle_comment('expand' if command[0] == 'e' else 'collapse', command[1] if len(command) > 1 else '')
        elif command[0] == 'sort':
            change_comment_sort(command[1] if len(command) > 1 else 'best')
        elif command[0] == 'more':
            print("Fetching more comments... (Not implemented)")
        elif command[0] == 'collapse_all':
            for comment in current_comments:
                comment.collapsed = True
            display_threaded_comments(current_comments, 0, 100, comment_sort_method)
        elif command[0] == 's':
            query = ' '.join(command[1:]) if len(command) > 1 else input("Enter your search query: ")
            search_and_summarize(query, current_subreddit)
        else:
            print("Invalid command. Type '/help' for a list of available commands.")


def display_help():
    help_text = """
    Available commands:

    /help               - Display this help message
    
    /sub <subreddit>    - Change to a specific subreddit (e.g., /sub AskReddit)
    /sort <method>      - Change the post sorting method. Options: hot, new, top
    /limit <number>     - Change the number of posts displayed
    <number>            - View a specific post and its comments
    n                   - View next page of comments
    p                   - View previous page of comments
    b                   - Go back to post list
    o                   - Open the current post's URL in your default web browser
    e <number>          - Expand a specific comment thread
    c <number>          - Collapse a specific comment thread
    sort <method>       - Sort comments. Options: best, new, controversial
    collapse_all        - Collapse all comments to show only root-level comments
    more                - Show more comments (not implemented)
    q                   - Quit the program
    s                   - Search and summarize (available globally)

    Notes:
    - If no subreddit is specified, the front page will be shown.
    - The default post sort method is 'hot'.
    - The default comment sort method is 'best'.
    - The default post limit is 10.
    - The search and summarize feature can now be used globally.
    - You need to set up your OpenAI API key in the .env file for the summarize feature to work.

    """
    print(help_text)


if __name__ == "__main__":
    main()
