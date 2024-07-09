# display.py

from rich.console import Console
from rich.table import Table
from rich.text import Text
import textwrap

class ConsoleUI:
    def __init__(self):
        self.console = Console()

    def color_score(self, score: int) -> Text:
        if score > 0:
            return Text(str(score), style="bold green")
        elif score < 0:
            return Text(str(score), style="bold red")
        else:
            return Text(str(score), style="bold yellow")

    def print_status(self, current_subreddit, post_sort_method, post_limit):
        status_table = Table(title="Current Status", show_header=False, box=None)
        status_table.add_column("Field", style="cyan")
        status_table.add_column("Value", style="magenta")

        status_table.add_row("Subreddit", current_subreddit or "Front Page")
        status_table.add_row("Sort Method", post_sort_method)
        status_table.add_row("Post Limit", str(post_limit))

        self.console.print(status_table)
        self.console.print("")  # Add an empty line for better readability

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

    def display_post_and_comments(self, post, comments, comment_page):
        self.console.print("\n[bold]Comments:[/bold]")
        self.display_threaded_comments(comments, comment_page * 10, 10)
        self.console.print("\nType 'n' for next page, 'p' for previous page, or 'b' to go back to posts.")

    def display_interactive_summary(self, post, summary):
        self.console.print(f"[bold magenta]{post.title}[/bold magenta]")
        self.console.print(f"[italic]{summary}[/italic]\n")
        self.console.print(f"[blue]URL: {post.url}[/blue]")
        self.console.print("\n[bold]Type 'details' to see the full comments or 'back' to return to the post list.[/bold]")

    def display_topics(self, topics):
        for idx, topic in enumerate(topics):
            self.console.print(f"Topic {idx+1}: {', '.join(topic)}")

    def display_threaded_comments(self, comments, start=0, count=10):
        displayed = 0
        for i, comment in enumerate(comments[start:], start=1):
            if displayed >= count:
                break
            self.display_comment(comment, i)
            displayed += 1
        self.console.print("\nEnter 'e <number>' to expand or 'c <number>' to collapse a comment thread.")
        return displayed

    def display_ai_analysis(self, subreddit, analysis):
        self.console.print(f"\n[bold]AI Analysis of r/{subreddit}:[/bold]\n")
        self.console.print(analysis)

    def display_comment(self, comment, number):
        indent = "  " * comment.depth
        collapse_symbol = "[-]" if not comment.collapsed else "[+]"
        self.console.print(f"{indent}{collapse_symbol} [cyan]{number}.[/cyan] [yellow]{comment.author}[/yellow] [green](Score: {comment.score})[/green]")
        
        if not comment.collapsed:
            wrapped_body = textwrap.fill(comment.body, width=80-len(indent), initial_indent=indent, subsequent_indent=indent)
            self.console.print(wrapped_body)
        
        if comment.children:
            reply_count = len(comment.children)
            if comment.collapsed or comment.is_root:
                self.console.print(f"{indent}  [blue]{reply_count} repl{'y' if reply_count == 1 else 'ies'}[/blue]")

    def display_help(self):
        help_text = """
        Available commands:

        /help               - Display this help message
        r <subreddit>       - Change to a specific subreddit (e.g., /sub AskReddit)
        sort <method>       - Change the post sorting method. Options: hot, new, top
        limit <number>      - Change the number of posts displayed
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
        analyze             - Get AI analysis of the current subreddit

        Notes:
        - If no subreddit is specified, the front page will be shown.
        - The default post sort method is 'hot'.
        - The default comment sort method is 'best'.
        - The default post limit is 10.
        - The search and summarize feature can now be used globally.
        - You need to set up your OpenAI API key in the .env file for the summarize feature to work.
        """

        self.console.print(help_text)
