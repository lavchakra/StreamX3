document.getElementById('summarizeBtn').addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (tab && tab.url) {
        const setupView = document.getElementById('setup-view');
        const loadingView = document.getElementById('loading');
        const resultsView = document.getElementById('results');
        
        // Switch to loading state
        setupView.style.display = 'none';
        loadingView.style.display = 'block';
        
        try {
            // Production URL on Render
            const API_URL = 'https://streamx3-neural-brief.onrender.com';


            
            const response = await fetch(`${API_URL}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    url: tab.url,
                    translate: true // Request both English and Hindi
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Server returned ${response.status}`);
            }

            const data = await response.json();
            
            // Populate results
            document.getElementById('summaryEn').textContent = data.summary;
            document.getElementById('summaryHi').textContent = data.hindi_summary || 'Hindi translation available in dashboard.';
            
            // Dynamic Sentiment Coloring
            const sentimentEl = document.getElementById('sentiment');
            const sent = data.sentiment.toLowerCase();
            sentimentEl.textContent = data.sentiment.split(' ')[0]; // Remove emoji for cleaner UI
            sentimentEl.className = 'meta-value'; // Reset
            if (sent.includes('positive')) sentimentEl.classList.add('badge-positive');
            else if (sent.includes('negative')) sentimentEl.classList.add('badge-negative');
            else sentimentEl.classList.add('badge-neutral');

            document.getElementById('category').textContent = data.category.toUpperCase();
            
            // Switch to results view with a slight delay for "analysis feel"
            setTimeout(() => {
                loadingView.style.display = 'none';
                resultsView.style.display = 'block';
            }, 500);

            
        } catch (error) {
            console.error('Extraction Error:', error);
            loadingView.style.display = 'none';
            setupView.style.display = 'block';
            alert(`SYSTEM_ERR: ${error.message}\n\nTroubleshooting:\n1. Ensure the backend server is active.\n2. If using Render, wait 30s for it to wake up.\n3. Check your internet connection.`);
        }

    }
});
