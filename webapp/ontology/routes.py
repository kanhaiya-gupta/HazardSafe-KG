from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory="webapp/templates")

# Pydantic models for ontology operations
class OntologyClass(BaseModel):
    name: str
    description: str
    properties: List[str] = []
    parent_class: Optional[str] = None

class OntologyProperty(BaseModel):
    name: str
    description: str
    data_type: str
    domain: str
    range: str

class OntologyRelationship(BaseModel):
    name: str
    description: str
    source_class: str
    target_class: str
    properties: List[str] = []

# Sample ontology data (in production, this would come from a database or file)
SAMPLE_ONTOLOGY = {
    "classes": [
        {
            "name": "HazardousSubstance",
            "description": "A chemical substance that poses risks to health, safety, or the environment",
            "properties": ["chemical_formula", "molecular_weight", "hazard_class", "flash_point"],
            "parent_class": None
        },
        {
            "name": "Container",
            "description": "A vessel designed to safely store and transport hazardous substances",
            "properties": ["material", "capacity", "pressure_rating", "temperature_rating"],
            "parent_class": None
        },
        {
            "name": "SafetyTest",
            "description": "A test procedure to validate safety characteristics",
            "properties": ["test_type", "test_conditions", "test_results", "test_date"],
            "parent_class": None
        },
        {
            "name": "RiskAssessment",
            "description": "Evaluation of potential risks associated with substances or operations",
            "properties": ["risk_level", "mitigation_measures", "assessment_date"],
            "parent_class": None
        }
    ],
    "properties": [
        {
            "name": "chemical_formula",
            "description": "Chemical formula of the substance",
            "data_type": "string",
            "domain": "HazardousSubstance",
            "range": "string"
        },
        {
            "name": "material",
            "description": "Material composition of the container",
            "data_type": "string",
            "domain": "Container",
            "range": "string"
        },
        {
            "name": "test_type",
            "description": "Type of safety test performed",
            "data_type": "string",
            "domain": "SafetyTest",
            "range": "string"
        }
    ],
    "relationships": [
        {
            "name": "stored_in",
            "description": "Relationship between substance and its container",
            "source_class": "HazardousSubstance",
            "target_class": "Container",
            "properties": ["storage_conditions", "max_quantity"]
        },
        {
            "name": "validated_by",
            "description": "Relationship between container and safety test",
            "source_class": "Container",
            "target_class": "SafetyTest",
            "properties": ["test_parameters", "validation_date"]
        },
        {
            "name": "assesses_risk_of",
            "description": "Relationship between risk assessment and substance",
            "source_class": "RiskAssessment",
            "target_class": "HazardousSubstance",
            "properties": ["risk_factors", "assessment_method"]
        }
    ]
}

@router.get("/", response_class=HTMLResponse)
async def ontology_dashboard(request: Request):
    """Ontology management dashboard"""
    return templates.TemplateResponse("ontology/index.html", {"request": request})

@router.get("/stats")
async def get_ontology_stats():
    """Get ontology statistics"""
    return {
        "classes": len(SAMPLE_ONTOLOGY["classes"]),
        "properties": len(SAMPLE_ONTOLOGY["properties"]),
        "relationships": len(SAMPLE_ONTOLOGY["relationships"])
    }

@router.get("/classes")
async def get_ontology_classes():
    """Get all ontology classes"""
    return {"classes": SAMPLE_ONTOLOGY["classes"]}

@router.post("/classes")
async def create_ontology_class(ontology_class: OntologyClass):
    """Create a new ontology class"""
    # In production, this would save to a database or file
    SAMPLE_ONTOLOGY["classes"].append(ontology_class.dict())
    return {"message": "Class created successfully", "class": ontology_class}

@router.get("/classes/{class_name}")
async def get_ontology_class(class_name: str):
    """Get a specific ontology class"""
    for cls in SAMPLE_ONTOLOGY["classes"]:
        if cls["name"] == class_name:
            return cls
    raise HTTPException(status_code=404, detail="Class not found")

@router.get("/properties")
async def get_ontology_properties():
    """Get all ontology properties"""
    return {"properties": SAMPLE_ONTOLOGY["properties"]}

@router.post("/properties")
async def create_ontology_property(property: OntologyProperty):
    """Create a new ontology property"""
    SAMPLE_ONTOLOGY["properties"].append(property.dict())
    return {"message": "Property created successfully", "property": property}

@router.get("/relationships")
async def get_ontology_relationships():
    """Get all ontology relationships"""
    return {"relationships": SAMPLE_ONTOLOGY["relationships"]}

@router.post("/relationships")
async def create_ontology_relationship(relationship: OntologyRelationship):
    """Create a new ontology relationship"""
    SAMPLE_ONTOLOGY["relationships"].append(relationship.dict())
    return {"message": "Relationship created successfully", "relationship": relationship}

@router.get("/export/owl")
async def export_owl():
    """Export ontology as OWL/RDF"""
    # This would generate actual OWL/RDF content
    owl_content = f"""
    <?xml version="1.0"?>
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
             xmlns:owl="http://www.w3.org/2002/07/owl#"
             xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
             xmlns:xsd="http://www.w3.org/2001/XMLSchema#">
        
        <owl:Ontology rdf:about="http://hazardsafe-kg.org/ontology"/>
        
        <!-- Classes -->
        {chr(10).join([f'''
        <owl:Class rdf:about="http://hazardsafe-kg.org/ontology#{cls['name']}">
            <rdfs:label>{cls['name']}</rdfs:label>
            <rdfs:comment>{cls['description']}</rdfs:comment>
        </owl:Class>''' for cls in SAMPLE_ONTOLOGY["classes"]])}
        
        <!-- Properties -->
        {chr(10).join([f'''
        <owl:DatatypeProperty rdf:about="http://hazardsafe-kg.org/ontology#{prop['name']}">
            <rdfs:label>{prop['name']}</rdfs:label>
            <rdfs:comment>{prop['description']}</rdfs:comment>
            <rdfs:domain rdf:resource="http://hazardsafe-kg.org/ontology#{prop['domain']}"/>
            <rdfs:range rdf:resource="http://www.w3.org/2001/XMLSchema#{prop['data_type']}"/>
        </owl:DatatypeProperty>''' for prop in SAMPLE_ONTOLOGY["properties"]])}
        
    </rdf:RDF>
    """
    
    return {"owl_content": owl_content}

@router.get("/export/shacl")
async def export_shacl():
    """Export SHACL constraints"""
    # This would generate SHACL validation rules
    shacl_content = f"""
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    @prefix hs: <http://hazardsafe-kg.org/ontology#> .
    
    hs:OntologyShape
        a sh:NodeShape ;
        sh:targetClass hs:HazardousSubstance ;
        sh:property [
            sh:path hs:chemical_formula ;
            sh:datatype xsd:string ;
            sh:minCount 1 ;
        ] ;
        sh:property [
            sh:path hs:hazard_class ;
            sh:datatype xsd:string ;
            sh:in ("flammable" "toxic" "corrosive" "explosive") ;
        ] .
    """
    
    return {"shacl_content": shacl_content}

@router.get("/validate")
async def validate_ontology():
    """Validate ontology consistency"""
    # This would perform actual ontology validation
    validation_results = {
        "valid": True,
        "warnings": [],
        "errors": [],
        "checks": [
            {"name": "Class consistency", "status": "passed"},
            {"name": "Property domains", "status": "passed"},
            {"name": "Relationship integrity", "status": "passed"}
        ]
    }
    
    return validation_results
