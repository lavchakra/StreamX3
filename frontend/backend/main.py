import os
import json
import re
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ── Groq Setup ──────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("❌ GROQ_API_KEY not set. Add it to backend/.env")

client = Groq(api_key=GROQ_API_KEY)
MODEL_NAME = "llama-3.3-70b-versatile" # Powerful, fast Groq model

# ── App Setup ─────────────────────────────────────────────────
app = FastAPI(title="NewsBriefAI Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3002", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request / Response Models ─────────────────────────────────
class AnalyzeRequest(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None
    translate: Optional[bool] = False

class AnalyzeResponse(BaseModel):
    summary: str
    sentiment: str
    keywords: list[str]
    category: str
    hindi_summary: Optional[str] = None

# ── Helpers ───────────────────────────────────────────────────
def extract_text_from_url(url: str) -> str:
    """Fetch article text from a URL using newspaper3k."""
    try:
        from newspaper import Article
        article = Article(url)
        article.download()
        article.parse()
        text = article.text.strip()
        if not text:
            raise ValueError("Empty article content")
        return text
    except Exception:
        # Fallback: plain HTTP fetch
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = httpx.get(url, headers=headers, follow_redirects=True, timeout=15)
            resp.raise_for_status()
            # Strip HTML tags roughly
            clean = re.sub(r"<[^>]+>", " ", resp.text)
            clean = re.sub(r"\s+", " ", clean).strip()
            return clean[:8000]  # limit tokens
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Could not fetch article: {e}")


def build_prompt(text: str, translate: bool) -> str:
    hindi_instruction = """
6. "hindi_summary": A complete Hindi translation of the summary (2-3 sentences in Devanagari script).""" if translate else """
6. "hindi_summary": null"""

    return f"""You are a professional news analyst. Analyze the following news article and return a JSON object with EXACTLY these keys:

1. "summary": A clear, concise summary in 3-4 sentences (English).
2. "sentiment": One of exactly: "Positive", "Negative", or "Neutral".
3. "keywords": A list of 5-8 important keywords or phrases from the article.
4. "category": One category from: Politics, Technology, Business, Sports, Entertainment, Science, Health, World, Environment, Crime, Education, General.{hindi_instruction}

IMPORTANT: Return ONLY valid JSON. No markdown, no code blocks, no extra text.

Article:
\"\"\"
{text[:6000]}
\"\"\"
"""

def parse_llm_response(raw: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks."""
    # Remove markdown code fences if present
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
    cleaned = cleaned.strip("`").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to find JSON object in the response
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Could not parse JSON from response: {raw[:200]}")

# ── Main Endpoint ─────────────────────────────────────────────
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    # Validate input
    if not req.text and not req.url:
        raise HTTPException(status_code=400, detail="Provide either 'text' or 'url'.")

    # Get article text
    if req.url:
        article_text = extract_text_from_url(req.url)
    else:
        article_text = req.text.strip()
        if len(article_text) < 50:
            raise HTTPException(status_code=400, detail="Text too short. Please provide more content.")

    # Build prompt & call Groq
    prompt = build_prompt(article_text, req.translate)
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=MODEL_NAME,
            temperature=0.3,
            max_tokens=1024,
            response_format={"type": "json_object"},
        )
        response_text = chat_completion.choices[0].message.content
        data = parse_llm_response(response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    # Validate and return
    return AnalyzeResponse(
        summary=data.get("summary", "Summary not available."),
        sentiment=data.get("sentiment", "Neutral"),
        keywords=data.get("keywords", []),
        category=data.get("category", "General"),
        hindi_summary=data.get("hindi_summary") if req.translate else None,
    )

# ── Health Check ──────────────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "ok", "message": "NewsBriefAI backend is running with Groq 🚀"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
