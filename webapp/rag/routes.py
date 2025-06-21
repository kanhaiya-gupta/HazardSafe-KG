from fastapi import APIRouter, Request, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import uuid
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="webapp/templates")

# Pydantic models for RAG operations
class RAGQuery(BaseModel):
    question: str
    context_type: str = "all"  # all, safety, technical, regulatory
    max_results: int = 5
    include_sources: bool = True

class DocumentUpload(BaseModel):
    title: str
    description: str
    document_type: str
    tags: List[str] = []

class SafetyValidation(BaseModel):
    substance_name: str
    container_type: str
    test_conditions: Dict[str, Any]
    validation_criteria: List[str]

# Sample RAG data (in production, this would come from a vector database)
SAMPLE_DOCUMENTS = [
    {
        "id": "doc_001",
        "title": "Sulfuric Acid Safety Data Sheet",
        "description": "Comprehensive safety information for sulfuric acid handling and storage",
        "content": "Sulfuric acid (H2SO4) is a highly corrosive substance that requires special handling. It should be stored in polyethylene containers rated for corrosive chemicals. The flash point is none, and it has a molecular weight of 98.08 g/mol. Safety measures include proper ventilation, PPE, and spill containment procedures.",
        "document_type": "safety_data_sheet",
        "tags": ["sulfuric_acid", "corrosive", "chemical_safety"],
        "upload_date": "2024-01-15",
        "file_path": "/documents/sulfuric_acid_sds.pdf"
    },
    {
        "id": "doc_002",
        "title": "Polyethylene Container Specifications",
        "description": "Technical specifications for polyethylene storage containers",
        "content": "Polyethylene containers are suitable for storing corrosive chemicals including sulfuric acid. These containers have a pressure rating of 2.0 bar and temperature rating of 60°C. The material is resistant to most acids and bases, making it ideal for chemical storage applications.",
        "document_type": "technical_specification",
        "tags": ["polyethylene", "container", "storage"],
        "upload_date": "2024-01-10",
        "file_path": "/documents/polyethylene_specs.pdf"
    },
    {
        "id": "doc_003",
        "title": "Corrosion Resistance Testing Protocol",
        "description": "Standard testing procedures for container corrosion resistance",
        "content": "Corrosion resistance testing involves exposing container materials to the target chemical for 24 hours at 25°C. The test evaluates material integrity, weight loss, and visual changes. A container passes if it shows no significant degradation or weight loss exceeding 1%.",
        "document_type": "test_protocol",
        "tags": ["corrosion_testing", "safety_validation", "container_testing"],
        "upload_date": "2024-01-12",
        "file_path": "/documents/corrosion_test_protocol.pdf"
    },
    {
        "id": "doc_004",
        "title": "Chemical Storage Regulations",
        "description": "Regulatory requirements for hazardous chemical storage",
        "content": "Hazardous chemicals must be stored in approved containers that have been tested and validated for the specific chemical. Storage areas must have proper ventilation, spill containment, and emergency response equipment. Regular inspections and safety audits are required.",
        "document_type": "regulatory",
        "tags": ["regulations", "compliance", "chemical_storage"],
        "upload_date": "2024-01-08",
        "file_path": "/documents/storage_regulations.pdf"
    }
]

SAMPLE_QUERIES = [
    {
        "id": "query_001",
        "question": "What containers are suitable for storing sulfuric acid?",
        "answer": "Polyethylene containers are suitable for storing sulfuric acid. These containers have a pressure rating of 2.0 bar and temperature rating of 60°C. The material is resistant to most acids and bases, making it ideal for chemical storage applications.",
        "sources": ["doc_002", "doc_001"],
        "confidence": 0.95,
        "timestamp": "2024-01-20T10:30:00Z"
    },
    {
        "id": "query_002",
        "question": "What safety measures are required for sulfuric acid storage?",
        "answer": "Safety measures for sulfuric acid storage include proper ventilation, PPE (personal protective equipment), and spill containment procedures. Storage areas must have proper ventilation, spill containment, and emergency response equipment.",
        "sources": ["doc_001", "doc_004"],
        "confidence": 0.92,
        "timestamp": "2024-01-20T11:15:00Z"
    }
]

@router.get("/", response_class=HTMLResponse)
async def rag_dashboard(request: Request):
    """RAG system dashboard"""
    return templates.TemplateResponse("rag/index.html", {"request": request})

@router.get("/stats")
async def get_rag_stats():
    """Get RAG system statistics"""
    return {
        "documents": len(SAMPLE_DOCUMENTS),
        "queries": len(SAMPLE_QUERIES),
        "document_types": len(set([doc["document_type"] for doc in SAMPLE_DOCUMENTS])),
        "total_tags": len(set([tag for doc in SAMPLE_DOCUMENTS for tag in doc["tags"]]))
    }

@router.get("/documents")
async def get_documents(document_type: Optional[str] = None, tag: Optional[str] = None, limit: int = 100):
    """Get documents from the RAG system"""
    documents = SAMPLE_DOCUMENTS
    
    if document_type:
        documents = [doc for doc in documents if doc["document_type"] == document_type]
    
    if tag:
        documents = [doc for doc in documents if tag in doc["tags"]]
    
    return {"documents": documents[:limit]}

@router.post("/query")
async def query_rag(query: RAGQuery):
    """Query the RAG system"""
    # In production, this would use actual RAG pipeline with vector search
    results = perform_rag_query(query.question, query.context_type, query.max_results)
    
    response = {
        "answer": results["answer"],
        "confidence": results["confidence"],
        "sources": results["sources"] if query.include_sources else [],
        "query_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat()
    }
    
    return response

@router.post("/upload")
async def upload_document(
    title: str,
    description: str,
    document_type: str,
    tags: str = "",
    file: UploadFile = File(...)
):
    """Upload a document to the RAG system"""
    # In production, this would process and store the document
    document_id = str(uuid.uuid4())
    
    # Parse tags
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    new_document = {
        "id": document_id,
        "title": title,
        "description": description,
        "content": f"Content extracted from {file.filename}",  # In production, extract actual content
        "document_type": document_type,
        "tags": tag_list,
        "upload_date": datetime.now().strftime("%Y-%m-%d"),
        "file_path": f"/documents/{file.filename}"
    }
    
    # In production, add to database
    SAMPLE_DOCUMENTS.append(new_document)
    
    return {
        "message": "Document uploaded successfully",
        "document_id": document_id,
        "document": new_document
    }

@router.post("/validate")
async def validate_safety(validation: SafetyValidation):
    """Validate safety requirements using RAG"""
    # In production, this would use RAG to validate against safety standards
    validation_result = perform_safety_validation(validation)
    return validation_result

@router.get("/search")
async def search_documents(query: str, document_type: Optional[str] = None):
    """Search documents in the RAG system"""
    results = []
    query_lower = query.lower()
    
    for doc in SAMPLE_DOCUMENTS:
        if document_type and doc["document_type"] != document_type:
            continue
        
        # Simple text search
        if (query_lower in doc["title"].lower() or 
            query_lower in doc["description"].lower() or 
            query_lower in doc["content"].lower()):
            results.append(doc)
    
    return {"results": results}

@router.get("/history")
async def get_query_history(limit: int = 50):
    """Get query history"""
    return {"queries": SAMPLE_QUERIES[:limit]}

@router.get("/suggestions")
async def get_query_suggestions(query: str):
    """Get query suggestions based on partial input"""
    # In production, this would use more sophisticated suggestion logic
    suggestions = [
        "What containers are suitable for storing sulfuric acid?",
        "What safety measures are required for chemical storage?",
        "How to test container corrosion resistance?",
        "What are the regulatory requirements for hazardous chemical storage?"
    ]
    
    # Filter suggestions based on input
    filtered_suggestions = [s for s in suggestions if query.lower() in s.lower()]
    
    return {"suggestions": filtered_suggestions[:5]}

# Helper functions
def perform_rag_query(question: str, context_type: str, max_results: int):
    """Perform RAG query (simplified implementation)"""
    # In production, this would use actual RAG pipeline
    question_lower = question.lower()
    
    # Simple keyword matching
    relevant_docs = []
    for doc in SAMPLE_DOCUMENTS:
        if context_type != "all" and doc["document_type"] != context_type:
            continue
        
        relevance_score = 0
        if "sulfuric acid" in question_lower and "sulfuric_acid" in doc["tags"]:
            relevance_score += 2
        if "container" in question_lower and "container" in doc["tags"]:
            relevance_score += 2
        if "safety" in question_lower and "safety" in doc["content"].lower():
            relevance_score += 1
        if "storage" in question_lower and "storage" in doc["content"].lower():
            relevance_score += 1
        
        if relevance_score > 0:
            relevant_docs.append((doc, relevance_score))
    
    # Sort by relevance and take top results
    relevant_docs.sort(key=lambda x: x[1], reverse=True)
    top_docs = relevant_docs[:max_results]
    
    if top_docs:
        # Generate answer based on top documents
        answer = generate_answer_from_documents(question, [doc for doc, score in top_docs])
        confidence = min(0.95, 0.7 + len(top_docs) * 0.05)
        sources = [doc["id"] for doc, score in top_docs]
    else:
        answer = "I couldn't find specific information about that in the available documents."
        confidence = 0.3
        sources = []
    
    return {
        "answer": answer,
        "confidence": confidence,
        "sources": sources
    }

def generate_answer_from_documents(question: str, documents: List[Dict]):
    """Generate answer from relevant documents (simplified implementation)"""
    # In production, this would use LLM to generate coherent answers
    question_lower = question.lower()
    
    if "container" in question_lower and "sulfuric acid" in question_lower:
        return "Polyethylene containers are suitable for storing sulfuric acid. These containers have a pressure rating of 2.0 bar and temperature rating of 60°C. The material is resistant to most acids and bases."
    elif "safety" in question_lower:
        return "Safety measures include proper ventilation, PPE (personal protective equipment), and spill containment procedures. Storage areas must have proper ventilation and emergency response equipment."
    elif "test" in question_lower:
        return "Corrosion resistance testing involves exposing container materials to the target chemical for 24 hours at 25°C. A container passes if it shows no significant degradation."
    else:
        # Generic answer based on document content
        content_pieces = [doc["content"][:200] for doc in documents[:2]]
        return "Based on the available documents: " + " ".join(content_pieces)

def perform_safety_validation(validation: SafetyValidation):
    """Perform safety validation (simplified implementation)"""
    # In production, this would use RAG to validate against safety standards
    
    validation_results = {
        "valid": True,
        "warnings": [],
        "errors": [],
        "recommendations": [],
        "validation_date": datetime.now().isoformat()
    }
    
    # Simple validation logic
    if validation.substance_name.lower() == "sulfuric acid":
        if validation.container_type.lower() == "polyethylene":
            validation_results["recommendations"].append("Container type is suitable for sulfuric acid storage")
        else:
            validation_results["warnings"].append("Verify container compatibility with sulfuric acid")
    
    if "temperature" in validation.test_conditions:
        temp = validation.test_conditions["temperature"]
        if temp > 60:
            validation_results["errors"].append("Temperature exceeds container rating")
    
    if validation_results["errors"]:
        validation_results["valid"] = False
    
    return validation_results
