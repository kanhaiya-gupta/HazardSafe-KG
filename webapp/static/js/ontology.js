// Ontology Management JavaScript

let ontologyData = {
    classes: [],
    properties: [],
    relationships: []
};

document.addEventListener('DOMContentLoaded', function() {
    loadOntologyData();
});

async function loadOntologyData() {
    try {
        // Load all ontology data
        const [classesResponse, propertiesResponse, relationshipsResponse, statsResponse] = await Promise.all([
            fetch('/ontology/classes'),
            fetch('/ontology/properties'),
            fetch('/ontology/relationships'),
            fetch('/ontology/stats')
        ]);

        const classesData = await classesResponse.json();
        const propertiesData = await propertiesResponse.json();
        const relationshipsData = await relationshipsResponse.json();
        const statsData = await statsResponse.json();

        ontologyData.classes = classesData.classes || [];
        ontologyData.properties = propertiesData.properties || [];
        ontologyData.relationships = relationshipsData.relationships || [];

        // Update statistics
        updateStatistics(statsData);
        
        // Render data
        renderClasses();
        renderProperties();
        renderRelationships();
        
        // Populate dropdowns
        populateClassDropdowns();

    } catch (error) {
        console.error('Error loading ontology data:', error);
        HazardSafeKG.showNotification('Error loading ontology data', 'error');
    }
}

function updateStatistics(stats) {
    document.getElementById('class-count').textContent = stats.classes || 0;
    document.getElementById('property-count').textContent = stats.properties || 0;
    document.getElementById('relationship-count').textContent = stats.relationships || 0;
}

function renderClasses() {
    const tbody = document.getElementById('classes-tbody');
    tbody.innerHTML = '';

    ontologyData.classes.forEach(cls => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${cls.name}</strong></td>
            <td>${cls.description}</td>
            <td>${cls.properties ? cls.properties.join(', ') : 'None'}</td>
            <td>${cls.parent_class || 'None'}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="editClass('${cls.name}')">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteClass('${cls.name}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function renderProperties() {
    const tbody = document.getElementById('properties-tbody');
    tbody.innerHTML = '';

    ontologyData.properties.forEach(prop => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${prop.name}</strong></td>
            <td>${prop.description}</td>
            <td><span class="badge bg-secondary">${prop.data_type}</span></td>
            <td>${prop.domain}</td>
            <td>${prop.range}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="editProperty('${prop.name}')">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteProperty('${prop.name}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function renderRelationships() {
    const tbody = document.getElementById('relationships-tbody');
    tbody.innerHTML = '';

    ontologyData.relationships.forEach(rel => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${rel.name}</strong></td>
            <td>${rel.description}</td>
            <td>${rel.source_class}</td>
            <td>${rel.target_class}</td>
            <td>${rel.properties ? rel.properties.join(', ') : 'None'}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="editRelationship('${rel.name}')">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteRelationship('${rel.name}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function populateClassDropdowns() {
    const classOptions = ontologyData.classes.map(cls => 
        `<option value="${cls.name}">${cls.name}</option>`
    ).join('');

    // Populate all class dropdowns
    const dropdowns = ['parentClass', 'domain', 'sourceClass', 'targetClass'];
    dropdowns.forEach(id => {
        const dropdown = document.getElementById(id);
        if (dropdown) {
            dropdown.innerHTML = '<option value="">Select a class...</option>' + classOptions;
        }
    });
}

// Modal functions
function showCreateClassModal() {
    const modal = new bootstrap.Modal(document.getElementById('createClassModal'));
    document.getElementById('createClassForm').reset();
    populateClassDropdowns();
    modal.show();
}

function showCreatePropertyModal() {
    const modal = new bootstrap.Modal(document.getElementById('createPropertyModal'));
    document.getElementById('createPropertyForm').reset();
    populateClassDropdowns();
    modal.show();
}

function showCreateRelationshipModal() {
    const modal = new bootstrap.Modal(document.getElementById('createRelationshipModal'));
    document.getElementById('createRelationshipForm').reset();
    populateClassDropdowns();
    modal.show();
}

// Create functions
async function createClass() {
    const form = document.getElementById('createClassForm');
    if (!HazardSafeKG.validateForm(form)) {
        HazardSafeKG.showNotification('Please fill in all required fields', 'warning');
        return;
    }

    const classData = {
        name: document.getElementById('className').value,
        description: document.getElementById('classDescription').value,
        parent_class: document.getElementById('parentClass').value || null,
        properties: []
    };

    try {
        const response = await fetch('/ontology/classes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(classData)
        });

        if (response.ok) {
            HazardSafeKG.showNotification('Class created successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('createClassModal')).hide();
            await loadOntologyData();
        } else {
            throw new Error('Failed to create class');
        }
    } catch (error) {
        console.error('Error creating class:', error);
        HazardSafeKG.showNotification('Error creating class', 'error');
    }
}

async function createProperty() {
    const form = document.getElementById('createPropertyForm');
    if (!HazardSafeKG.validateForm(form)) {
        HazardSafeKG.showNotification('Please fill in all required fields', 'warning');
        return;
    }

    const propertyData = {
        name: document.getElementById('propertyName').value,
        description: document.getElementById('propertyDescription').value,
        data_type: document.getElementById('dataType').value,
        domain: document.getElementById('domain').value,
        range: document.getElementById('range').value
    };

    try {
        const response = await fetch('/ontology/properties', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(propertyData)
        });

        if (response.ok) {
            HazardSafeKG.showNotification('Property created successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('createPropertyModal')).hide();
            await loadOntologyData();
        } else {
            throw new Error('Failed to create property');
        }
    } catch (error) {
        console.error('Error creating property:', error);
        HazardSafeKG.showNotification('Error creating property', 'error');
    }
}

async function createRelationship() {
    const form = document.getElementById('createRelationshipForm');
    if (!HazardSafeKG.validateForm(form)) {
        HazardSafeKG.showNotification('Please fill in all required fields', 'warning');
        return;
    }

    const relationshipData = {
        name: document.getElementById('relationshipName').value,
        description: document.getElementById('relationshipDescription').value,
        source_class: document.getElementById('sourceClass').value,
        target_class: document.getElementById('targetClass').value,
        properties: []
    };

    try {
        const response = await fetch('/ontology/relationships', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(relationshipData)
        });

        if (response.ok) {
            HazardSafeKG.showNotification('Relationship created successfully', 'success');
            bootstrap.Modal.getInstance(document.getElementById('createRelationshipModal')).hide();
            await loadOntologyData();
        } else {
            throw new Error('Failed to create relationship');
        }
    } catch (error) {
        console.error('Error creating relationship:', error);
        HazardSafeKG.showNotification('Error creating relationship', 'error');
    }
}

// Validation and export functions
async function validateOntology() {
    try {
        const response = await fetch('/ontology/validate');
        const result = await response.json();

        if (result.valid) {
            HazardSafeKG.showNotification('Ontology validation passed', 'success');
            document.getElementById('validation-status').textContent = 'Valid';
            document.getElementById('validation-status').className = 'text-success';
        } else {
            HazardSafeKG.showNotification('Ontology validation failed', 'error');
            document.getElementById('validation-status').textContent = 'Invalid';
            document.getElementById('validation-status').className = 'text-danger';
        }

        // Show detailed results
        console.log('Validation results:', result);
    } catch (error) {
        console.error('Error validating ontology:', error);
        HazardSafeKG.showNotification('Error validating ontology', 'error');
    }
}

async function exportOWL() {
    try {
        const response = await fetch('/ontology/export/owl');
        const result = await response.json();
        
        // Create and download file
        const blob = new Blob([result.owl_content], { type: 'application/xml' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'hazardsafe-ontology.owl';
        a.click();
        window.URL.revokeObjectURL(url);
        
        HazardSafeKG.showNotification('OWL file exported successfully', 'success');
    } catch (error) {
        console.error('Error exporting OWL:', error);
        HazardSafeKG.showNotification('Error exporting OWL file', 'error');
    }
}

async function exportSHACL() {
    try {
        const response = await fetch('/ontology/export/shacl');
        const result = await response.json();
        
        // Create and download file
        const blob = new Blob([result.shacl_content], { type: 'text/turtle' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'hazardsafe-shacl.ttl';
        a.click();
        window.URL.revokeObjectURL(url);
        
        HazardSafeKG.showNotification('SHACL file exported successfully', 'success');
    } catch (error) {
        console.error('Error exporting SHACL:', error);
        HazardSafeKG.showNotification('Error exporting SHACL file', 'error');
    }
}

// Edit and delete functions (placeholder implementations)
function editClass(className) {
    HazardSafeKG.showNotification(`Edit functionality for class '${className}' not yet implemented`, 'info');
}

function deleteClass(className) {
    if (confirm(`Are you sure you want to delete the class '${className}'?`)) {
        HazardSafeKG.showNotification(`Delete functionality for class '${className}' not yet implemented`, 'info');
    }
}

function editProperty(propertyName) {
    HazardSafeKG.showNotification(`Edit functionality for property '${propertyName}' not yet implemented`, 'info');
}

function deleteProperty(propertyName) {
    if (confirm(`Are you sure you want to delete the property '${propertyName}'?`)) {
        HazardSafeKG.showNotification(`Delete functionality for property '${propertyName}' not yet implemented`, 'info');
    }
}

function editRelationship(relationshipName) {
    HazardSafeKG.showNotification(`Edit functionality for relationship '${relationshipName}' not yet implemented`, 'info');
}

function deleteRelationship(relationshipName) {
    if (confirm(`Are you sure you want to delete the relationship '${relationshipName}'?`)) {
        HazardSafeKG.showNotification(`Delete functionality for relationship '${relationshipName}' not yet implemented`, 'info');
    }
}

// Ontology management JavaScript for HazardSafe-KG platform

class OntologyManager {
    constructor() {
        this.baseUrl = '/ontology';
        this.init();
    }

    async init() {
        await this.loadOntologyInfo();
        await this.loadSupportedFormats();
        this.setupEventListeners();
    }

    async loadOntologyInfo() {
        try {
            const response = await fetch(this.baseUrl);
            const data = await response.json();
            
            document.getElementById('ontology-status').textContent = data.status;
            document.getElementById('ontology-triples').textContent = data.statistics.triples || 0;
            document.getElementById('ontology-classes').textContent = data.statistics.classes || 0;
            document.getElementById('ontology-properties').textContent = data.statistics.properties || 0;
            document.getElementById('ontology-instances').textContent = data.statistics.instances || 0;
            
        } catch (error) {
            console.error('Failed to load ontology info:', error);
            this.showNotification('Failed to load ontology information', 'error');
        }
    }

    async loadSupportedFormats() {
        try {
            const response = await fetch(`${this.baseUrl}/formats`);
            const data = await response.json();
            
            const formatList = document.getElementById('supported-formats');
            formatList.innerHTML = '';
            
            data.supported_formats.forEach(format => {
                const formatItem = document.createElement('div');
                formatItem.className = 'format-item';
                formatItem.innerHTML = `
                    <div class="format-header">
                        <span class="format-extension">${format.extension}</span>
                        <span class="format-name">${format.name}</span>
                    </div>
                    <div class="format-description">${format.description}</div>
                `;
                formatList.appendChild(formatItem);
            });
            
        } catch (error) {
            console.error('Failed to load supported formats:', error);
            this.showNotification('Failed to load supported formats', 'error');
        }
    }

    setupEventListeners() {
        // File upload
        const uploadForm = document.getElementById('upload-form');
        if (uploadForm) {
            uploadForm.addEventListener('submit', (e) => this.handleFileUpload(e));
        }

        // Format conversion
        const convertForm = document.getElementById('convert-form');
        if (convertForm) {
            convertForm.addEventListener('submit', (e) => this.handleFormatConversion(e));
        }

        // Export
        const exportBtn = document.getElementById('export-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.handleExport());
        }

        // CRUD operations
        const addClassBtn = document.getElementById('add-class-btn');
        if (addClassBtn) {
            addClassBtn.addEventListener('click', () => this.showAddClassModal());
        }

        const addPropertyBtn = document.getElementById('add-property-btn');
        if (addPropertyBtn) {
            addPropertyBtn.addEventListener('click', () => this.showAddPropertyModal());
        }

        const addInstanceBtn = document.getElementById('add-instance-btn');
        if (addInstanceBtn) {
            addInstanceBtn.addEventListener('click', () => this.showAddInstanceModal());
        }

        // Validation
        const validateBtn = document.getElementById('validate-btn');
        if (validateBtn) {
            validateBtn.addEventListener('click', () => this.handleValidation());
        }

        // Refresh buttons
        const refreshClassesBtn = document.getElementById('refresh-classes');
        if (refreshClassesBtn) {
            refreshClassesBtn.addEventListener('click', () => this.loadClasses());
        }

        const refreshPropertiesBtn = document.getElementById('refresh-properties');
        if (refreshPropertiesBtn) {
            refreshPropertiesBtn.addEventListener('click', () => this.loadProperties());
        }

        const refreshInstancesBtn = document.getElementById('refresh-instances');
        if (refreshInstancesBtn) {
            refreshInstancesBtn.addEventListener('click', () => this.loadInstances());
        }
    }

    async handleFileUpload(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const fileInput = document.getElementById('ontology-file');
        
        if (!fileInput.files[0]) {
            this.showNotification('Please select a file to upload', 'error');
            return;
        }

        formData.append('file', fileInput.files[0]);

        try {
            const response = await fetch(`${this.baseUrl}/upload`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification(result.message, 'success');
                await this.loadOntologyInfo();
                event.target.reset();
            } else {
                this.showNotification(result.detail, 'error');
            }
        } catch (error) {
            console.error('Upload failed:', error);
            this.showNotification('Failed to upload file', 'error');
        }
    }

    async handleFormatConversion(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const fileInput = document.getElementById('convert-file');
        const outputFormat = document.getElementById('output-format').value;
        
        if (!fileInput.files[0]) {
            this.showNotification('Please select a file to convert', 'error');
            return;
        }

        if (!outputFormat) {
            this.showNotification('Please select output format', 'error');
            return;
        }

        formData.append('input_file', fileInput.files[0]);
        formData.append('output_format', outputFormat);

        try {
            const response = await fetch(`${this.baseUrl}/convert`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification(result.message, 'success');
                
                // Display converted content
                const contentArea = document.getElementById('converted-content');
                if (contentArea) {
                    contentArea.value = result.content;
                    contentArea.style.display = 'block';
                }
                
                event.target.reset();
            } else {
                this.showNotification(result.detail, 'error');
            }
        } catch (error) {
            console.error('Conversion failed:', error);
            this.showNotification('Failed to convert file', 'error');
        }
    }

    async handleExport() {
        const format = document.getElementById('export-format').value || 'turtle';
        
        try {
            const response = await fetch(`${this.baseUrl}/export?format=${format}`);
            const result = await response.json();

            if (response.ok) {
                // Create download link
                const blob = new Blob([result.content], { type: 'text/plain' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `ontology.${format}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showNotification('Ontology exported successfully', 'success');
            } else {
                this.showNotification(result.detail, 'error');
            }
        } catch (error) {
            console.error('Export failed:', error);
            this.showNotification('Failed to export ontology', 'error');
        }
    }

    async loadClasses() {
        try {
            const response = await fetch(`${this.baseUrl}/classes`);
            const data = await response.json();
            
            const classesList = document.getElementById('classes-list');
            classesList.innerHTML = '';
            
            data.classes.forEach(cls => {
                const classItem = document.createElement('div');
                classItem.className = 'class-item';
                classItem.innerHTML = `
                    <div class="class-header">
                        <h4>${cls.label || 'Unnamed Class'}</h4>
                        <span class="class-uri">${cls.uri}</span>
                    </div>
                    <div class="class-comment">${cls.comment || 'No description'}</div>
                    ${cls.superclass ? `<div class="class-superclass">Superclass: ${cls.superclass}</div>` : ''}
                `;
                classesList.appendChild(classItem);
            });
            
        } catch (error) {
            console.error('Failed to load classes:', error);
            this.showNotification('Failed to load classes', 'error');
        }
    }

    async loadProperties() {
        try {
            const response = await fetch(`${this.baseUrl}/properties`);
            const data = await response.json();
            
            const propertiesList = document.getElementById('properties-list');
            propertiesList.innerHTML = '';
            
            data.properties.forEach(prop => {
                const propItem = document.createElement('div');
                propItem.className = 'property-item';
                propItem.innerHTML = `
                    <div class="property-header">
                        <h4>${prop.label || 'Unnamed Property'}</h4>
                        <span class="property-type">${prop.type}</span>
                    </div>
                    <div class="property-uri">${prop.uri}</div>
                    <div class="property-comment">${prop.comment || 'No description'}</div>
                    ${prop.domain ? `<div class="property-domain">Domain: ${prop.domain}</div>` : ''}
                    ${prop.range ? `<div class="property-range">Range: ${prop.range}</div>` : ''}
                `;
                propertiesList.appendChild(propItem);
            });
            
        } catch (error) {
            console.error('Failed to load properties:', error);
            this.showNotification('Failed to load properties', 'error');
        }
    }

    async loadInstances() {
        try {
            const classFilter = document.getElementById('instance-class-filter').value;
            const url = classFilter ? `${this.baseUrl}/instances?class_uri=${encodeURIComponent(classFilter)}` : `${this.baseUrl}/instances`;
            
            const response = await fetch(url);
            const data = await response.json();
            
            const instancesList = document.getElementById('instances-list');
            instancesList.innerHTML = '';
            
            data.instances.forEach(instance => {
                const instanceItem = document.createElement('div');
                instanceItem.className = 'instance-item';
                instanceItem.innerHTML = `
                    <div class="instance-header">
                        <h4>${instance.label || 'Unnamed Instance'}</h4>
                        <span class="instance-uri">${instance.uri}</span>
                    </div>
                    <div class="instance-comment">${instance.comment || 'No description'}</div>
                    ${instance.class ? `<div class="instance-class">Class: ${instance.class}</div>` : ''}
                `;
                instancesList.appendChild(instanceItem);
            });
            
        } catch (error) {
            console.error('Failed to load instances:', error);
            this.showNotification('Failed to load instances', 'error');
        }
    }

    showAddClassModal() {
        const modal = document.getElementById('add-class-modal');
        modal.style.display = 'block';
    }

    showAddPropertyModal() {
        const modal = document.getElementById('add-property-modal');
        modal.style.display = 'block';
    }

    showAddInstanceModal() {
        const modal = document.getElementById('add-instance-modal');
        modal.style.display = 'block';
    }

    async handleValidation() {
        const substanceData = {
            id: document.getElementById('substance-id').value,
            chemicalFormula: document.getElementById('chemical-formula').value,
            molecularWeight: parseFloat(document.getElementById('molecular-weight').value) || 0,
            flashPoint: document.getElementById('flash-point').value,
            boilingPoint: parseFloat(document.getElementById('boiling-point').value) || 0,
            meltingPoint: parseFloat(document.getElementById('melting-point').value) || 0,
            density: parseFloat(document.getElementById('density').value) || 0
        };

        try {
            const response = await fetch(`${this.baseUrl}/validate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(substanceData)
            });

            const result = await response.json();

            const validationResults = document.getElementById('validation-results');
            validationResults.innerHTML = '';

            if (result.valid) {
                validationResults.innerHTML = '<div class="validation-success">✓ Data is valid</div>';
            } else {
                const errorsList = document.createElement('div');
                errorsList.className = 'validation-errors';
                errorsList.innerHTML = '<h4>Validation Errors:</h4>';
                
                result.errors.forEach(error => {
                    const errorItem = document.createElement('div');
                    errorItem.className = 'validation-error';
                    errorItem.textContent = error.message || error;
                    errorsList.appendChild(errorItem);
                });
                
                validationResults.appendChild(errorsList);
            }

        } catch (error) {
            console.error('Validation failed:', error);
            this.showNotification('Failed to validate data', 'error');
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    // Close modal functions
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.style.display = 'none';
    }

    // Submit functions for modals
    async submitClass(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const classData = {
            uri: formData.get('uri'),
            label: formData.get('label'),
            comment: formData.get('comment'),
            superclass: formData.get('superclass') || null
        };

        try {
            const response = await fetch(`${this.baseUrl}/classes`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(classData)
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification(result.message, 'success');
                this.closeModal('add-class-modal');
                await this.loadClasses();
                event.target.reset();
            } else {
                this.showNotification(result.detail, 'error');
            }
        } catch (error) {
            console.error('Failed to add class:', error);
            this.showNotification('Failed to add class', 'error');
        }
    }

    async submitProperty(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const propertyData = {
            uri: formData.get('uri'),
            label: formData.get('label'),
            comment: formData.get('comment'),
            type: formData.get('type'),
            domain: formData.get('domain') || null,
            range: formData.get('range') || null
        };

        try {
            const response = await fetch(`${this.baseUrl}/properties`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(propertyData)
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification(result.message, 'success');
                this.closeModal('add-property-modal');
                await this.loadProperties();
                event.target.reset();
            } else {
                this.showNotification(result.detail, 'error');
            }
        } catch (error) {
            console.error('Failed to add property:', error);
            this.showNotification('Failed to add property', 'error');
        }
    }

    async submitInstance(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const instanceData = {
            uri: formData.get('uri'),
            label: formData.get('label'),
            comment: formData.get('comment'),
            class: formData.get('class'),
            properties: {}
        };

        // Add custom properties if any
        const customProps = formData.get('custom_properties');
        if (customProps) {
            try {
                instanceData.properties = JSON.parse(customProps);
            } catch (e) {
                // Ignore parsing errors
            }
        }

        try {
            const response = await fetch(`${this.baseUrl}/instances`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(instanceData)
            });

            const result = await response.json();

            if (response.ok) {
                this.showNotification(result.message, 'success');
                this.closeModal('add-instance-modal');
                await this.loadInstances();
                event.target.reset();
            } else {
                this.showNotification(result.detail, 'error');
            }
        } catch (error) {
            console.error('Failed to add instance:', error);
            this.showNotification('Failed to add instance', 'error');
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const ontologyManager = new OntologyManager();
    
    // Make it globally available
    window.ontologyManager = ontologyManager;
    
    // Load initial data
    ontologyManager.loadClasses();
    ontologyManager.loadProperties();
    ontologyManager.loadInstances();
}); 