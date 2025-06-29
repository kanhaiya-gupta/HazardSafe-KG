/**
 * Validation Engine JavaScript functionality
 */

// Load validation statistics on page load
document.addEventListener('DOMContentLoaded', function() {
    loadValidationStats();
    setupEventListeners();
});

function setupEventListeners() {
    // CSV validation form
    document.getElementById('csv-validation-form').addEventListener('submit', handleCSVValidation);
    
    // Data validation form
    document.getElementById('data-validation-form').addEventListener('submit', handleDataValidation);
    
    // File upload handling
    document.getElementById('csv-file').addEventListener('change', handleFileSelect);
    
    // Drag and drop functionality
    const uploadArea = document.getElementById('upload-area');
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('drop', handleDrop);
    uploadArea.addEventListener('click', () => document.getElementById('csv-file').click());
}

async function loadValidationStats() {
    try {
        const response = await fetch('/validation/stats');
        const stats = await response.json();
        
        document.getElementById('rules-count').textContent = stats.validation_rules;
        document.getElementById('data-types-count').textContent = stats.data_types.length;
        document.getElementById('total-rules-count').textContent = stats.total_rules;
        document.getElementById('status').textContent = stats.status;
        
    } catch (error) {
        console.error('Error loading validation stats:', error);
    }
}

async function handleCSVValidation(event) {
    event.preventDefault();
    
    const formData = new FormData();
    const fileInput = document.getElementById('csv-file');
    const dataType = document.getElementById('data-type').value;
    
    if (!fileInput.files[0]) {
        showResult('csv-validation-result', 'Please select a CSV file', 'error');
        return;
    }
    
    if (!dataType) {
        showResult('csv-validation-result', 'Please select a data type', 'error');
        return;
    }
    
    formData.append('file', fileInput.files[0]);
    formData.append('data_type', dataType);
    
    try {
        const response = await fetch('/validation/validate-csv', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        displayCSVValidationResult(result);
        
    } catch (error) {
        console.error('Error validating CSV:', error);
        showResult('csv-validation-result', 'Error validating CSV file', 'error');
    }
}

async function handleDataValidation(event) {
    event.preventDefault();
    
    const dataType = document.getElementById('data-type-obj').value;
    const dataJson = document.getElementById('data-json').value;
    
    if (!dataType) {
        showResult('data-validation-result', 'Please select a data type', 'error');
        return;
    }
    
    if (!dataJson) {
        showResult('data-validation-result', 'Please enter data in JSON format', 'error');
        return;
    }
    
    try {
        const data = JSON.parse(dataJson);
        
        const response = await fetch('/validation/validate-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                data: data,
                data_type: dataType
            })
        });
        
        const result = await response.json();
        displayDataValidationResult(result);
        
    } catch (error) {
        console.error('Error validating data:', error);
        showResult('data-validation-result', 'Error validating data', 'error');
    }
}

async function checkCompatibility() {
    const substanceData = document.getElementById('substance-data').value;
    const containerData = document.getElementById('container-data').value;
    
    if (!substanceData || !containerData) {
        showResult('compatibility-result', 'Please enter both substance and container data', 'error');
        return;
    }
    
    try {
        const substance = JSON.parse(substanceData);
        const container = JSON.parse(containerData);
        
        const response = await fetch('/validation/validate-compatibility', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                substance_data: substance,
                container_data: container
            })
        });
        
        const result = await response.json();
        displayCompatibilityResult(result);
        
    } catch (error) {
        console.error('Error checking compatibility:', error);
        showResult('compatibility-result', 'Error checking compatibility', 'error');
    }
}

async function validateFormula() {
    const formula = document.getElementById('chemical-formula').value.trim();
    
    if (!formula) {
        showResult('formula-validation-result', 'Please enter a chemical formula', 'error');
        return;
    }
    
    try {
        const response = await fetch('/validation/validate-formula', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                formula: formula
            })
        });
        
        const result = await response.json();
        displayFormulaValidationResult(result);
        
    } catch (error) {
        console.error('Error validating formula:', error);
        showResult('formula-validation-result', 'Error validating chemical formula', 'error');
    }
}

async function loadRules() {
    const dataType = document.getElementById('rules-selector').value;
    
    if (!dataType) {
        document.getElementById('rules-display').innerHTML = '';
        return;
    }
    
    try {
        const response = await fetch(`/validation/rules/${dataType}`);
        const result = await response.json();
        displayRules(result);
        
    } catch (error) {
        console.error('Error loading rules:', error);
        document.getElementById('rules-display').innerHTML = '<div class="alert alert-danger">Error loading validation rules</div>';
    }
}

function displayCSVValidationResult(result) {
    const container = document.getElementById('csv-validation-result');
    const validation = result.validation_result;
    
    let html = `<h6>Validation Results for ${result.filename}</h6>`;
    
    if (validation.valid) {
        html += `<div class="result-success">
            <i class="fas fa-check-circle me-2"></i>
            <strong>Validation Passed!</strong><br>
            Total rows: ${validation.total_rows}<br>
            Valid rows: ${validation.valid_rows}
        </div>`;
    } else {
        html += `<div class="result-error">
            <i class="fas fa-times-circle me-2"></i>
            <strong>Validation Failed!</strong>
        </div>`;
    }
    
    if (validation.errors && validation.errors.length > 0) {
        html += `<div class="result-error">
            <strong>Errors:</strong><br>
            <ul>${validation.errors.map(error => `<li>${error}</li>`).join('')}</ul>
        </div>`;
    }
    
    if (validation.warnings && validation.warnings.length > 0) {
        html += `<div class="result-warning">
            <strong>Warnings:</strong><br>
            <ul>${validation.warnings.map(warning => `<li>${warning}</li>`).join('')}</ul>
        </div>`;
    }
    
    container.innerHTML = html;
}

function displayDataValidationResult(result) {
    const container = document.getElementById('data-validation-result');
    const validation = result.validation_result;
    
    let html = `<h6>Data Validation Results</h6>`;
    
    if (validation.valid) {
        html += `<div class="result-success">
            <i class="fas fa-check-circle me-2"></i>
            <strong>Data is valid!</strong>
        </div>`;
    } else {
        html += `<div class="result-error">
            <i class="fas fa-times-circle me-2"></i>
            <strong>Data validation failed!</strong>
        </div>`;
    }
    
    if (validation.errors && validation.errors.length > 0) {
        html += `<div class="result-error">
            <strong>Errors:</strong><br>
            <ul>${validation.errors.map(error => `<li>${error}</li>`).join('')}</ul>
        </div>`;
    }
    
    if (validation.warnings && validation.warnings.length > 0) {
        html += `<div class="result-warning">
            <strong>Warnings:</strong><br>
            <ul>${validation.warnings.map(warning => `<li>${warning}</li>`).join('')}</ul>
        </div>`;
    }
    
    container.innerHTML = html;
}

function displayCompatibilityResult(result) {
    const container = document.getElementById('compatibility-result');
    const validation = result.validation_result;
    
    let html = `<h6>Compatibility Check Results</h6>`;
    
    if (validation.compatible) {
        html += `<div class="result-success">
            <i class="fas fa-check-circle me-2"></i>
            <strong>Compatible!</strong> ${validation.reason || ''}
        </div>`;
    } else {
        html += `<div class="result-error">
            <i class="fas fa-times-circle me-2"></i>
            <strong>Not Compatible!</strong> ${validation.reason || ''}
        </div>`;
    }
    
    if (validation.recommendations && validation.recommendations.length > 0) {
        html += `<div class="result-warning">
            <strong>Recommendations:</strong><br>
            <ul>${validation.recommendations.map(rec => `<li>${rec}</li>`).join('')}</ul>
        </div>`;
    }
    
    container.innerHTML = html;
}

function displayFormulaValidationResult(result) {
    const container = document.getElementById('formula-validation-result');
    const validation = result.validation_result;
    
    let html = `<h6>Formula Validation Results for ${result.formula}</h6>`;
    
    if (validation.valid) {
        html += `<div class="result-success">
            <i class="fas fa-check-circle me-2"></i>
            <strong>Valid chemical formula!</strong>
        </div>`;
        
        if (validation.elements) {
            html += `<div class="result-success">
                <strong>Elements:</strong> ${validation.elements.join(', ')}
            </div>`;
        }
    } else {
        html += `<div class="result-error">
            <i class="fas fa-times-circle me-2"></i>
            <strong>Invalid chemical formula!</strong> ${validation.reason || ''}
        </div>`;
    }
    
    container.innerHTML = html;
}

function displayRules(result) {
    const container = document.getElementById('rules-display');
    const rules = result.rules;
    
    let html = `<h5>Validation Rules for ${result.data_type}</h5>`;
    
    // Required fields
    if (rules.required_fields) {
        html += `<div class="rule-item">
            <strong>Required Fields:</strong> ${rules.required_fields.join(', ')}
        </div>`;
    }
    
    // Field types
    if (rules.field_types) {
        html += `<div class="rule-item">
            <strong>Field Types:</strong><br>
            <ul>${Object.entries(rules.field_types).map(([field, type]) => `<li>${field}: ${type}</li>`).join('')}</ul>
        </div>`;
    }
    
    // Constraints
    if (rules.constraints) {
        html += `<div class="rule-item">
            <strong>Constraints:</strong><br>
            <ul>${Object.entries(rules.constraints).map(([field, constraint]) => 
                `<li>${field}: ${JSON.stringify(constraint)}</li>`
            ).join('')}</ul>
        </div>`;
    }
    
    // Valid values
    if (rules.hazard_classes) {
        html += `<div class="rule-item">
            <strong>Valid Hazard Classes:</strong> ${rules.hazard_classes.join(', ')}
        </div>`;
    }
    
    if (rules.materials) {
        html += `<div class="rule-item">
            <strong>Valid Materials:</strong> ${rules.materials.join(', ')}
        </div>`;
    }
    
    if (rules.test_types) {
        html += `<div class="rule-item">
            <strong>Valid Test Types:</strong> ${rules.test_types.join(', ')}
        </div>`;
    }
    
    if (rules.risk_levels) {
        html += `<div class="rule-item">
            <strong>Valid Risk Levels:</strong> ${rules.risk_levels.join(', ')}
        </div>`;
    }
    
    container.innerHTML = html;
}

function showResult(containerId, message, type) {
    const container = document.getElementById(containerId);
    const className = type === 'error' ? 'result-error' : type === 'warning' ? 'result-warning' : 'result-success';
    const icon = type === 'error' ? 'times-circle' : type === 'warning' ? 'exclamation-triangle' : 'check-circle';
    
    container.innerHTML = `<div class="${className}">
        <i class="fas fa-${icon} me-2"></i>${message}
    </div>`;
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        const uploadArea = document.getElementById('upload-area');
        uploadArea.innerHTML = `
            <i class="fas fa-file-csv fa-3x text-success mb-3"></i>
            <p class="mb-2"><strong>${file.name}</strong></p>
            <p class="text-muted">Size: ${(file.size / 1024).toFixed(2)} KB</p>
        `;
    }
}

function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const fileInput = document.getElementById('csv-file');
        fileInput.files = files;
        handleFileSelect({ target: fileInput });
    }
}
