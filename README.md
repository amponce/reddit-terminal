# Reddit Terminal

A Snoo Terminal application to browse Reddit posts and comments using the Reddit API or web scraping as a fallback.

## Features

- View posts from the front page or specific subreddits
- Display comments in a threaded manner
- Pagination for comments
- Fallback to web scraping if API credentials are not available

## Prerequisites

- Python 3.6 or later
- `praw`, `requests`, `beautifulsoup4`, `rich`, `python-dotenv`

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/yourusername/reddit_terminal_reader.git
   cd reddit_terminal_reader
   ```

2. Create and activate a virtual environment:

   ```sh
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:

   ```sh
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your Reddit API credentials:

   ```env
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   REDDIT_USER_AGENT=your_user_agent
   OPENAI_API_KEY=your_key
   ```

## Getting Reddit API Credentials

1. Go to [Reddit's App Preferences](https://www.reddit.com/prefs/apps).
2. Click on "Create App" or "Create Another App" at the bottom of the page.
3. Fill in the required fields:
   - **name**: Choose a name for your application.
   - **App type**: Select "script".
   - **description**: (optional) Provide a description for your app.
   - **about url**: (optional) Add a URL for more information about your app.
   - **redirect uri**: Set this to `http://localhost:8000` or any URL you prefer (this won't be used in this script).
   - **permissions**: (optional) Set the required permissions.
4. Click "Create app".
5. Your app will be created, and you will see `client_id` and `client_secret`. Copy these values and add them to your `.env` file along with a user agent.

## Usage

Run the main script to start the Reddit Terminal Reader:

```sh
python main.py
```

## Commands

- `/help` - Display the help message
- `/sub <subreddit>` - Change to a specific subreddit (e.g., `/sub AskReddit`)
- `/sort <method>` - Change the post sorting method. Options: `hot`, `new`, `top`
- `/limit <number>` - Change the number of posts displayed
- `<number>` - View a specific post and its comments
- `n` - View next page of comments
- `p` - View previous page of comments
- `b` - Go back to post list
- `o` - Open the current post's URL in your default web browser
- `e <number>` - Expand a specific comment thread
- `c <number>` - Collapse a specific comment thread
- `sort <method>` - Sort comments. Options: `best`, `new`, `controversial`
- `collapse_all` - Collapse all comments to show only root-level comments
- `more` - Show more comments (not implemented)
- `q` - Quit the program

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
