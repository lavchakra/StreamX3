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
            // Unified URL from Cloudflare
            const API_URL = 'https://strand-congratulations-consequently-cost.trycloudflare.com';
            
            const response = await fetch(`${API_URL}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Bypass the tunnel reminder page for direct API access
                    'bypass-tunnel-reminder': 'true'
                },
                body: JSON.stringify({
                    url: tab.url,
                    translate: true // Request both English and Hindi
                })
            });

            if (!response.ok) throw new Error('Neural extraction failed.');

            const data = await response.json();
            
            // Populate results
            document.getElementById('summaryEn').textContent = data.summary;
            document.getElementById('summaryHi').textContent = data.hindi_summary || 'Hindi translation available in dashboard.';
            document.getElementById('sentiment').textContent = data.sentiment;
            document.getElementById('category').textContent = data.category;
            
            // Switch to results view
            loadingView.style.display = 'none';
            resultsView.style.display = 'block';
            
        } catch (error) {
            console.error(error);
            loadingView.style.display = 'none';
            setupView.style.display = 'block';
            alert('SYSTEM_ERR: Could not connect to Neural API. Please verify the tunnel is active.');
        }
    }
});
