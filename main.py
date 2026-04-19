from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional
import httpx

from scraper import scrape_article
from analyzer import analyze_article
from chatbot import ask_question

app = FastAPI(
    title="News Summarizer API",
    description="Backend API for News Summarizer Chatbot + Chrome Extension",
    version="1.0.0"
)

# ---------------------------------------------------------------------------
# CORS — allow the Chrome extension and any local frontend to call the API
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None
    translate: Optional[bool] = False

class AnalyzeResponse(BaseModel):
    url: Optional[str] = None
    title: str
    text: str
    summary: Optional[str] = None
    hindi_summary: Optional[str] = None
    sentiment: str
    sentiment_score: float
    keywords: list[str]
    category: str

class AskRequest(BaseModel):
    article_text: str
    question: str

class AskResponse(BaseModel):
    answer: str


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "News Summarizer API is running"}


# ---------------------------------------------------------------------------
# /analyze  — scrape + DS pipeline
# ---------------------------------------------------------------------------

@app.post("/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze(req: AnalyzeRequest):
    """
    Accepts a news article URL or text.
    Uses the integrated DS pipeline for summary, sentiment, and keywords.
    """
    try:
        if req.url:
            article = scrape_article(req.url)
            text_to_process = article["text"]
            title = article["title"]
            used_url = req.url
        elif req.text:
            text_to_process = req.text
            title = "Pasted Text Analysis"
            used_url = None
        else:
            raise HTTPException(status_code=400, detail="Must provide either url or text.")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Scraping/parsing failed: {e}")

    # Determine language mode based on 'translate' flag
    mode = "both" if req.translate else "english"

    try:
        analysis = analyze_article(text_to_process, language_mode=mode)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")

    return AnalyzeResponse(
        url=used_url,
        title=title,
        text=text_to_process,
        **analysis,
    )


# ---------------------------------------------------------------------------
# /ask  — Groq LLM Q&A
# ---------------------------------------------------------------------------

@app.post("/ask", response_model=AskResponse, tags=["Chatbot"])
async def ask(req: AskRequest):
    """
    Accepts article text + a user question.
    Sends both to Groq (LLaMA-3) and returns a plain-text answer.
    """
    if not req.article_text.strip():
        raise HTTPException(status_code=400, detail="article_text cannot be empty.")
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question cannot be empty.")

    try:
        answer = ask_question(article_text=req.article_text, question=req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq request failed: {e}")

    return AskResponse(answer=answer)


# ---------------------------------------------------------------------------
# Serve Frontend Static Files
# ---------------------------------------------------------------------------

# Port 8000 will now also serve our React App
import os

frontend_path = os.path.join(os.getcwd(), "frontend", "build")

if os.path.exists(frontend_path):
    # Serve static assets (JS, CSS)
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")

    # Serve the main React SPA for everything else
    @app.get("/{catchall:path}")
    async def serve_react_app(catchall: str):
        # If the file exists in build directory, serve it (e.g., manifest.json, favicon.ico)
        file_path = os.path.join(frontend_path, catchall)
        if catchall != "" and os.path.exists(file_path):
            return FileResponse(file_path)
        # Otherwise serve index.html
        return FileResponse(os.path.join(frontend_path, "index.html"))
else:
    @app.get("/")
    def root():
        return {"status": "ok", "message": "Backend only: frontend/build not found"}
