from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import uuid
from datetime import datetime

router = APIRouter(prefix="/kg", tags=["kg"])
templates = Jinja2Templates(directory="webapp/templates")

# Pydantic models for KG operations
class KGQuery(BaseModel):
    query: str
    query_type: str = "cypher"  # cypher, gremlin, sparql
    limit: int = 100

class NodeData(BaseModel):
    labels: List[str]
    properties: Dict[str, Any]

class RelationshipData(BaseModel):
    start_node_id: str
    end_node_id: str
    relationship_type: str
    properties: Optional[Dict[str, Any]] = None

# Sample KG data (in production, this would come from Neo4j)
SAMPLE_NODES = [
    {
        "id": "node_001",
        "labels": ["HazardousSubstance"],
        "properties": {
            "name": "Sulfuric Acid",
            "chemical_formula": "H2SO4",
            "molecular_weight": 98.08,
            "hazard_class": "corrosive",
            "flash_point": "none",
            "boiling_point": 337
        }
    },
    {
        "id": "node_002",
        "labels": ["Container"],
        "properties": {
            "name": "Polyethylene Container",
            "material": "polyethylene",
            "capacity": 100,
            "pressure_rating": 2.0,
            "temperature_rating": 60
        }
    },
    {
        "id": "node_003",
        "labels": ["SafetyTest"],
        "properties": {
            "name": "Corrosion Resistance Test",
            "test_type": "corrosion",
            "duration": 24,
            "temperature": 25,
            "pressure": 1.0
        }
    },
    {
        "id": "node_004",
        "labels": ["RiskAssessment"],
        "properties": {
            "name": "Sulfuric Acid Storage Assessment",
            "risk_level": "medium",
            "assessment_date": "2024-01-15",
            "assessor": "Safety Team"
        }
    }
]

SAMPLE_RELATIONSHIPS = [
    {
        "id": "rel_001",
        "start_node_id": "node_001",
        "end_node_id": "node_002",
        "type": "STORED_IN",
        "properties": {
            "compatibility": "compatible",
            "max_concentration": 98
        }
    },
    {
        "id": "rel_002",
        "start_node_id": "node_001",
        "end_node_id": "node_003",
        "type": "TESTED_BY",
        "properties": {
            "test_result": "passed",
            "test_date": "2024-01-10"
        }
    },
    {
        "id": "rel_003",
        "start_node_id": "node_001",
        "end_node_id": "node_004",
        "type": "ASSESSED_BY",
        "properties": {
            "assessment_type": "storage_safety"
        }
    }
]

@router.get("/", response_class=HTMLResponse)
async def kg_dashboard(request: Request):
    """Knowledge Graph dashboard"""
    return templates.TemplateResponse("kg/index.html", {"request": request})

@router.get("/stats")
async def get_kg_stats():
    """Get knowledge graph statistics"""
    return {
        "nodes": len(SAMPLE_NODES),
        "relationships": len(SAMPLE_RELATIONSHIPS),
        "node_types": len(set([label for node in SAMPLE_NODES for label in node["labels"]])),
        "relationship_types": len(set([rel["type"] for rel in SAMPLE_RELATIONSHIPS]))
    }

@router.get("/nodes")
async def get_nodes(label: Optional[str] = None, limit: int = 100):
    """Get nodes from the knowledge graph"""
    nodes = SAMPLE_NODES
    
    if label:
        nodes = [node for node in nodes if label in node["labels"]]
    
    return {"nodes": nodes[:limit]}

@router.get("/relationships")
async def get_relationships(relationship_type: Optional[str] = None, limit: int = 100):
    """Get relationships from the knowledge graph"""
    relationships = SAMPLE_RELATIONSHIPS
    
    if relationship_type:
        relationships = [rel for rel in relationships if rel["type"] == relationship_type]
    
    return {"relationships": relationships[:limit]}

@router.post("/query")
async def query_kg(query: KGQuery):
    """Query the knowledge graph"""
    # In production, this would use Neo4j to execute Cypher queries
    
    # Sample query results
    if "MATCH" in query.query.upper():
        results = {
            "query_type": "match",
            "results": [
                {"node": SAMPLE_NODES[0]},
                {"node": SAMPLE_NODES[1]},
                {"relationship": SAMPLE_RELATIONSHIPS[0]}
            ],
            "count": 3
        }
    elif "CREATE" in query.query.upper():
        results = {
            "query_type": "create",
            "result": "Node/relationship created successfully"
        }
    else:
        results = {
            "query_type": "other",
            "results": "Query executed successfully"
        }
    
    return {
        "query": query.query,
        "query_type": query.query_type,
        "results": results,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/nodes")
async def create_node(node_data: NodeData):
    """Create a new node in the knowledge graph"""
    # In production, this would use Neo4j
    node_id = str(uuid.uuid4())
    
    new_node = {
        "id": node_id,
        "labels": node_data.labels,
        "properties": node_data.properties
    }
    
    SAMPLE_NODES.append(new_node)
    
    return {
        "message": "Node created successfully",
        "node_id": node_id,
        "node": new_node
    }

@router.post("/relationships")
async def create_relationship(relationship_data: RelationshipData):
    """Create a new relationship in the knowledge graph"""
    # In production, this would use Neo4j
    relationship_id = str(uuid.uuid4())
    
    new_relationship = {
        "id": relationship_id,
        "start_node_id": relationship_data.start_node_id,
        "end_node_id": relationship_data.end_node_id,
        "type": relationship_data.relationship_type,
        "properties": relationship_data.properties or {}
    }
    
    SAMPLE_RELATIONSHIPS.append(new_relationship)
    
    return {
        "message": "Relationship created successfully",
        "relationship_id": relationship_id,
        "relationship": new_relationship
    }

@router.get("/search")
async def search_kg(query: str, search_type: str = "nodes"):
    """Search the knowledge graph"""
    results = []
    query_lower = query.lower()
    
    if search_type == "nodes":
        for node in SAMPLE_NODES:
            if (query_lower in node["properties"].get("name", "").lower() or
                any(query_lower in str(value).lower() for value in node["properties"].values())):
                results.append(node)
    elif search_type == "relationships":
        for rel in SAMPLE_RELATIONSHIPS:
            if query_lower in rel["type"].lower():
                results.append(rel)
    
    return {"results": results}

@router.get("/path")
async def find_path(start_id: str, end_id: str, max_length: int = 5):
    """Find path between two nodes"""
    # In production, this would use Neo4j pathfinding algorithms
    
    # Sample path finding
    path = {
        "start_node": next((node for node in SAMPLE_NODES if node["id"] == start_id), None),
        "end_node": next((node for node in SAMPLE_NODES if node["id"] == end_id), None),
        "path": [
            {"node": SAMPLE_NODES[0]},
            {"relationship": SAMPLE_RELATIONSHIPS[0]},
            {"node": SAMPLE_NODES[1]}
        ],
        "length": 2
    }
    
    return {"path": path}

@router.get("/recommendations")
async def get_recommendations(node_id: str, relationship_type: Optional[str] = None):
    """Get recommendations based on node connections"""
    # In production, this would use graph algorithms for recommendations
    
    recommendations = {
        "node_id": node_id,
        "recommendations": [
            {
                "node": SAMPLE_NODES[1],
                "score": 0.85,
                "reason": "Frequently connected with similar substances"
            },
            {
                "node": SAMPLE_NODES[2],
                "score": 0.72,
                "reason": "Common testing protocol for this substance type"
            }
        ]
    }
    
    return recommendations

@router.get("/visualize")
async def get_visualization_data(limit: int = 50):
    """Get data for knowledge graph visualization"""
    # Prepare data for visualization (nodes and edges)
    nodes = []
    edges = []
    
    for node in SAMPLE_NODES[:limit]:
        nodes.append({
            "id": node["id"],
            "label": node["properties"].get("name", node["id"]),
            "type": node["labels"][0] if node["labels"] else "Unknown",
            "properties": node["properties"]
        })
    
    for rel in SAMPLE_RELATIONSHIPS[:limit]:
        edges.append({
            "id": rel["id"],
            "source": rel["start_node_id"],
            "target": rel["end_node_id"],
            "type": rel["type"],
            "properties": rel["properties"]
        })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "node_types": list(set([node["type"] for node in nodes])),
        "edge_types": list(set([edge["type"] for edge in edges]))
    }

@router.get("/export")
async def export_kg(format: str = "json"):
    """Export knowledge graph data"""
    # In production, this would export from Neo4j
    
    allowed_formats = ["json", "csv", "cypher"]
    if format not in allowed_formats:
        raise HTTPException(status_code=400, detail=f"Unsupported format. Allowed: {allowed_formats}")
    
    if format == "json":
        export_data = {
            "nodes": SAMPLE_NODES,
            "relationships": SAMPLE_RELATIONSHIPS,
            "export_date": datetime.now().isoformat()
        }
    elif format == "csv":
        export_data = {
            "nodes_csv": "id,labels,properties\n",
            "relationships_csv": "id,start_node,end_node,type,properties\n",
            "export_date": datetime.now().isoformat()
        }
    else:  # cypher
        export_data = {
            "cypher_script": "// Knowledge Graph Export\n",
            "export_date": datetime.now().isoformat()
        }
    
    return {
        "format": format,
        "data": export_data,
        "filename": f"knowledge_graph_export_{datetime.now().strftime('%Y%m%d')}.{format}"
    }

@router.delete("/nodes/{node_id}")
async def delete_node(node_id: str):
    """Delete a node from the knowledge graph"""
    node = next((node for node in SAMPLE_NODES if node["id"] == node_id), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # In production, this would delete from Neo4j
    SAMPLE_NODES.remove(node)
    
    # Also remove related relationships
    SAMPLE_RELATIONSHIPS[:] = [
        rel for rel in SAMPLE_RELATIONSHIPS 
        if rel["start_node_id"] != node_id and rel["end_node_id"] != node_id
    ]
    
    return {"message": "Node deleted successfully", "node_id": node_id}

@router.delete("/relationships/{relationship_id}")
async def delete_relationship(relationship_id: str):
    """Delete a relationship from the knowledge graph"""
    relationship = next((rel for rel in SAMPLE_RELATIONSHIPS if rel["id"] == relationship_id), None)
    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")
    
    # In production, this would delete from Neo4j
    SAMPLE_RELATIONSHIPS.remove(relationship)
    
    return {"message": "Relationship deleted successfully", "relationship_id": relationship_id}
