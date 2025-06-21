// RAG System JavaScript

let ragData = {
    documents: [],
    queries: []
};

document.addEventListener('DOMContentLoaded', function() {
    loadRAGData();
    setupEventListeners();
});

async function loadRAGData() {
    try {
        const [statsResponse, documentsResponse, historyResponse] = await Promise.all([
            fetch('/rag/stats'),
            fetch('/rag/documents'),
            fetch('/rag/history')
        ]);

        const statsData = await statsResponse.json();
        const documentsData = await documentsResponse.json();
        const historyData = await historyResponse.json();

        ragData.documents = documentsData.documents || [];
        ragData.queries = historyData.queries || [];
        
        // Update statistics
        updateStatistics(statsData);
        
        // Render data
        renderDocuments();
        renderQueryHistory();

    } catch (error) {
        console.error('Error loading RAG data:', error);
        HazardSafeKG.showNotification('Error loading RAG data', 'error');
    }
}

function updateStatistics(stats) {
    document.getElementById('document-count').textContent = stats.documents || 0;
    document.getElementById('query-count').textContent = stats.queries || 0;
    document.getElementById('document-types').textContent = stats.document_types || 0;
    document.getElementById('total-tags').textContent = stats.total_tags || 0;
}

function setupEventListeners() {
    // Query form submission
    document.getElementById('queryForm').addEventListener('submit', function(e) {
        e.preventDefault();
        submitQuery();
    });

    // Validation form submission
    document.getElementById('validationForm').addEventListener('submit', function(e) {
        e.preventDefault();
        validateSafety();
    });

    // Upload form submission
    document.getElementById('uploadForm').addEventListener('submit', function(e) {
        e.preventDefault();
        uploadDocument();
    });

    // Auto-suggestions for question input
    const questionInput = document.getElementById('questionInput');
    questionInput.addEventListener('input', HazardSafeKG.debounce(async function() {
        if (this.value.length > 2) {
            await loadSuggestions(this.value);
        }
    }, 300));
}

function renderDocuments() {
    const tbody = document.getElementById('documents-tbody');
    tbody.innerHTML = '';

    ragData.documents.forEach(doc => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${doc.title}</strong></td>
            <td><span class="badge bg-secondary">${doc.document_type}</span></td>
            <td>${doc.tags ? doc.tags.join(', ') : 'None'}</td>
            <td>${doc.upload_date}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="showDocumentDetails('${doc.id}')">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteDocument('${doc.id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function renderQueryHistory() {
    const historyContainer = document.getElementById('query-history');
    
    if (ragData.queries.length === 0) {
        historyContainer.innerHTML = '<p class="text-muted">No query history yet.</p>';
        return;
    }

    let html = '';
    ragData.queries.slice(0, 5).forEach(query => {
        const confidence = Math.round(query.confidence * 100);
        const timestamp = new Date(query.timestamp).toLocaleString();
        
        html += `
            <div class="border-bottom pb-2 mb-2">
                <small class="text-muted">${timestamp}</small>
                <p class="mb-1"><strong>${query.question}</strong></p>
                <p class="mb-1 small">${query.answer.substring(0, 100)}...</p>
                <span class="badge bg-${confidence > 80 ? 'success' : confidence > 60 ? 'warning' : 'danger'}">${confidence}% confidence</span>
            </div>
        `;
    });
    
    historyContainer.innerHTML = html;
}

async function submitQuery() {
    const question = document.getElementById('questionInput').value;
    const contextType = document.getElementById('contextType').value;
    const maxResults = parseInt(document.getElementById('maxResults').value);
    const includeSources = document.getElementById('includeSources').checked;

    if (!question.trim()) {
        HazardSafeKG.showNotification('Please enter a question', 'warning');
        return;
    }

    const submitButton = document.querySelector('#queryForm button[type="submit"]');
    const originalText = submitButton.innerHTML;
    HazardSafeKG.showLoading(submitButton);

    try {
        const response = await fetch('/rag/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: question,
                context_type: contextType,
                max_results: maxResults,
                include_sources: includeSources
            })
        });

        const result = await response.json();
        displayQueryResult(result);
        
        // Reload data to update statistics
        await loadRAGData();

    } catch (error) {
        console.error('Error submitting query:', error);
        HazardSafeKG.showNotification('Error processing query', 'error');
    } finally {
        HazardSafeKG.hideLoading(submitButton, originalText);
    }
}

function displayQueryResult(result) {
    const resultsContainer = document.getElementById('query-results');
    const confidence = Math.round(result.confidence * 100);
    
    let html = `
        <div class="alert alert-info">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h6><i class="fas fa-robot me-2"></i>AI Response</h6>
                    <p class="mb-2">${result.answer}</p>
                    <span class="badge bg-${confidence > 80 ? 'success' : confidence > 60 ? 'warning' : 'danger'}">${confidence}% confidence</span>
                </div>
                <small class="text-muted">${new Date(result.timestamp).toLocaleString()}</small>
            </div>
        </div>
    `;

    if (result.sources && result.sources.length > 0) {
        html += `
            <div class="mt-3">
                <h6><i class="fas fa-book me-2"></i>Sources</h6>
                <ul class="list-unstyled">
        `;
        
        result.sources.forEach(sourceId => {
            const sourceDoc = ragData.documents.find(doc => doc.id === sourceId);
            if (sourceDoc) {
                html += `<li><i class="fas fa-file-alt me-2"></i>${sourceDoc.title}</li>`;
            }
        });
        
        html += '</ul></div>';
    }

    resultsContainer.innerHTML = html;
}

async function validateSafety() {
    const substanceName = document.getElementById('substanceName').value;
    const containerType = document.getElementById('containerType').value;
    const temperature = parseFloat(document.getElementById('temperature').value) || 25;
    const pressure = parseFloat(document.getElementById('pressure').value) || 1.0;

    if (!substanceName || !containerType) {
        HazardSafeKG.showNotification('Please fill in substance name and container type', 'warning');
        return;
    }

    const submitButton = document.querySelector('#validationForm button[type="submit"]');
    const originalText = submitButton.innerHTML;
    HazardSafeKG.showLoading(submitButton);

    try {
        const response = await fetch('/rag/validate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                substance_name: substanceName,
                container_type: containerType,
                test_conditions: {
                    temperature: temperature,
                    pressure: pressure
                },
                validation_criteria: ['compatibility', 'temperature', 'pressure']
            })
        });

        const result = await response.json();
        displayValidationResult(result);

    } catch (error) {
        console.error('Error validating safety:', error);
        HazardSafeKG.showNotification('Error validating safety', 'error');
    } finally {
        HazardSafeKG.hideLoading(submitButton, originalText);
    }
}

function displayValidationResult(result) {
    const resultsContainer = document.getElementById('query-results');
    
    let html = `
        <div class="alert alert-${result.valid ? 'success' : 'danger'}">
            <h6><i class="fas fa-shield-alt me-2"></i>Safety Validation Result</h6>
            <p class="mb-2"><strong>Status:</strong> ${result.valid ? 'Valid' : 'Invalid'}</p>
            <small class="text-muted">${new Date(result.validation_date).toLocaleString()}</small>
        </div>
    `;

    if (result.recommendations && result.recommendations.length > 0) {
        html += `
            <div class="alert alert-success">
                <h6><i class="fas fa-check-circle me-2"></i>Recommendations</h6>
                <ul class="mb-0">
                    ${result.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    if (result.warnings && result.warnings.length > 0) {
        html += `
            <div class="alert alert-warning">
                <h6><i class="fas fa-exclamation-triangle me-2"></i>Warnings</h6>
                <ul class="mb-0">
                    ${result.warnings.map(warning => `<li>${warning}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    if (result.errors && result.errors.length > 0) {
        html += `
            <div class="alert alert-danger">
                <h6><i class="fas fa-times-circle me-2"></i>Errors</h6>
                <ul class="mb-0">
                    ${result.errors.map(error => `<li>${error}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    resultsContainer.innerHTML = html;
}

async function uploadDocument() {
    const form = document.getElementById('uploadForm');
    if (!HazardSafeKG.validateForm(form)) {
        HazardSafeKG.showNotification('Please fill in all required fields', 'warning');
        return;
    }

    const formData = new FormData();
    formData.append('title', document.getElementById('documentTitle').value);
    formData.append('description', document.getElementById('documentDescription').value);
    formData.append('document_type', document.getElementById('documentType').value);
    formData.append('tags', document.getElementById('documentTags').value);
    formData.append('file', document.getElementById('documentFile').files[0]);

    const submitButton = document.querySelector('#uploadForm button[type="submit"]');
    const originalText = submitButton.innerHTML;
    HazardSafeKG.showLoading(submitButton);

    try {
        const response = await fetch('/rag/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        
        if (response.ok) {
            HazardSafeKG.showNotification('Document uploaded successfully', 'success');
            form.reset();
            await loadRAGData();
        } else {
            throw new Error(result.message || 'Upload failed');
        }

    } catch (error) {
        console.error('Error uploading document:', error);
        HazardSafeKG.showNotification('Error uploading document', 'error');
    } finally {
        HazardSafeKG.hideLoading(submitButton, originalText);
    }
}

async function loadSuggestions(query) {
    try {
        const response = await fetch(`/rag/suggestions?query=${encodeURIComponent(query)}`);
        const result = await response.json();
        
        // In a real implementation, you would show these suggestions in a dropdown
        console.log('Suggestions:', result.suggestions);
        
    } catch (error) {
        console.error('Error loading suggestions:', error);
    }
}

function loadQuickQuestion(question) {
    document.getElementById('questionInput').value = question;
    document.getElementById('contextType').value = 'all';
    document.getElementById('maxResults').value = '5';
    document.getElementById('includeSources').checked = true;
}

async function showDocumentDetails(documentId) {
    try {
        const document = ragData.documents.find(doc => doc.id === documentId);
        if (!document) {
            HazardSafeKG.showNotification('Document not found', 'error');
            return;
        }

        const modal = new bootstrap.Modal(document.getElementById('documentDetailsModal'));
        const content = document.getElementById('documentDetailsContent');
        
        let html = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Document Information</h6>
                    <table class="table table-sm">
                        <tr><td><strong>ID:</strong></td><td>${document.id}</td></tr>
                        <tr><td><strong>Title:</strong></td><td>${document.title}</td></tr>
                        <tr><td><strong>Type:</strong></td><td><span class="badge bg-secondary">${document.document_type}</span></td></tr>
                        <tr><td><strong>Upload Date:</strong></td><td>${document.upload_date}</td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>Content Preview</h6>
                    <div class="border p-3 bg-light" style="max-height: 200px; overflow-y: auto;">
                        <small>${document.content.substring(0, 500)}...</small>
                    </div>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-12">
                    <h6>Tags</h6>
                    <div>
                        ${document.tags ? document.tags.map(tag => `<span class="badge bg-info me-1">${tag}</span>`).join('') : 'No tags'}
                    </div>
                </div>
            </div>
        `;
        
        content.innerHTML = html;
        modal.show();

    } catch (error) {
        console.error('Error showing document details:', error);
        HazardSafeKG.showNotification('Error loading document details', 'error');
    }
}

function deleteDocument(documentId) {
    if (confirm('Are you sure you want to delete this document?')) {
        HazardSafeKG.showNotification('Delete functionality not yet implemented', 'info');
    }
}

function clearResults() {
    document.getElementById('query-results').innerHTML = `
        <div class="text-center text-muted py-5">
            <i class="fas fa-robot fa-3x mb-3"></i>
            <p>Ask a question to get AI-powered safety insights</p>
        </div>
    `;
}

function exportResults() {
    const resultsContainer = document.getElementById('query-results');
    const content = resultsContainer.innerText;
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'rag-results.txt';
    a.click();
    window.URL.revokeObjectURL(url);
    
    HazardSafeKG.showNotification('Results exported successfully', 'success');
}

function downloadDocument() {
    HazardSafeKG.showNotification('Download functionality not yet implemented', 'info');
} 