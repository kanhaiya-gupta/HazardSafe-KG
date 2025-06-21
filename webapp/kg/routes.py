from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory="webapp/templates")

# Pydantic models for KG operations
class KGQuery(BaseModel):
    query: str
    query_type: str = "cypher"  # cypher, sparql, natural
    limit: int = 100

class KGNode(BaseModel):
    id: str
    labels: List[str]
    properties: Dict[str, Any]

class KGRelationship(BaseModel):
    id: str
    type: str
    start_node: str
    end_node: str
    properties: Dict[str, Any]

# Sample knowledge graph data (in production, this would come from Neo4j)
SAMPLE_KG_DATA = {
    "nodes": [
        {
            "id": "substance_001",
            "labels": ["HazardousSubstance"],
            "properties": {
                "name": "Sulfuric Acid",
                "chemical_formula": "H2SO4",
                "molecular_weight": 98.08,
                "hazard_class": "corrosive",
                "flash_point": "none"
            }
        },
        {
            "id": "container_001",
            "labels": ["Container"],
            "properties": {
                "name": "Polyethylene Tank",
                "material": "polyethylene",
                "capacity": 1000,
                "pressure_rating": 2.0,
                "temperature_rating": 60
            }
        },
        {
            "id": "test_001",
            "labels": ["SafetyTest"],
            "properties": {
                "name": "Corrosion Resistance Test",
                "test_type": "corrosion",
                "test_conditions": "25°C, 24h exposure",
                "test_results": "passed",
                "test_date": "2024-01-15"
            }
        },
        {
            "id": "risk_001",
            "labels": ["RiskAssessment"],
            "properties": {
                "name": "Storage Risk Assessment",
                "risk_level": "medium",
                "mitigation_measures": "ventilation, PPE",
                "assessment_date": "2024-01-10"
            }
        }
    ],
    "relationships": [
        {
            "id": "rel_001",
            "type": "STORED_IN",
            "start_node": "substance_001",
            "end_node": "container_001",
            "properties": {
                "storage_conditions": "ambient temperature",
                "max_quantity": 500
            }
        },
        {
            "id": "rel_002",
            "type": "VALIDATED_BY",
            "start_node": "container_001",
            "end_node": "test_001",
            "properties": {
                "test_parameters": "corrosion resistance",
                "validation_date": "2024-01-15"
            }
        },
        {
            "id": "rel_003",
            "type": "ASSESSES_RISK_OF",
            "start_node": "risk_001",
            "end_node": "substance_001",
            "properties": {
                "risk_factors": "corrosivity, toxicity",
                "assessment_method": "hazard analysis"
            }
        }
    ]
}

@router.get("/", response_class=HTMLResponse)
async def kg_dashboard(request: Request):
    """Knowledge Graph dashboard"""
    return templates.TemplateResponse("kg/index.html", {"request": request})

@router.get("/stats")
async def get_kg_stats():
    """Get knowledge graph statistics"""
    return {
        "nodes": len(SAMPLE_KG_DATA["nodes"]),
        "relationships": len(SAMPLE_KG_DATA["relationships"]),
        "node_types": len(set([node["labels"][0] for node in SAMPLE_KG_DATA["nodes"]])),
        "relationship_types": len(set([rel["type"] for rel in SAMPLE_KG_DATA["relationships"]]))
    }

@router.get("/nodes")
async def get_kg_nodes(node_type: Optional[str] = None, limit: int = 100):
    """Get knowledge graph nodes"""
    nodes = SAMPLE_KG_DATA["nodes"]
    if node_type:
        nodes = [node for node in nodes if node_type in node["labels"]]
    
    return {"nodes": nodes[:limit]}

@router.get("/relationships")
async def get_kg_relationships(relationship_type: Optional[str] = None, limit: int = 100):
    """Get knowledge graph relationships"""
    relationships = SAMPLE_KG_DATA["relationships"]
    if relationship_type:
        relationships = [rel for rel in relationships if rel["type"] == relationship_type]
    
    return {"relationships": relationships[:limit]}

@router.post("/query")
async def query_kg(query: KGQuery):
    """Query the knowledge graph"""
    # In production, this would execute actual Cypher/SPARQL queries
    if query.query_type == "cypher":
        return execute_cypher_query(query.query, query.limit)
    elif query.query_type == "sparql":
        return execute_sparql_query(query.query, query.limit)
    else:
        return execute_natural_query(query.query, query.limit)

@router.get("/visualize")
async def get_kg_visualization_data():
    """Get data for knowledge graph visualization"""
    return {
        "nodes": SAMPLE_KG_DATA["nodes"],
        "relationships": SAMPLE_KG_DATA["relationships"]
    }

@router.get("/node/{node_id}")
async def get_kg_node(node_id: str):
    """Get a specific knowledge graph node"""
    for node in SAMPLE_KG_DATA["nodes"]:
        if node["id"] == node_id:
            return node
    raise HTTPException(status_code=404, detail="Node not found")

@router.get("/search")
async def search_kg_nodes(query: str, node_type: Optional[str] = None):
    """Search for nodes in the knowledge graph"""
    results = []
    for node in SAMPLE_KG_DATA["nodes"]:
        if node_type and node_type not in node["labels"]:
            continue
        
        # Simple text search in properties
        for key, value in node["properties"].items():
            if query.lower() in str(value).lower():
                results.append(node)
                break
    
    return {"results": results}

@router.get("/path")
async def find_path(start_node: str, end_node: str, max_depth: int = 3):
    """Find path between two nodes"""
    # Simple path finding implementation
    paths = find_paths_between_nodes(start_node, end_node, max_depth)
    return {"paths": paths}

@router.get("/recommendations")
async def get_recommendations(node_id: str, recommendation_type: str = "similar"):
    """Get recommendations based on a node"""
    # Simple recommendation logic
    recommendations = generate_recommendations(node_id, recommendation_type)
    return {"recommendations": recommendations}

# Helper functions for query execution
def execute_cypher_query(query: str, limit: int):
    """Execute Cypher query (simplified implementation)"""
    # In production, this would connect to Neo4j
    if "MATCH" in query.upper():
        if "HazardousSubstance" in query:
            substances = [node for node in SAMPLE_KG_DATA["nodes"] if "HazardousSubstance" in node["labels"]]
            return {"results": substances[:limit]}
        elif "Container" in query:
            containers = [node for node in SAMPLE_KG_DATA["nodes"] if "Container" in node["labels"]]
            return {"results": containers[:limit]}
        else:
            return {"results": SAMPLE_KG_DATA["nodes"][:limit]}
    else:
        return {"results": [], "error": "Invalid Cypher query"}

def execute_sparql_query(query: str, limit: int):
    """Execute SPARQL query (simplified implementation)"""
    # In production, this would connect to a SPARQL endpoint
    return {"results": [], "message": "SPARQL queries not yet implemented"}

def execute_natural_query(query: str, limit: int):
    """Execute natural language query (simplified implementation)"""
    # Simple keyword-based search
    results = []
    query_lower = query.lower()
    
    for node in SAMPLE_KG_DATA["nodes"]:
        for key, value in node["properties"].items():
            if query_lower in str(value).lower():
                results.append(node)
                break
    
    return {"results": results[:limit]}

def find_paths_between_nodes(start_node: str, end_node: str, max_depth: int):
    """Find paths between two nodes (simplified implementation)"""
    # Simple path finding - in production, use graph algorithms
    paths = []
    
    # Find direct relationships
    for rel in SAMPLE_KG_DATA["relationships"]:
        if rel["start_node"] == start_node and rel["end_node"] == end_node:
            paths.append([start_node, end_node])
        elif rel["start_node"] == end_node and rel["end_node"] == start_node:
            paths.append([start_node, end_node])
    
    return paths

def generate_recommendations(node_id: str, recommendation_type: str):
    """Generate recommendations (simplified implementation)"""
    recommendations = []
    
    # Find similar nodes based on labels
    target_node = None
    for node in SAMPLE_KG_DATA["nodes"]:
        if node["id"] == node_id:
            target_node = node
            break
    
    if target_node:
        for node in SAMPLE_KG_DATA["nodes"]:
            if node["id"] != node_id and node["labels"] == target_node["labels"]:
                recommendations.append(node)
    
    return recommendations[:5]  # Return top 5 recommendations
