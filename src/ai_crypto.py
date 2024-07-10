# ai_crypto.py

from openai import OpenAI
from .post_analysis import (
    extract_summary, extract_ideas, extract_insights, extract_quotes, extract_habits,
    extract_facts, extract_references, extract_one_sentence_takeaway, extract_recommendations
)
from textblob import TextBlob

class AIClientCrypto:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.conversation_history = []

    def analyze_post(self, post_title, post_content, comments):
        summary = extract_summary(post_title, post_content)
        ideas = extract_ideas(comments)
        insights = extract_insights(ideas)
        quotes = extract_quotes(comments)
        habits = extract_habits(comments)
        facts = extract_facts(comments)
        references = extract_references(comments)
        takeaway = extract_one_sentence_takeaway(post_title, post_content)
        recommendations = extract_recommendations(comments)
        
        sentiments = [TextBlob(comment).sentiment.polarity for comment in comments]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

        trending_coins = self.identify_trending_coins(comments)

        analysis = f"{summary}\n\n"
        analysis += "IDEAS:\n" + "".join(f"- {idea}\n" for idea in ideas[:25]) + "\n"
        analysis += "INSIGHTS:\n" + "".join(f"- {insight}\n" for insight in insights[:10]) + "\n"
        analysis += "QUOTES:\n" + "".join(f"- {quote}\n" for quote in quotes[:20]) + "\n"
        analysis += "HABITS:\n" + "".join(f"- {habit}\n" for habit in habits[:20]) + "\n"
        analysis += "FACTS:\n" + "".join(f"- {fact}\n" for fact in facts[:20]) + "\n"
        analysis += "REFERENCES:\n" + "".join(f"- {reference}\n" for reference in references[:20]) + "\n"
        analysis += f"{takeaway}\n\n"
        analysis += "RECOMMENDATIONS:\n" + "".join(f"- {recommendation}\n" for recommendation in recommendations[:20]) + "\n"
        analysis += f"AVERAGE SENTIMENT: {avg_sentiment:.2f}\n"
        analysis += f"TRENDING COINS: {', '.join(trending_coins)}\n"

        self.conversation_history.append({"role": "assistant", "content": analysis})
        return analysis

    def system_command(self, input_text):
        prompt = f"""
        You extract surprising, insightful, and interesting information from text content, specifically focusing on cryptocurrency and finance. Your goal is to provide insights related to new altcoins, trending coins based on sentiment, and strategies for making money with cryptocurrency.

        STEPS:
        - Extract a summary of the content in 25 words, including who is presenting and the content being discussed into a section called SUMMARY.
        - Extract 20 to 50 of the most surprising, insightful, and/or interesting ideas from the input in a section called IDEAS:. If there are less than 50 then collect all of them. Make sure you extract at least 20.
        - Extract 10 to 20 of the best insights from the input and from a combination of the raw input and the IDEAS above into a section called INSIGHTS. These INSIGHTS should be fewer, more refined, more insightful, and more abstracted versions of the best ideas in the content.
        - Extract 15 to 30 of the most surprising, insightful, and/or interesting quotes from the input into a section called QUOTES:. Use the exact quote text from the input.
        - Extract 15 to 30 of the most practical and useful personal habits of the speakers, or mentioned by the speakers, in the content into a section called HABITS.
        - Extract 15 to 30 of the most surprising, insightful, and/or interesting valid facts about the greater world that were mentioned in the content into a section called FACTS:.
        - Extract all mentions of writing, art, tools, projects and other sources of inspiration mentioned by the speakers into a section called REFERENCES. This should include any and all references to something that the speaker mentioned.
        - Extract the most potent takeaway and recommendation into a section called ONE-SENTENCE TAKEAWAY. This should be a 15-word sentence that captures the most important essence of the content.
        - Extract the 15 to 30 of the most surprising, insightful, and/or interesting recommendations that can be collected from the content into a section called RECOMMENDATIONS.

        OUTPUT INSTRUCTIONS:
        - Only output Markdown.
        - Write the IDEAS bullets as exactly 15 words.
        - Write the RECOMMENDATIONS bullets as exactly 15 words.
        - Write the HABITS bullets as exactly 15 words.
        - Write the FACTS bullets as exactly 15 words.
        - Write the INSIGHTS bullets as exactly 15 words.
        - Extract at least 25 IDEAS from the content.
        - Extract at least 10 INSIGHTS from the content.
        - Extract at least 20 items for the other output sections.
        - Do not give warnings or notes; only output the requested sections.
        - You use bulleted lists for output, not numbered lists.
        - Do not repeat ideas, quotes, facts, or resources.
        - Do not start items with the same opening words.
        - Ensure you follow ALL these instructions when creating your output.

        INPUT:
        {input_text}
        """

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts detailed insights from text."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            n=1,
            stop=None,
            temperature=0.7
        )

        analysis = response.choices[0].message.content.strip()
        self.conversation_history.append({"role": "user", "content": input_text})
        self.conversation_history.append({"role": "assistant", "content": analysis})
        return analysis

    def identify_trending_coins(self, comments):
        # This is a placeholder implementation
        coins = ["BTC", "ETH", "DOGE", "ADA", "BNB", "XRP", "SOL", "DOT", "SHIB", "LTC"]
        mentioned_coins = []
        for comment in comments:
            for coin in coins:
                if coin.lower() in comment.lower():
                    mentioned_coins.append(coin)
        trending_coins = list(set(mentioned_coins))
        return trending_coins

# List of popular cryptocurrency subreddits
CRYPTO_SUBREDDITS = [
    'r/Bitcoin',
    'r/ethereum',
    'r/CryptoCurrency',
    'r/BitcoinBeginners',
    'r/altcoin',
    'r/cryptomarkets',
    'r/defi',
    'r/SatoshiStreetBets',
    'r/CryptoMoonShots',
    'r/cryptotechnology',
    'r/Crypto_General',
    'r/CryptoMarkets',
    'r/CryptoTechnology',
    'r/BitcoinMarkets',
    'r/Crypto_Currency_News',
    'r/BitcoinMining',
    'r/CryptoCurrencies',
    'r/cryptotrading',
    'r/cryptodevs',
    'r/Cardano',
    'r/Ripple',
    'r/BitcoinCash',
    'r/Dogecoin',
    'r/Litecoin',
    'r/Monero',
    'r/Stellar',
    'r/Tronix',
    'r/IOTA'
]