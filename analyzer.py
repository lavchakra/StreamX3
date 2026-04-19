"""
analyzer.py
-----------
DS analysis pipeline integrated with logic from D:\\News Summarizer\\summarizer.py.
Powers the news summarization, sentiment analysis, and keyword extraction.
"""

import json
from textblob import TextBlob
from chatbot import _get_client

def _generate_summary_via_llm(text: str, language: str = "english") -> str:
    """Uses Groq to generate a precise 4-line summary in English or Hindi."""
    client = _get_client()
    
    # Simple truncation to prevent context window overflow
    words = text.split()
    if len(words) > 3000:
        text = " ".join(words[:3000])

    if language.lower() == "hindi":
        prompt = f"""
        नीचे दिए गए समाचार लेख का ठीक 4 पंक्तियों में, स्वाभाविक और स्पष्ट हिंदी में सारांश लिखो।
        केवल हिंदी में उत्तर दो।

        Article:
        {text}

        Summary:
        """
    else:
        prompt = f"""
        Summarize the following news article in exactly 4 lines.
        Be concise, factual, and clear.

        Article:
        {text}

        Summary:
        """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=512
    )
    return response.choices[0].message.content.strip()


def _extract_metadata_via_llm(text: str) -> dict:
    """Uses Groq JSON mode to extract keywords and category."""
    client = _get_client()
    words = text.split()
    if len(words) > 2500:
        text = " ".join(words[:2500])

    prompt = f"""
    Extract exactly and return as JSON:
    1. Top 5 keywords as a list of strings
    2. One category from: Politics, Sports, Tech, Business, Health, World

    Reply in JSON only like this:
    {{"keywords": ["word1", "word2", "word3", "word4", "word5"], "category": "Tech"}}

    Article:
    {text}
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.1,
        max_tokens=256
    )
    return json.loads(response.choices[0].message.content)


def analyze_article(text: str, language_mode: str = "english") -> dict:
    """
    Full DS analysis pipeline based on the user's custom DS module.
    language_mode: "english", "hindi", or "both"
    """
    # --- Sentiment (Logic from summarizer.py) ---
    blob = TextBlob(text)
    polarity: float = round(blob.sentiment.polarity, 4)
    if polarity > 0.1:
        sentiment = "Positive 🟢"
    elif polarity < -0.1:
        sentiment = "Negative 🔴"
    else:
        sentiment = "Neutral 🟡"

    # --- Summary Generation ---
    results = {
        "summary": None,
        "hindi_summary": None,
        "sentiment": sentiment,
        "sentiment_score": polarity,
        "keywords": [],
        "category": "General"
    }

    if language_mode in ["english", "both"]:
        results["summary"] = _generate_summary_via_llm(text, language="english")
    
    if language_mode in ["hindi", "both"]:
        results["hindi_summary"] = _generate_summary_via_llm(text, language="hindi")

    # --- Keywords & Category ---
    try:
        extras = _extract_metadata_via_llm(text)
        results["keywords"] = extras.get("keywords", [])
        results["category"] = extras.get("category", "General")
    except Exception as e:
        print(f"Metadata extraction error: {e}")
        pass

    return results
