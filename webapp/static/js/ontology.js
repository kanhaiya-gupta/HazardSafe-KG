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