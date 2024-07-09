# comment_utils.py

from .models import Comment
import requests
from bs4 import BeautifulSoup

class CommentManager:
    def __init__(self):
        self.current_comments = []
        self.comment_page = 0
        self.comment_sort_method = 'best'

    def flatten_comments(self, comments, depth=0, max_depth=6):
        for comment in comments:
            if depth < max_depth:
                yield comment
                yield from self.flatten_comments(comment.children, depth + 1, max_depth)

    def toggle_comment(self, action, comment_number):
        try:
            comment_index = int(comment_number) - 1
            if 0 <= comment_index < len(self.current_comments):
                comment = self.current_comments[comment_index]
                comment.collapsed = action == 'collapse'
                return True
            else:
                print("Invalid comment number.")
                return False
        except (ValueError, IndexError):
            print(f"Invalid {action} command. Use '{action[0]} <number>'.")
            return False

    def sort_comments(self, comments, method='best'):
        if method == 'best':
            return sorted(comments, key=lambda c: c.score, reverse=True)
        elif method == 'new':
            return comments  # Assuming comments are already in chronological order
        elif method == 'controversial':
            return sorted(comments, key=lambda c: abs(c.score), reverse=True)
        else:
            return comments

    def change_comment_sort(self, new_sort: str):
        if new_sort in ['best', 'new', 'controversial']:
            self.comment_sort_method = new_sort
            self.current_comments = self.sort_comments(self.current_comments, self.comment_sort_method)
            return True
        else:
            print("Invalid sort method. Use 'best', 'new', or 'controversial'.")
            return False

    def collapse_all_comments(self):
        for comment in self.current_comments:
            comment.collapsed = True

    def navigate_comments(self, direction):
        if direction == 'next':
            self.comment_page += 1
        elif direction == 'prev' and self.comment_page > 0:
            self.comment_page -= 1
        return self.comment_page

    def get_displayed_comments(self, start=0, count=10):
        return self.current_comments[start:start+count]

def get_comments(post, reddit_client):
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
        if depth <= 6:  # Limit depth to 6
            comments.append(Comment(author, score, body, depth))
    return comments
