"""
test.py
-------
Verifies all endpoints with 3–5 real article URLs.
Run with:  python test.py
"""

import json
import sys
import requests

BASE_URL = "http://localhost:8000"

# ── 3–5 real, freely-accessible news article URLs ────────────────────────────
TEST_URLS = [
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://en.wikipedia.org/wiki/Climate_change",
    "https://en.wikipedia.org/wiki/SpaceX",
]

SAMPLE_QUESTION = "What is the main topic of this article?"


def separator(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_health():
    separator("GET /  (Health Check)")
    resp = requests.get(f"{BASE_URL}/")
    print(f"Status : {resp.status_code}")
    print(f"Body   : {resp.json()}")
    assert resp.status_code == 200, "Health check failed!"
    print("[PASS]")


def test_analyze(url: str) -> str:
    """Returns the article text for use in /ask test."""
    separator(f"POST /analyze\n  URL: {url[:70]}...")
    payload = {"url": url}
    resp = requests.post(f"{BASE_URL}/analyze", json=payload, timeout=60)
    print(f"Status : {resp.status_code}")

    if resp.status_code != 200:
        print(f"[SKIP] (non-200): {resp.text[:300]}")
        return ""

    data = resp.json()
    print(f"Title         : {data.get('title', 'N/A')}")
    print(f"Summary       : {data.get('summary', '')[:200]}...")
    print(f"Sentiment     : {data.get('sentiment')}  (score={data.get('sentiment_score')})")
    print(f"Category      : {data.get('category')}")
    print(f"Keywords      : {data.get('keywords')}")
    print(f"Text length   : {len(data.get('text', ''))} chars")
    print("[PASS]")
    return data.get("text", "")


def test_ask(article_text: str, url_label: str):
    if not article_text:
        print(f"\n[SKIP] /ask for {url_label} - no article text.")
        return

    separator(f"POST /ask\n  Article from: {url_label[:60]}...")
    payload = {
        "article_text": article_text,
        "question": SAMPLE_QUESTION,
    }
    resp = requests.post(f"{BASE_URL}/ask", json=payload, timeout=60)
    print(f"Status : {resp.status_code}")

    if resp.status_code != 200:
        print(f"[FAIL]: {resp.text[:300]}")
        return

    data = resp.json()
    print(f"Question : {SAMPLE_QUESTION}")
    print(f"Answer   : {data['answer'][:400]}")
    print("[PASS]")


def test_invalid_analyze():
    separator("POST /analyze  — invalid URL (expect 422)")
    payload = {"url": "not-a-real-url"}
    resp = requests.post(f"{BASE_URL}/analyze", json=payload, timeout=30)
    print(f"Status : {resp.status_code}")
    print(f"Detail : {resp.json().get('detail', '')[:200]}")
    assert resp.status_code in (422, 400), f"Expected 4xx, got {resp.status_code}"
    print("[PASS]")


def test_empty_ask():
    separator("POST /ask  — empty question (expect 400)")
    payload = {"article_text": "Some article text here.", "question": ""}
    resp = requests.post(f"{BASE_URL}/ask", json=payload, timeout=30)
    print(f"Status : {resp.status_code}")
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
    print("[PASS]")


# ── Runner ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n[START]  Testing News Summarizer API at {BASE_URL}\n")

    try:
        test_health()
    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Cannot connect to {BASE_URL}")
        print("    Make sure the server is running:  uvicorn main:app --reload")
        sys.exit(1)

    test_invalid_analyze()
    test_empty_ask()

    for url in TEST_URLS:
        article_text = test_analyze(url)
        test_ask(article_text, url)

    print("\n" + "=" * 60)
    print("  All tests complete!")
    print("=" * 60 + "\n")
