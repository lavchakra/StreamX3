import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import API_BASE_URL from './config';
import './App.css';

function App() {
  const [inputMode, setInputMode] = useState('text'); // 'text' or 'url'
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [language, setLanguage] = useState('english'); // 'english' | 'hindi' | 'both'
  const [error, setError] = useState('');

  // Sidebar & Chat State
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef(null);

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Read URL from Chrome Extension
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const passedUrl = params.get('url');
    if (passedUrl) {
      setInputMode('url');
      setInputValue(passedUrl);
    }
  }, []);

  const handleSummarize = async () => {
    if (!inputValue.trim()) {
      setError('Please enter some text or a URL first.');
      return;
    }
    setError('');
    setLoading(true);
    setResult(null);
    setMessages([]); // Clear chat history on new analysis (User Request)
    setIsSidebarOpen(false); // Close sidebar on new analysis

    try {
      const payload = {
        [inputMode === 'url' ? 'url' : 'text']: inputValue,
        translate: language === 'hindi' || language === 'both',
      };

      const response = await axios.post(`${API_BASE_URL}/analyze`, payload);
      setResult(response.data);
    } catch (err) {
      setError('Could not connect to backend. Make sure the API is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleAskQuestion = async (e) => {
    if (e) e.preventDefault();
    if (!chatInput.trim() || chatLoading || !result) return;

    const userMsg = chatInput.trim();
    setChatInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setChatLoading(true);

    try {
      const payload = {
        article_text: result.text,
        question: userMsg
      };
      const response = await axios.post(`${API_BASE_URL}/ask`, payload);
      setMessages(prev => [...prev, { role: 'ai', content: response.data.answer }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'ai', content: 'Connection error. Please check the backend.' }]);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className={`app ${isSidebarOpen ? 'sidebar-open' : ''}`}>
      {/* Header */}
      <header className="header">
        <div className="logo">
          <span className="logo-icon">🚀</span>
          <span className="logo-text">Cyber<span className="logo-accent">Brief</span></span>
        </div>
        <p className="tagline">Neural News Summarization v2.0</p>
      </header>

      <main className="main">
        {/* Mode Toggle */}
        <div className="mode-toggle">
          <button
            className={`mode-btn ${inputMode === 'text' ? 'active' : ''}`}
            onClick={() => { setInputMode('text'); setInputValue(''); }}
          >
            📝 Text
          </button>
          <button
            className={`mode-btn ${inputMode === 'url' ? 'active' : ''}`}
            onClick={() => { setInputMode('url'); setInputValue(''); }}
          >
            🔗 URL
          </button>
        </div>

        {/* Input Area */}
        <div className="input-card">
          {inputMode === 'text' ? (
            <textarea
              className="text-input"
              placeholder="Inject news article text..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              rows={8}
            />
          ) : (
            <input
              type="url"
              className="url-input"
              placeholder="https://news-source.com/article"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
            />
          )}

          <div className="lang-selector">
            <span className="lang-label">SYSTEM_LANG:</span>
            <div className="lang-options">
              {['english', 'hindi', 'both'].map((val) => (
                <button
                  key={val}
                  className={`lang-btn ${language === val ? 'active' : ''}`}
                  onClick={() => setLanguage(val)}
                >
                  {val.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          {error && <p className="error-msg">SYSTEM_ERR: {error}</p>}

          <button
            className={`summarize-btn ${loading ? 'loading' : ''}`}
            onClick={handleSummarize}
            disabled={loading}
          >
            {loading ? 'ANALYZING...' : 'SUMMARIZE ARTICLE'}
          </button>
        </div>

        {/* Result Grid */}
        {result && (
          <div className="results">
            {(language === 'english' || language === 'both') && (
              <div className="result-card summary-card">
                <div className="card-header">
                  <h3>// ENGLISH_SUMMARY</h3>
                </div>
                <p>{result.summary}</p>
              </div>
            )}

            {(language === 'hindi' || language === 'both') && result.hindi_summary && (
              <div className="result-card hindi-card">
                <div className="card-header">
                  <h3>// हिंदी_सारांश</h3>
                </div>
                <p>{result.hindi_summary}</p>
              </div>
            )}

            <div className="result-card">
              <div className="card-header"><h3>// SENTIMENT</h3></div>
              <div className="sentiment-badge">{result.sentiment}</div>
            </div>

            <div className="result-card">
              <div className="card-header"><h3>// KEYWORDS</h3></div>
              <div className="keywords-list">
                {result.keywords?.map((kw, i) => (
                  <span key={i} className="keyword-tag">{kw}</span>
                ))}
              </div>
            </div>

            <div className="result-card">
              <div className="card-header"><h3>// CATEGORY</h3></div>
              <div className="category-badge">{result.category}</div>
            </div>
          </div>
        )}
      </main>

      {/* Floating Toggle */}
      {result && (
        <div className="chat-toggle" onClick={() => setIsSidebarOpen(true)}>
          💬
        </div>
      )}

      {/* Sidebar Overlay */}
      <div 
        className={`sidebar-overlay ${isSidebarOpen ? 'open' : ''}`} 
        onClick={() => setIsSidebarOpen(false)}
      />

      {/* Sliding Sidebar */}
      <aside className={`sidebar ${isSidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h2><span>🛰️</span> Neural Analysis Chat</h2>
          <button className="close-btn" onClick={() => setIsSidebarOpen(false)}>×</button>
        </div>

        <div className="chat-messages">
          {messages.length === 0 && (
            <p className="text-muted" style={{textAlign: 'center', marginTop: '20px'}}>
              Ask anything about the article...
            </p>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`message ${m.role}`}>
              {m.content}
            </div>
          ))}
          {chatLoading && <div className="message ai">Thinking...</div>}
          <div ref={chatEndRef} />
        </div>

        <form className="chat-input-area" onSubmit={handleAskQuestion}>
          <input
            type="text"
            className="chat-input"
            placeholder="Query article data..."
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            disabled={chatLoading}
          />
          <button type="submit" className="send-btn" disabled={chatLoading}>
            SEND
          </button>
        </form>
      </aside>

      <footer className="footer">
        <p>CyberBrief AI · v2.0.0-STABLE · CSE DISTRICT 2</p>
      </footer>
    </div>
  );
}

export default App;
