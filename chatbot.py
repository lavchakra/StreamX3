"""
chatbot.py
----------
Sends article text + a user question to Groq's LLaMA-3 model and returns
a plain-text answer.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(override=True)

_client: Groq | None = None


def _get_client() -> Groq:
    """Lazily initialise the Groq client (reads GROQ_API_KEY from env or .env)."""
    global _client
    if _client:
        return _client
        
    # Priority: 1. Environment Variable, 2. .env file
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        from dotenv import dotenv_values
        config = dotenv_values(".env")
        api_key = config.get("GROQ_API_KEY")

    if not api_key or api_key == "your_groq_api_key_here":
        raise EnvironmentError(
            "GROQ_API_KEY is not set. "
            "Please set it as an environment variable or in your .env file."
        )
    
    _client = Groq(api_key=api_key)
    return _client



_SYSTEM_PROMPT = (
    "You are a helpful news analyst assistant. "
    "You will be given the full text of a news article followed by a user question. "
    "Answer the question accurately and concisely based only on the article content. "
    "If the answer cannot be found in the article, say so clearly."
)


def ask_question(article_text: str, question: str, model: str = "llama-3.1-8b-instant") -> str:
    """
    Sends article_text and question to Groq and returns the model's answer.

    Args:
        article_text : Full plain-text content of the news article.
        question     : User's question about the article.
        model        : Groq model ID (default: llama3-8b-8192 — fastest free-tier).

    Returns:
        Plain-text answer string.

    Raises:
        EnvironmentError : GROQ_API_KEY not set.
        Exception        : Any Groq API / network error.
    """
    client = _get_client()

    # Truncate article to ~3000 words to stay within context limits on free tier
    words = article_text.split()
    if len(words) > 3000:
        article_text = " ".join(words[:3000]) + "\n[Article truncated for brevity]"

    user_message = (
        f"ARTICLE:\n{article_text}\n\n"
        f"QUESTION: {question}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        temperature=0.3,   # low temperature → factual, grounded answers
        max_tokens=512,
    )

    return response.choices[0].message.content.strip()


def summarize_in_hindi(article_text: str, model: str = "llama-3.1-8b-instant") -> str:
    """Uses Groq to generate a 4-line summary of the article in Hindi."""
    client = _get_client()

    words = article_text.split()
    if len(words) > 3000:
        article_text = " ".join(words[:3000])

    prompt = (
        "नीचे दिए गए समाचार लेख का ठीक 4 पंक्तियों में, स्वाभाविक और स्पष्ट हिंदी में सारांश लिखो।\n"
        "केवल हिंदी में उत्तर दो।\n\n"
        f"Article:\n{article_text}\n\nSummary:\n"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=400,
    )
    return response.choices[0].message.content.strip()
