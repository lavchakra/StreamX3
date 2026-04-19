# News Summarizer Backend

FastAPI backend for the **News Summarizer Chatbot + Chrome Extension**.

## Project Structure

```
Backend/
├── main.py           # FastAPI app — /analyze & /ask endpoints
├── scraper.py        # newspaper3k article scraper
├── analyzer.py       # DS pipeline: summary, sentiment, keywords, category
├── chatbot.py        # Groq LLaMA-3 Q&A integration
├── test.py           # Endpoint tests with real article URLs
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

### 1. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Download NLTK data (required by TextBlob / newspaper3k)

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
python -m textblob.download_corpora
```

### 4. Set environment variables

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

Get a free Groq API key at [console.groq.com/keys](https://console.groq.com/keys).

### 5. Run the server

```bash
uvicorn main:app --reload --port 8000
```

Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Endpoints

| Method | Path       | Description                                       |
|--------|------------|---------------------------------------------------|
| GET    | `/`        | Health check                                      |
| POST   | `/analyze` | Scrape URL → summary, sentiment, keywords, category |
| POST   | `/ask`     | Article text + question → Groq LLM answer         |

### POST `/analyze`

```json
// Request
{ "url": "https://www.bbc.com/news/..." }

// Response
{
  "url": "...",
  "title": "Article Title",
  "text": "Full article text...",
  "summary": "Key points...",
  "sentiment": "positive",
  "sentiment_score": 0.12,
  "keywords": ["AI", "regulation", "EU"],
  "category": "technology"
}
```

### POST `/ask`

```json
// Request
{
  "article_text": "Full article text...",
  "question": "Who is the main subject of this article?"
}

// Response
{ "answer": "The article discusses..." }
```

## Running Tests

Make sure the server is running first, then:

```bash
python test.py
```

## Deployment (Render Free Tier)

1. Push the `Backend/` folder to GitHub.
2. Create a new **Web Service** on [render.com](https://render.com).
3. Set:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add `GROQ_API_KEY` in the **Environment** tab.
5. Update `API_BASE_URL` in your Chrome extension's `sidepanel.js` to the Render URL.
