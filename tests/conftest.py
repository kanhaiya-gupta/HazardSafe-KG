"""
Pytest configuration and common fixtures for HazardSafe-KG tests.
"""
import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_ontology_data():
    """Sample ontology data for testing."""
    return {
        "classes": [
            {"name": "HazardousSubstance", "properties": ["name", "cas_number", "risk_level"]},
            {"name": "Container", "properties": ["type", "material", "capacity"]},
            {"name": "SafetyTest", "properties": ["test_type", "result", "date"]}
        ],
        "relationships": [
            {"source": "HazardousSubstance", "target": "Container", "type": "STORED_IN"},
            {"source": "HazardousSubstance", "target": "SafetyTest", "type": "TESTED_BY"}
        ]
    }


@pytest.fixture
def sample_kg_data():
    """Sample knowledge graph data for testing."""
    return {
        "nodes": [
            {"id": "1", "label": "HazardousSubstance", "properties": {"name": "Methanol", "cas_number": "67-56-1"}},
            {"id": "2", "label": "Container", "properties": {"type": "Steel_Drum", "capacity": "200L"}},
            {"id": "3", "label": "SafetyTest", "properties": {"test_type": "Flash_Point", "result": "Pass"}}
        ],
        "relationships": [
            {"source": "1", "target": "2", "type": "STORED_IN"},
            {"source": "1", "target": "3", "type": "TESTED_BY"}
        ]
    }


@pytest.fixture
def sample_rag_data():
    """Sample RAG data for testing."""
    return {
        "documents": [
            {
                "id": "doc1",
                "content": "Methanol is a hazardous substance with CAS number 67-56-1. It has a flash point of 11°C.",
                "metadata": {"source": "safety_data_sheet.pdf", "page": 1}
            },
            {
                "id": "doc2", 
                "content": "Storage requirements for methanol include steel containers with proper ventilation.",
                "metadata": {"source": "storage_guidelines.pdf", "page": 3}
            }
        ],
        "queries": [
            "What is the flash point of methanol?",
            "How should methanol be stored?",
            "What is the CAS number for methanol?"
        ]
    }


@pytest.fixture
def sample_validation_data():
    """Sample validation data for testing."""
    return {
        "valid_csv": [
            {"name": "Methanol", "cas_number": "67-56-1", "risk_level": "High"},
            {"name": "Ethanol", "cas_number": "64-17-5", "risk_level": "Medium"}
        ],
        "invalid_csv": [
            {"name": "", "cas_number": "invalid", "risk_level": "Unknown"},
            {"name": "Test", "cas_number": "", "risk_level": ""}
        ],
        "validation_rules": {
            "required_fields": ["name", "cas_number"],
            "cas_number_format": r"^\d{1,7}-\d{2}-\d$",
            "risk_levels": ["Low", "Medium", "High"]
        }
    }


@pytest.fixture
def mock_neo4j_connection():
    """Mock Neo4j connection for testing."""
    class MockNeo4jConnection:
        def __init__(self):
            self.nodes = []
            self.relationships = []
        
        def run(self, query, **kwargs):
            return MockResult()
        
        def close(self):
            pass
    
    class MockResult:
        def __iter__(self):
            return iter([])
    
    return MockNeo4jConnection()


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing."""
    class MockVectorStore:
        def __init__(self):
            self.documents = []
            self.embeddings = {}
        
        def add_documents(self, documents):
            self.documents.extend(documents)
            return True
        
        def similarity_search(self, query, k=5):
            return self.documents[:k]
        
        def delete_collection(self):
            self.documents = []
            return True
    
    return MockVectorStore() 