# ai_analysis.py

from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF

class AIClient:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def summarize_comments(self, comments, post_title, subreddit):
        prompt = (
            f"Summarize the following Reddit comments on the post titled '{post_title}' "
            f"in the subreddit '{subreddit}':\n\n"
            f"{' '.join(comments[:5])}\n\nSummary:"
        )
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    def extract_topics(self, comments):
        vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words='english')
        tfidf = vectorizer.fit_transform(comments)
        nmf = NMF(n_components=5, random_state=1).fit(tfidf)
        feature_names = vectorizer.get_feature_names_out()
        topics = []
        for topic_idx, topic in enumerate(nmf.components_):
            topic_keywords = [feature_names[i] for i in topic.argsort()[:-6:-1]]
            topics.append(topic_keywords)
        return topics

    def ai_subreddit_analysis(self, subreddit_name, aspects, posts):
        # Prepare the prompt for the AI
        post_titles = "\n".join([f"- {post.title}" for post in posts])
        prompt = f"""Analyze the following recent posts from the r/{subreddit_name} subreddit:

{post_titles}

The user is particularly interested in: {aspects}

Based on these posts and the user's interests, provide a brief analysis of:
1. The main topics or themes currently being discussed, focusing on {aspects}
2. Any trending or particularly interesting posts related to {aspects}
3. The overall mood or sentiment of the subreddit, especially regarding {aspects}
4. What a new visitor to this subreddit should pay attention to, considering their interest in {aspects}

Limit your response to 200 words."""

        # Get AI analysis
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes Reddit content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            n=1,
            stop=None,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
