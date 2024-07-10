# post_analysis.py

def extract_summary(post_title, post_content):
    return f"SUMMARY:\n- {post_title}: {post_content[:25]}..."

def extract_ideas(comments):
    ideas = []
    for comment in comments:
        ideas.extend(comment.split('.'))
    return [f"- {idea.strip()}." for idea in ideas if idea.strip()]

def extract_insights(ideas):
    insights = []
    for idea in ideas[:10]:
        insights.append(f"- {idea[:15].strip()}.")
    return insights

def extract_quotes(comments):
    quotes = []
    for comment in comments:
        quotes.extend(comment.split('.'))
    return [f"- {quote.strip()}." for quote in quotes if quote.strip()]

def extract_habits(comments):
    habits = []
    for comment in comments:
        if 'habit' in comment:
            habits.append(f"- {comment.strip()}.")
    return habits

def extract_facts(comments):
    facts = []
    for comment in comments:
        if 'fact' in comment:
            facts.append(f"- {comment.strip()}.")
    return facts

def extract_references(comments):
    references = []
    for comment in comments:
        if 'reference' in comment:
            references.append(f"- {comment.strip()}.")
    return references

def extract_one_sentence_takeaway(post_title, post_content):
    return f"ONE-SENTENCE TAKEAWAY:\n- {post_title}: {post_content[:15]}..."

def extract_recommendations(comments):
    recommendations = []
    for comment in comments:
        if 'recommendation' in comment:
            recommendations.append(f"- {comment.strip()}.")
    return recommendations