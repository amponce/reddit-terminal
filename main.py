# main.py

from src.reddit_client import RedditClient
from src.models import Post, Comment
from src.display import ConsoleUI
from src.comment_utils import CommentManager, get_comments
from src.search import search_and_summarize
from src.ai_analysis import AIClient
from src.config import config

import webbrowser

def open_in_browser(url):
    webbrowser.open(url, new=2)

class RedditTerminal:
    def __init__(self):
        self.reddit_client = RedditClient()
        self.console_ui = ConsoleUI()
        self.comment_manager = CommentManager()
        self.ai_client = AIClient(config.OPENAI_API_KEY) if config.USE_AI_FEATURES else None
        
        self.current_subreddit = config.DEFAULT_SUBREDDIT
        self.current_posts = []
        self.post_limit = config.DEFAULT_POST_LIMIT
        self.post_sort_method = config.DEFAULT_POST_SORT
        self.selected_post_index = None

    def refresh_posts(self):
        self.current_posts = self.reddit_client.get_posts(self.current_subreddit, self.post_sort_method, self.post_limit)
        self.console_ui.display_posts(self.current_posts)

    def change_subreddit(self, new_subreddit: str):
        self.current_subreddit = new_subreddit if new_subreddit else None
        self.refresh_posts()

    def change_post_sort(self, new_sort: str):
        if new_sort in ['hot', 'new', 'top']:
            self.post_sort_method = new_sort
            self.refresh_posts()
        else:
            print("Invalid sort method. Use 'hot', 'new', or 'top'.")

    def change_post_limit(self, new_limit: str):
        try:
            self.post_limit = int(new_limit)
            self.refresh_posts()
        except ValueError:
            print("Invalid limit. Please enter a number.")

    def view_post(self, post_index):
        if 0 <= post_index < len(self.current_posts):
            post = self.current_posts[post_index]
            post = self.reddit_client.get_post_content(post)  # Fetch the post content
            self.comment_manager.current_comments = get_comments(post, self.reddit_client)
            self.comment_manager.comment_page = 0
            self.selected_post_index = post_index
            self.console_ui.display_post_and_comments(post, self.comment_manager.current_comments, self.comment_manager.comment_page)
        else:
            print(f"Invalid post number. Please enter a number between 1 and {len(self.current_posts)}.")

    def display_post_and_comments(self, post):
        self.console_ui.display_post_and_comments(post, self.comment_manager.current_comments, self.comment_manager.comment_page)

    def navigate_comments(self, direction):
        if direction == 'next':
            self.comment_manager.comment_page += 1
        elif direction == 'prev' and self.comment_manager.comment_page > 0:
            self.comment_manager.comment_page -= 1
        self.display_post_and_comments(self.current_posts[self.selected_post_index])

    def analyze_specific_post(self, post_index):
        if 0 <= post_index < len(self.current_posts):
            post = self.current_posts[post_index]
            post = self.reddit_client.get_post_content(post)  # Fetch the post content
            comments = self.comment_manager.current_comments
            analysis = self.perform_analysis(post, comments)
            print(f"\nDetailed Analysis of '{post.title}':\n{analysis}")
        else:
            print(f"Invalid post number. Please enter a number between 1 and {len(self.current_posts)}.")

    def analyze_current_post(self):
        if self.selected_post_index is not None:
            post = self.current_posts[self.selected_post_index]
            post = self.reddit_client.get_post_content(post)  # Fetch the post content
            comments = self.comment_manager.current_comments
            analysis = self.perform_analysis(post, comments)
            print(f"\nDetailed Analysis of '{post.title}':\n{analysis}")
        else:
            print("No post selected. Please select a post first.")

    def perform_analysis(self, post, comments):
        if self.ai_client:
            comment_texts = [comment.body for comment in comments if hasattr(comment, 'body')]
            input_text = f"Post Title: {post.title}\n\nPost Content: {post.selftext}\n\nComments:\n" + "\n".join(comment_texts)
            analysis = self.ai_client.system_command(input_text)
            return analysis
        else:
            return "AI analysis is not enabled. Please check your configuration."

    def run(self):
        self.refresh_posts()

        while True:
            self.console_ui.print_status(self.current_subreddit, self.post_sort_method, self.post_limit)
            command = input("Enter a command: ").lower().split()

            if not command:
                continue
            if command[0] == 'q':
                break
            elif command[0] == '/help':
                self.console_ui.display_help()
            elif command[0] == 'r':
                self.change_subreddit(command[1] if len(command) > 1 else None)
            elif command[0] == 'sort':
                self.change_post_sort(command[1] if len(command) > 1 else 'hot')
            elif command[0] == 'limit':
                self.change_post_limit(command[1] if len(command) > 1 else '20')
            elif command[0].isdigit():
                self.view_post(int(command[0]) - 1)
            elif command[0] == 'n':
                self.navigate_comments('next')
            elif command[0] == 'p':
                self.navigate_comments('prev')
            elif command[0] == 'b':
                self.refresh_posts()
            elif command[0] == 'o':
                self.open_current_post_in_browser()
            elif command[0] in ['e', 'c']:
                self.comment_manager.toggle_comment('expand' if command[0] == 'e' else 'collapse', command[1] if len(command) > 1 else '')
                self.display_post_and_comments(self.current_posts[self.selected_post_index])
            elif command[0] == 'sort' and len(command) > 1:
                if self.comment_manager.change_comment_sort(command[1]):
                    self.display_post_and_comments(self.current_posts[self.selected_post_index])
            elif command[0] == 'collapse_all':
                self.comment_manager.collapse_all_comments()
                self.display_post_and_comments(self.current_posts[self.selected_post_index])
            elif command[0] == 's':
                query = ' '.join(command[1:]) if len(command) > 1 else input("Enter your search query: ")
                search_and_summarize(self.reddit_client, self.ai_client, query, self.current_subreddit)
            elif command[0] == 'analyze':
                if self.selected_post_index is not None:
                    self.analyze_current_post()
                else:
                    print("Please select a post first by entering its number.")
            elif command[0] == 'analyze_post':
                if self.ai_client:
                    if len(command) > 1 and command[1].isdigit():
                        self.analyze_specific_post(int(command[1]) - 1)
                    else:
                        print("Please provide a valid post number to analyze.")
                else:
                    print("AI features are not enabled.")
            else:
                print("Invalid command. Type '/help' for a list of available commands.")

    def open_current_post_in_browser(self):
        if self.selected_post_index is not None and hasattr(self.current_posts[self.selected_post_index], 'url'):
            open_in_browser(self.current_posts[self.selected_post_index].url)
            print(f"Opening {self.current_posts[self.selected_post_index].url} in your default browser.")
        else:
            print("No post selected or URL available.")

if __name__ == "__main__":
    reddit_terminal = RedditTerminal()
    reddit_terminal.run()