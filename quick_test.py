import requests

BASE = "http://localhost:8000"
URL = "https://apnews.com/article/artificial-intelligence-regulation-eu-act-a3b36b5e96ce2fd29c5b749ec0aba305"

print("--- Testing /analyze ---")
r = requests.post(f"{BASE}/analyze", json={"url": URL}, timeout=60)
print("Status:", r.status_code)

if r.status_code == 200:
    d = r.json()
    print("Title    :", d["title"])
    score = d["sentiment_score"]
    print(f"Sentiment: {d['sentiment']} ({score})")
    print("Category :", d["category"])
    print("Keywords :", d["keywords"][:5])
    print("Summary  :", d["summary"][:300])
    text = d["text"]

    print()
    print("--- Testing /ask ---")
    r2 = requests.post(
        f"{BASE}/ask",
        json={
            "article_text": text,
            "question": "What is this article about in one sentence?",
        },
        timeout=60,
    )
    print("Status:", r2.status_code)
    if r2.status_code == 200:
        print("Answer :", r2.json()["answer"])
    else:
        print("Error:", r2.text[:300])
else:
    print("Error:", r.text[:300])
