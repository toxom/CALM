let currentMode = 'binary';
const API_BASE = 'http://localhost:8000';

async function setMode(mode) {
    currentMode = mode;
    
    // Update UI
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Update server config
    try {
        const response = await fetch(`${API_BASE}/config/mode`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode })
        });
        const data = await response.json();
        
        document.getElementById('config-status').innerHTML = `
            <div class="status success">
                ✓ Mode switched to: <strong>${mode.toUpperCase()}</strong>
            </div>
        `;
    } catch (error) {
        document.getElementById('config-status').innerHTML = `
            <div class="status error">Error: ${error.message}</div>
        `;
    }
}

async function storePattern() {
    const text = document.getElementById('store-text').value;
    
    try {
        const response = await fetch(`${API_BASE}/llm/store`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, mode: currentMode })
        });
        const data = await response.json();
        
        document.getElementById('store-result').innerHTML = `
            <div class="result">
                <h3>✓ Stored Successfully</h3>
                <div class="metric">
                    <span class="metric-label">Pattern ID:</span>
                    <span class="metric-value">${data.pattern_id}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Activated Locations:</span>
                    <span class="metric-value">${data.activated_locations}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Mode:</span>
                    <span class="metric-value">${currentMode}</span>
                </div>
            </div>
        `;
        
        listPatterns();
    } catch (error) {
        document.getElementById('store-result').innerHTML = `
            <div class="result" style="border-color: #dc2626;">
                <h3>Error</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
}

async function recallPatterns() {
    const query = document.getElementById('recall-query').value;
    
    try {
        const response = await fetch(`${API_BASE}/llm/recall`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, mode: currentMode, top_k: 5 })
        });
        const data = await response.json();
        
        let patternsHTML = '';
        data.recalled_patterns.forEach(pattern => {
            patternsHTML += `
                <div class="pattern-item">
                    <div>${pattern.text}</div>
                    <div class="similarity-bar">
                        <div class="similarity-fill" style="width: ${pattern.similarity * 100}%"></div>
                    </div>
                    <small style="color: #666;">Similarity: ${(pattern.similarity * 100).toFixed(1)}%</small>
                </div>
            `;
        });
        
        document.getElementById('recall-result').innerHTML = `
            <div class="result">
                <h3><span class="system-label system1">System 1</span>Fast Recall</h3>
                <div class="metric">
                    <span class="metric-label">Recall Time:</span>
                    <span class="metric-value">${data.recall_time_ms.toFixed(2)}ms</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Confidence:</span>
                    <span class="metric-value">${data.confidence.toFixed(2)}</span>
                </div>
                <div style="margin-top: 15px;">
                    ${patternsHTML || '<p style="color: #666;">No similar patterns found</p>'}
                </div>
            </div>
        `;
    } catch (error) {
        document.getElementById('recall-result').innerHTML = `
            <div class="result" style="border-color: #dc2626;">
                <h3>Error</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
}

async function hybridQuery() {
    const query = document.getElementById('hybrid-query').value;
    
    try {
        const response = await fetch(`${API_BASE}/llm/hybrid`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                query, 
                use_sdm: true, 
                mode: currentMode,
                sdm_threshold: 0.5
            })
        });
        const data = await response.json();
        
        let system1HTML = '';
        if (data.system1_result && data.system1_result.patterns) {
            system1HTML = data.system1_result.patterns.map(p => `
                <div class="pattern-item">
                    <div>${p.text}</div>
                    <small style="color: #666;">Similarity: ${(p.similarity * 100).toFixed(1)}%</small>
                </div>
            `).join('');
        }
        
        document.getElementById('hybrid-result').innerHTML = `
            <div class="result">
                <h3>
                    <span class="system-label system1">System 1</span>
                    <span class="system-label system2">System 2</span>
                    Hybrid Response
                </h3>
                <div class="metric">
                    <span class="metric-label">Processing Time:</span>
                    <span class="metric-value">${data.processing_time_ms.toFixed(2)}ms</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Used SDM:</span>
                    <span class="metric-value">${data.used_sdm ? '✓ Yes' : '✗ No'}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Used LLM:</span>
                    <span class="metric-value">${data.used_llm ? '✓ Yes' : '✗ No'}</span>
                </div>
                
                ${system1HTML ? `
                    <div style="margin-top: 20px;">
                        <h4 style="color: #667eea; margin-bottom: 10px;">System 1 Retrieved:</h4>
                        ${system1HTML}
                    </div>
                ` : ''}
                
                <div style="margin-top: 20px; padding: 15px; background: white; border-radius: 8px;">
                    <h4 style="color: #667eea; margin-bottom: 10px;">Combined Answer:</h4>
                    <p style="line-height: 1.6; white-space: pre-wrap;">${data.combined_answer}</p>
                </div>
            </div>
        `;
    } catch (error) {
        document.getElementById('hybrid-result').innerHTML = `
            <div class="result" style="border-color: #dc2626;">
                <h3>Error</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
}

async function listPatterns() {
    try {
        const response = await fetch(`${API_BASE}/llm/patterns`);
        const data = await response.json();
        
        if (data.total_patterns === 0) {
            document.getElementById('patterns-list').innerHTML = `
                <p style="color: #666; margin-top: 15px;">No patterns stored yet</p>
            `;
            return;
        }
        
        const patternsHTML = data.patterns.map(p => `
            <div class="pattern-item">
                <strong>${p.text}</strong>
                <div style="margin-top: 5px; font-size: 12px; color: #666;">
                    ID: ${p.pattern_id} | Mode: ${p.mode}
                </div>
            </div>
        `).join('');
        
        document.getElementById('patterns-list').innerHTML = `
            <div style="margin-top: 15px;">
                <p style="margin-bottom: 10px;"><strong>Total: ${data.total_patterns} patterns</strong>
                ${patternsHTML}
            </div>
        `;
    } catch (error) {
        document.getElementById('patterns-list').innerHTML = `
            <p style="color: #dc2626; margin-top: 15px;">Error loading patterns</p>
        `;
    }
}

async function clearPatterns() {
    if (!confirm('Clear all stored patterns?')) return;
    
    try {
        await fetch(`${API_BASE}/llm/clear`, { method: 'DELETE' });
        listPatterns();
        document.getElementById('patterns-list').innerHTML = `
            <div class="status success" style="margin-top: 15px;">
                All patterns cleared
            </div>
        `;
    } catch (error) {
        alert('Error clearing patterns');
    }
}

// Load patterns on start
listPatterns();