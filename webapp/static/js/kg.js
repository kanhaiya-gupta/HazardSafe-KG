// Knowledge Graph JavaScript

let graphData = {
    nodes: [],
    relationships: []
};

let simulation;
let selectedNode = null;

document.addEventListener('DOMContentLoaded', function() {
    loadKGData();
    initializeGraph();
});

async function loadKGData() {
    try {
        const [statsResponse, visualizationResponse] = await Promise.all([
            fetch('/kg/stats'),
            fetch('/kg/visualize')
        ]);

        const statsData = await statsResponse.json();
        const visualizationData = await visualizationResponse.json();

        graphData = visualizationData;
        
        // Update statistics
        updateStatistics(statsData);
        
        // Render initial graph
        renderGraph();

    } catch (error) {
        console.error('Error loading KG data:', error);
        HazardSafeKG.showNotification('Error loading knowledge graph data', 'error');
    }
}

function updateStatistics(stats) {
    document.getElementById('node-count').textContent = stats.nodes || 0;
    document.getElementById('relationship-count').textContent = stats.relationships || 0;
    document.getElementById('node-types').textContent = stats.node_types || 0;
    document.getElementById('relationship-types').textContent = stats.relationship_types || 0;
}

function initializeGraph() {
    const container = document.getElementById('graph-container');
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Create SVG
    const svg = d3.select('#graph-container')
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    // Add zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {
            svg.select('g').attr('transform', event.transform);
        });

    svg.call(zoom);

    // Create main group for graph elements
    svg.append('g').attr('id', 'graph-group');
}

function renderGraph() {
    const container = document.getElementById('graph-container');
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Clear existing graph
    d3.select('#graph-group').selectAll('*').remove();

    // Create force simulation
    simulation = d3.forceSimulation(graphData.nodes)
        .force('link', d3.forceLink(graphData.relationships).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(30));

    // Create links
    const links = d3.select('#graph-group')
        .selectAll('.link')
        .data(graphData.relationships)
        .enter()
        .append('line')
        .attr('class', 'link')
        .style('stroke', '#999')
        .style('stroke-width', 2)
        .style('stroke-opacity', 0.6);

    // Create link labels
    const linkLabels = d3.select('#graph-group')
        .selectAll('.link-label')
        .data(graphData.relationships)
        .enter()
        .append('text')
        .attr('class', 'link-label')
        .text(d => d.type)
        .style('font-size', '10px')
        .style('fill', '#666')
        .style('text-anchor', 'middle');

    // Create nodes
    const nodes = d3.select('#graph-group')
        .selectAll('.node')
        .data(graphData.nodes)
        .enter()
        .append('g')
        .attr('class', 'node')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));

    // Add circles to nodes
    nodes.append('circle')
        .attr('r', 20)
        .style('fill', d => getNodeColor(d.labels[0]))
        .style('stroke', '#fff')
        .style('stroke-width', 2)
        .style('cursor', 'pointer')
        .on('click', function(event, d) {
            showNodeDetails(d);
        });

    // Add node labels
    nodes.append('text')
        .text(d => d.properties.name || d.id)
        .style('font-size', '12px')
        .style('text-anchor', 'middle')
        .style('pointer-events', 'none')
        .style('fill', '#fff')
        .style('font-weight', 'bold');

    // Update positions on simulation tick
    simulation.on('tick', () => {
        links
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        linkLabels
            .attr('x', d => (d.source.x + d.target.x) / 2)
            .attr('y', d => (d.source.y + d.target.y) / 2);

        nodes
            .attr('transform', d => `translate(${d.x},${d.y})`);
    });
}

function getNodeColor(nodeType) {
    const colors = {
        'HazardousSubstance': '#e74c3c',
        'Container': '#3498db',
        'SafetyTest': '#2ecc71',
        'RiskAssessment': '#f39c12'
    };
    return colors[nodeType] || '#95a5a6';
}

function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

async function executeQuery() {
    const queryType = document.getElementById('queryType').value;
    const query = document.getElementById('queryInput').value;
    const limit = parseInt(document.getElementById('queryLimit').value);

    if (!query.trim()) {
        HazardSafeKG.showNotification('Please enter a query', 'warning');
        return;
    }

    try {
        const response = await fetch('/kg/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                query_type: queryType,
                limit: limit
            })
        });

        const result = await response.json();
        displayQueryResults(result);

    } catch (error) {
        console.error('Error executing query:', error);
        HazardSafeKG.showNotification('Error executing query', 'error');
    }
}

function loadQuickQuery(query) {
    document.getElementById('queryInput').value = query;
    document.getElementById('queryType').value = 'cypher';
}

async function searchNodes() {
    const query = document.getElementById('searchQuery').value;
    const nodeType = document.getElementById('searchNodeType').value;

    if (!query.trim()) {
        HazardSafeKG.showNotification('Please enter a search term', 'warning');
        return;
    }

    try {
        const params = new URLSearchParams({ query: query });
        if (nodeType) params.append('node_type', nodeType);

        const response = await fetch(`/kg/search?${params}`);
        const result = await response.json();
        
        displayQueryResults({ results: result.results });

    } catch (error) {
        console.error('Error searching nodes:', error);
        HazardSafeKG.showNotification('Error searching nodes', 'error');
    }
}

async function findPath() {
    const startNode = document.getElementById('startNode').value;
    const endNode = document.getElementById('endNode').value;
    const maxDepth = parseInt(document.getElementById('maxDepth').value);

    if (!startNode || !endNode) {
        HazardSafeKG.showNotification('Please enter both start and end node IDs', 'warning');
        return;
    }

    try {
        const params = new URLSearchParams({
            start_node: startNode,
            end_node: endNode,
            max_depth: maxDepth
        });

        const response = await fetch(`/kg/path?${params}`);
        const result = await response.json();
        
        displayQueryResults({ paths: result.paths });

    } catch (error) {
        console.error('Error finding path:', error);
        HazardSafeKG.showNotification('Error finding path', 'error');
    }
}

function displayQueryResults(result) {
    const resultsContainer = document.getElementById('query-results');
    
    if (result.error) {
        resultsContainer.innerHTML = `<div class="alert alert-danger">${result.error}</div>`;
        return;
    }

    if (result.message) {
        resultsContainer.innerHTML = `<div class="alert alert-info">${result.message}</div>`;
        return;
    }

    let html = '';
    
    if (result.results && result.results.length > 0) {
        html += '<div class="table-responsive"><table class="table table-hover">';
        html += '<thead><tr><th>Type</th><th>Name</th><th>Properties</th><th>Actions</th></tr></thead><tbody>';
        
        result.results.forEach(item => {
            const nodeType = item.labels ? item.labels[0] : 'Unknown';
            const name = item.properties ? item.properties.name || item.id : item.id;
            const properties = item.properties ? Object.entries(item.properties).map(([k, v]) => `${k}: ${v}`).join(', ') : '';
            
            html += `
                <tr>
                    <td><span class="badge bg-secondary">${nodeType}</span></td>
                    <td><strong>${name}</strong></td>
                    <td><small>${properties}</small></td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="showNodeDetails('${item.id}')">
                            <i class="fas fa-eye"></i> View
                        </button>
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table></div>';
    } else if (result.paths && result.paths.length > 0) {
        html += '<h6>Found Paths:</h6>';
        result.paths.forEach((path, index) => {
            html += `<div class="alert alert-info">Path ${index + 1}: ${path.join(' → ')}</div>`;
        });
    } else {
        html = '<p class="text-muted">No results found.</p>';
    }
    
    resultsContainer.innerHTML = html;
}

async function showNodeDetails(nodeId) {
    try {
        let node;
        if (typeof nodeId === 'string') {
            // Fetch node details by ID
            const response = await fetch(`/kg/node/${nodeId}`);
            node = await response.json();
        } else {
            // Use provided node object
            node = nodeId;
        }

        const modal = new bootstrap.Modal(document.getElementById('nodeDetailsModal'));
        const content = document.getElementById('nodeDetailsContent');
        
        let html = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Node Information</h6>
                    <table class="table table-sm">
                        <tr><td><strong>ID:</strong></td><td>${node.id}</td></tr>
                        <tr><td><strong>Type:</strong></td><td><span class="badge bg-secondary">${node.labels.join(', ')}</span></td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>Properties</h6>
                    <table class="table table-sm">
        `;
        
        for (const [key, value] of Object.entries(node.properties)) {
            html += `<tr><td><strong>${key}:</strong></td><td>${value}</td></tr>`;
        }
        
        html += `
                    </table>
                </div>
            </div>
        `;
        
        content.innerHTML = html;
        modal.show();
        
        // Store selected node for recommendations
        selectedNode = node;

    } catch (error) {
        console.error('Error showing node details:', error);
        HazardSafeKG.showNotification('Error loading node details', 'error');
    }
}

async function getRecommendations() {
    if (!selectedNode) {
        HazardSafeKG.showNotification('No node selected', 'warning');
        return;
    }

    try {
        const response = await fetch(`/kg/recommendations?node_id=${selectedNode.id}`);
        const result = await response.json();
        
        if (result.recommendations && result.recommendations.length > 0) {
            let html = '<h6>Recommendations:</h6><div class="table-responsive"><table class="table table-sm">';
            html += '<thead><tr><th>Type</th><th>Name</th><th>Properties</th></tr></thead><tbody>';
            
            result.recommendations.forEach(item => {
                const nodeType = item.labels ? item.labels[0] : 'Unknown';
                const name = item.properties ? item.properties.name || item.id : item.id;
                const properties = item.properties ? Object.entries(item.properties).slice(0, 3).map(([k, v]) => `${k}: ${v}`).join(', ') : '';
                
                html += `
                    <tr>
                        <td><span class="badge bg-secondary">${nodeType}</span></td>
                        <td><strong>${name}</strong></td>
                        <td><small>${properties}</small></td>
                    </tr>
                `;
            });
            
            html += '</tbody></table></div>';
            
            const content = document.getElementById('nodeDetailsContent');
            content.innerHTML += html;
        } else {
            HazardSafeKG.showNotification('No recommendations found', 'info');
        }

    } catch (error) {
        console.error('Error getting recommendations:', error);
        HazardSafeKG.showNotification('Error getting recommendations', 'error');
    }
}

function resetView() {
    if (simulation) {
        simulation.alpha(1).restart();
    }
}

function exportGraph() {
    // Export graph data as JSON
    const dataStr = JSON.stringify(graphData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'knowledge-graph-export.json';
    a.click();
    window.URL.revokeObjectURL(url);
    
    HazardSafeKG.showNotification('Graph exported successfully', 'success');
}

// Handle window resize
window.addEventListener('resize', () => {
    const container = document.getElementById('graph-container');
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    d3.select('#graph-container svg')
        .attr('width', width)
        .attr('height', height);
    
    if (simulation) {
        simulation.force('center', d3.forceCenter(width / 2, height / 2));
        simulation.alpha(1).restart();
    }
}); 