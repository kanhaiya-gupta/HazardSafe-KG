"""
Ontology management routes for HazardSafe-KG platform.
"""

from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import logging
import tempfile
import os
from ontology.src.manager import ontology_manager
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ontology", tags=["ontology"])
templates = Jinja2Templates(directory="webapp/templates")

# Pydantic models for ontology operations
class OntologyUpload(BaseModel):
    name: str
    description: str
    version: str = "1.0"
    format: str = "ttl"
    tags: List[str] = []

class OntologyQuery(BaseModel):
    query: str
    query_type: str = "sparql"  # sparql, owl, rdf
    limit: int = 100

class OntologyValidation(BaseModel):
    ontology_id: str
    validation_type: str = "shacl"  # shacl, owl, custom
    rules: Optional[Dict[str, Any]] = None

# Sample ontology data (in production, this would come from the ontology manager)
SAMPLE_ONTOLOGIES = [
    {
        "id": "onto_001",
        "name": "Hazardous Substances Ontology",
        "description": "Core ontology for hazardous substances and their properties",
        "version": "1.0",
        "format": "ttl",
        "file_path": "ontology/data/hazardous_substances.ttl",
        "upload_date": "2024-01-15",
        "tags": ["hazardous_substances", "chemical_safety", "core"],
        "classes": 25,
        "properties": 45,
        "instances": 150,
        "status": "active"
    },
    {
        "id": "onto_002",
        "name": "Container Safety Ontology",
        "description": "Ontology for container specifications and safety requirements",
        "version": "1.2",
        "format": "owl",
        "file_path": "ontology/data/container_safety.owl",
        "upload_date": "2024-01-10",
        "tags": ["containers", "safety", "storage"],
        "classes": 18,
        "properties": 32,
        "instances": 85,
        "status": "active"
    },
    {
        "id": "onto_003",
        "name": "Testing Protocols Ontology",
        "description": "Ontology for safety testing protocols and procedures",
        "version": "0.9",
        "format": "json-ld",
        "file_path": "ontology/data/testing_protocols.json-ld",
        "upload_date": "2024-01-12",
        "tags": ["testing", "protocols", "safety"],
        "classes": 12,
        "properties": 28,
        "instances": 45,
        "status": "draft"
    }
]

SAMPLE_VALIDATIONS = [
    {
        "id": "val_001",
        "ontology_id": "onto_001",
        "validation_type": "shacl",
        "status": "passed",
        "timestamp": "2024-01-20T10:30:00Z",
        "results": {
            "total_checks": 45,
            "passed": 43,
            "failed": 2,
            "warnings": 1
        },
        "details": [
            {
                "severity": "error",
                "message": "Missing required property 'hazard_class' for class 'HazardousSubstance'",
                "location": "line 45"
            },
            {
                "severity": "warning",
                "message": "Deprecated property 'old_property' used in class 'Container'",
                "location": "line 78"
            }
        ]
    }
]

@router.get("/", response_class=HTMLResponse)
async def ontology_dashboard(request: Request):
    """Ontology management dashboard"""
    return templates.TemplateResponse("ontology/index.html", {"request": request})

@router.get("/list")
async def list_ontologies():
    """List all ontologies"""
    return {"ontologies": SAMPLE_ONTOLOGIES}

@router.get("/stats")
async def get_ontology_stats():
    """Get ontology statistics"""
    return {
        "total_ontologies": len(SAMPLE_ONTOLOGIES),
        "total_validations": len(SAMPLE_VALIDATIONS),
        "formats_supported": 7,
        "active_ontologies": len([o for o in SAMPLE_ONTOLOGIES if o["status"] == "active"])
    }

@router.get("/classes")
async def get_ontology_classes():
    """Get ontology classes"""
    # Sample classes from the loaded ontologies
    classes = [
        {
            "uri": "http://hazardsafe-kg.org/ontology#HazardousSubstance",
            "label": "Hazardous Substance",
            "description": "A substance that poses a risk to health, safety, or the environment",
            "type": "owl:Class"
        },
        {
            "uri": "http://hazardsafe-kg.org/ontology#Container",
            "label": "Container",
            "description": "A vessel used for storing hazardous substances",
            "type": "owl:Class"
        },
        {
            "uri": "http://hazardsafe-kg.org/ontology#SafetyTest",
            "label": "Safety Test",
            "description": "A test performed to ensure safety compliance",
            "type": "owl:Class"
        },
        {
            "uri": "http://hazardsafe-kg.org/ontology#SafetyProcedure",
            "label": "Safety Procedure",
            "description": "A procedure for handling hazardous substances safely",
            "type": "owl:Class"
        }
    ]
    return {"classes": classes, "total_classes": len(classes)}

@router.get("/properties")
async def get_ontology_properties():
    """Get ontology properties"""
    # Sample properties from the loaded ontologies
    properties = [
        {
            "uri": "http://hazardsafe-kg.org/ontology#chemicalFormula",
            "label": "Chemical Formula",
            "description": "The molecular formula of a substance",
            "type": "owl:DatatypeProperty",
            "domain": "HazardousSubstance",
            "range": "xsd:string"
        },
        {
            "uri": "http://hazardsafe-kg.org/ontology#molecularWeight",
            "label": "Molecular Weight",
            "description": "The molecular weight of a substance",
            "type": "owl:DatatypeProperty",
            "domain": "HazardousSubstance",
            "range": "xsd:float"
        },
        {
            "uri": "http://hazardsafe-kg.org/ontology#hazardClass",
            "label": "Hazard Class",
            "description": "The classification of hazard for a substance",
            "type": "owl:DatatypeProperty",
            "domain": "HazardousSubstance",
            "range": "xsd:string"
        },
        {
            "uri": "http://hazardsafe-kg.org/ontology#containerMaterial",
            "label": "Container Material",
            "description": "The material used for the container",
            "type": "owl:DatatypeProperty",
            "domain": "Container",
            "range": "xsd:string"
        }
    ]
    return {"properties": properties, "total_properties": len(properties)}

@router.get("/relationships")
async def get_ontology_relationships():
    """Get ontology relationships"""
    # Sample relationships from the loaded ontologies
    relationships = [
        {
            "uri": "http://hazardsafe-kg.org/ontology#storedIn",
            "label": "Stored In",
            "description": "Relationship between a substance and its container",
            "type": "owl:ObjectProperty",
            "domain": "HazardousSubstance",
            "range": "Container"
        },
        {
            "uri": "http://hazardsafe-kg.org/ontology#testedBy",
            "label": "Tested By",
            "description": "Relationship between a substance and its safety test",
            "type": "owl:ObjectProperty",
            "domain": "HazardousSubstance",
            "range": "SafetyTest"
        },
        {
            "uri": "http://hazardsafe-kg.org/ontology#requiresProcedure",
            "label": "Requires Procedure",
            "description": "Relationship between a substance and its safety procedure",
            "type": "owl:ObjectProperty",
            "domain": "HazardousSubstance",
            "range": "SafetyProcedure"
        }
    ]
    return {"relationships": relationships, "total_relationships": len(relationships)}

@router.get("/instances")
async def get_ontology_instances(class_uri: Optional[str] = None):
    """Get ontology instances"""
    # Sample instances from the loaded ontologies
    instances = [
        {
            "uri": "http://hazardsafe-kg.org/ontology#SulfuricAcid",
            "label": "Sulfuric Acid",
            "class": "HazardousSubstance",
            "properties": {
                "chemicalFormula": "H2SO4",
                "molecularWeight": 98.08,
                "hazardClass": "corrosive"
            }
        },
        {
            "uri": "http://hazardsafe-kg.org/ontology#PolyethyleneContainer",
            "label": "Polyethylene Container",
            "class": "Container",
            "properties": {
                "containerMaterial": "polyethylene",
                "capacity": 100,
                "pressureRating": 2.0
            }
        },
        {
            "uri": "http://hazardsafe-kg.org/ontology#CorrosionTest",
            "label": "Corrosion Resistance Test",
            "class": "SafetyTest",
            "properties": {
                "testType": "corrosion",
                "duration": 24,
                "temperature": 25
            }
        }
    ]
    
    if class_uri:
        instances = [i for i in instances if i["class"] in class_uri]
    
    return {"instances": instances, "total_instances": len(instances)}

@router.get("/formats")
async def get_supported_formats():
    """Get list of supported ontology formats"""
    return {
        "formats": [
            {"name": "Turtle", "extension": "ttl", "description": "Terse RDF Triple Language"},
            {"name": "OWL/XML", "extension": "owl", "description": "Web Ontology Language XML"},
            {"name": "RDF/XML", "extension": "rdf", "description": "Resource Description Framework XML"},
            {"name": "JSON-LD", "extension": "json-ld", "description": "JSON for Linked Data"},
            {"name": "N-Triples", "extension": "nt", "description": "Simple line-based RDF format"},
            {"name": "Notation3", "extension": "n3", "description": "Compact RDF notation"},
            {"name": "TriG", "extension": "trig", "description": "Terse RDF Triple Language for Named Graphs"}
        ]
    }

@router.get("/validations")
async def get_validation_history(ontology_id: Optional[str] = None):
    """Get validation history"""
    validations = SAMPLE_VALIDATIONS
    
    if ontology_id:
        validations = [v for v in validations if v["ontology_id"] == ontology_id]
    
    return {"validations": validations}

@router.get("/validate")
async def get_validation_status():
    """Get current validation status"""
    # Return the most recent validation result or perform a quick validation
    if SAMPLE_VALIDATIONS:
        latest_validation = SAMPLE_VALIDATIONS[-1]
        return {
            "valid": latest_validation["status"] == "passed",
            "status": latest_validation["status"],
            "timestamp": latest_validation["timestamp"],
            "results": latest_validation["results"],
            "details": latest_validation["details"]
        }
    else:
        # No validation history, return default status
        return {
            "valid": True,
            "status": "not_validated",
            "timestamp": datetime.now().isoformat(),
            "results": {
                "total_checks": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            },
            "details": []
        }

@router.get("/{ontology_id}")
async def get_ontology(ontology_id: str):
    """Get specific ontology details"""
    ontology = next((o for o in SAMPLE_ONTOLOGIES if o["id"] == ontology_id), None)
    if not ontology:
        raise HTTPException(status_code=404, detail="Ontology not found")
    
    return {"ontology": ontology}

@router.post("/upload")
async def upload_ontology(
    name: str = Form(...),
    description: str = Form(...),
    version: str = Form("1.0"),
    format: str = Form("ttl"),
    tags: str = Form(""),
    file: UploadFile = File(...)
):
    """Upload a new ontology"""
    # In production, this would use the ontology manager
    ontology_id = str(uuid.uuid4())
    
    # Parse tags
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    # Validate file format
    allowed_formats = ["ttl", "owl", "rdf", "json-ld", "nt", "n3", "trig"]
    if format not in allowed_formats:
        raise HTTPException(status_code=400, detail=f"Unsupported format. Allowed: {allowed_formats}")
    
    new_ontology = {
        "id": ontology_id,
        "name": name,
        "description": description,
        "version": version,
        "format": format,
        "file_path": f"ontology/data/{file.filename}",
        "upload_date": datetime.now().strftime("%Y-%m-%d"),
        "tags": tag_list,
        "classes": 0,  # Would be calculated from actual ontology
        "properties": 0,
        "instances": 0,
        "status": "active"
    }
    
    # In production, save file and process ontology
    SAMPLE_ONTOLOGIES.append(new_ontology)
    
    return {
        "message": "Ontology uploaded successfully",
        "ontology_id": ontology_id,
        "ontology": new_ontology
    }

@router.post("/query")
async def query_ontology(query: OntologyQuery):
    """Query ontology using SPARQL or other query languages"""
    # In production, this would use the ontology manager to execute queries
    
    # Sample SPARQL query results
    if "SELECT" in query.query.upper():
        results = {
            "query_type": "select",
            "results": [
                {"subject": "http://example.org/HazardousSubstance", "predicate": "rdf:type", "object": "owl:Class"},
                {"subject": "http://example.org/Container", "predicate": "rdf:type", "object": "owl:Class"}
            ],
            "count": 2
        }
    elif "ASK" in query.query.upper():
        results = {
            "query_type": "ask",
            "result": True
        }
    else:
        results = {
            "query_type": "construct",
            "results": "Graph constructed successfully"
        }
    
    return {
        "query": query.query,
        "query_type": query.query_type,
        "results": results,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/validate")
async def validate_ontology(validation: OntologyValidation):
    """Validate ontology using SHACL or other validation methods"""
    # In production, this would use the ontology manager for validation
    
    validation_id = str(uuid.uuid4())
    
    # Sample validation results
    validation_result = {
        "id": validation_id,
        "ontology_id": validation.ontology_id,
        "validation_type": validation.validation_type,
        "status": "passed",
        "timestamp": datetime.now().isoformat(),
        "results": {
            "total_checks": 50,
            "passed": 48,
            "failed": 2,
            "warnings": 1
        },
        "details": [
            {
                "severity": "error",
                "message": "Missing required property 'hazard_class'",
                "location": "line 45"
            },
            {
                "severity": "warning",
                "message": "Deprecated property used",
                "location": "line 78"
            }
        ]
    }
    
    SAMPLE_VALIDATIONS.append(validation_result)
    
    return validation_result

@router.get("/{ontology_id}/export")
async def export_ontology(ontology_id: str, format: str = "ttl"):
    """Export ontology in specified format"""
    ontology = next((o for o in SAMPLE_ONTOLOGIES if o["id"] == ontology_id), None)
    if not ontology:
        raise HTTPException(status_code=404, detail="Ontology not found")
    
    # In production, this would use the ontology manager to convert formats
    allowed_formats = ["ttl", "owl", "rdf", "json-ld", "nt", "n3", "trig"]
    if format not in allowed_formats:
        raise HTTPException(status_code=400, detail=f"Unsupported export format. Allowed: {allowed_formats}")
    
    # Sample export content
    export_content = f"""# Exported ontology: {ontology['name']}
# Format: {format}
# Version: {ontology['version']}

# Sample ontology content in {format} format
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<http://example.org/HazardousSubstance> rdf:type owl:Class .
<http://example.org/Container> rdf:type owl:Class .
"""
    
    return {
        "ontology_id": ontology_id,
        "format": format,
        "content": export_content,
        "filename": f"{ontology['name'].replace(' ', '_')}.{format}"
    }

@router.get("/{ontology_id}/visualize")
async def visualize_ontology(ontology_id: str):
    """Get ontology visualization data"""
    ontology = next((o for o in SAMPLE_ONTOLOGIES if o["id"] == ontology_id), None)
    if not ontology:
        raise HTTPException(status_code=404, detail="Ontology not found")
    
    # Sample visualization data
    visualization_data = {
        "nodes": [
            {"id": "HazardousSubstance", "type": "class", "label": "Hazardous Substance"},
            {"id": "Container", "type": "class", "label": "Container"},
            {"id": "SafetyTest", "type": "class", "label": "Safety Test"},
            {"id": "hazard_class", "type": "property", "label": "Hazard Class"},
            {"id": "material", "type": "property", "label": "Material"}
        ],
        "edges": [
            {"source": "HazardousSubstance", "target": "hazard_class", "type": "property"},
            {"source": "Container", "target": "material", "type": "property"},
            {"source": "HazardousSubstance", "target": "SafetyTest", "type": "relationship"}
        ]
    }
    
    return {
        "ontology_id": ontology_id,
        "visualization": visualization_data
    }

@router.delete("/{ontology_id}")
async def delete_ontology(ontology_id: str):
    """Delete an ontology"""
    ontology = next((o for o in SAMPLE_ONTOLOGIES if o["id"] == ontology_id), None)
    if not ontology:
        raise HTTPException(status_code=404, detail="Ontology not found")
    
    # In production, this would remove from storage
    SAMPLE_ONTOLOGIES.remove(ontology)
    
    return {"message": "Ontology deleted successfully", "ontology_id": ontology_id}
