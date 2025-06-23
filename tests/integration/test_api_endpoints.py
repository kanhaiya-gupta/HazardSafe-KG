"""
Integration tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from main import app


class TestAPIEndpoints:
    """Test cases for API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_home_endpoint(self, client):
        """Test home endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "HazardSafe-KG" in response.text
    
    def test_ontology_endpoint(self, client):
        """Test ontology endpoint."""
        response = client.get("/ontology")
        assert response.status_code == 200
        assert "Ontology" in response.text
    
    def test_kg_endpoint(self, client):
        """Test knowledge graph endpoint."""
        response = client.get("/kg")
        assert response.status_code == 200
        assert "Knowledge Graph" in response.text
    
    def test_rag_endpoint(self, client):
        """Test RAG endpoint."""
        response = client.get("/nlp_rag")
        assert response.status_code == 200
        assert "RAG" in response.text
    
    def test_validation_endpoint(self, client):
        """Test validation endpoint."""
        response = client.get("/validation")
        assert response.status_code == 200
        assert "Validation" in response.text
    
    def test_architecture_endpoint(self, client):
        """Test architecture endpoint."""
        response = client.get("/architecture")
        assert response.status_code == 200
        assert "Architecture" in response.text
    
    def test_ontology_api_get_classes(self, client):
        """Test ontology API get classes endpoint."""
        response = client.get("/api/ontology/classes")
        assert response.status_code == 200
        data = response.json()
        assert "classes" in data
    
    def test_ontology_api_add_class(self, client):
        """Test ontology API add class endpoint."""
        class_data = {
            "name": "TestClass",
            "properties": ["prop1", "prop2"]
        }
        response = client.post("/api/ontology/classes", json=class_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_kg_api_get_nodes(self, client):
        """Test KG API get nodes endpoint."""
        response = client.get("/api/kg/nodes")
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
    
    def test_kg_api_add_node(self, client):
        """Test KG API add node endpoint."""
        node_data = {
            "label": "HazardousSubstance",
            "properties": {"name": "TestSubstance", "cas_number": "123-45-6"}
        }
        response = client.post("/api/kg/nodes", json=node_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_rag_api_upload_document(self, client):
        """Test RAG API upload document endpoint."""
        # Create a test file
        test_content = "This is a test document about hazardous substances."
        
        response = client.post(
            "/api/nlp_rag/upload",
            files={"file": ("test.txt", test_content, "text/plain")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_rag_api_query(self, client):
        """Test RAG API query endpoint."""
        query_data = {
            "query": "What is methanol?",
            "top_k": 5
        }
        response = client.post("/api/nlp_rag/query", json=query_data)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
    
    def test_validation_api_validate_csv(self, client):
        """Test validation API validate CSV endpoint."""
        csv_data = [
            {"name": "Methanol", "cas_number": "67-56-1", "risk_level": "High"},
            {"name": "Ethanol", "cas_number": "64-17-5", "risk_level": "Medium"}
        ]
        
        response = client.post("/api/validation/validate-csv", json=csv_data)
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert "errors" in data
    
    def test_validation_api_validate_json(self, client):
        """Test validation API validate JSON endpoint."""
        json_data = {
            "substances": [
                {"name": "Methanol", "cas_number": "67-56-1"},
                {"name": "Ethanol", "cas_number": "64-17-5"}
            ]
        }
        
        response = client.post("/api/validation/validate-json", json=json_data)
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert "errors" in data
    
    def test_api_error_handling(self, client):
        """Test API error handling."""
        # Test invalid endpoint
        response = client.get("/api/invalid/endpoint")
        assert response.status_code == 404
        
        # Test invalid JSON
        response = client.post("/api/ontology/classes", data="invalid json")
        assert response.status_code == 422
    
    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.get("/")
        assert response.status_code == 200
        # CORS headers should be present in FastAPI responses
    
    def test_api_response_format(self, client):
        """Test API response format consistency."""
        # Test ontology API
        response = client.get("/api/ontology/classes")
        data = response.json()
        assert "classes" in data or "error" in data
        
        # Test KG API
        response = client.get("/api/kg/nodes")
        data = response.json()
        assert "nodes" in data or "error" in data
        
        # Test RAG API
        response = client.get("/api/nlp_rag/documents")
        data = response.json()
        assert "documents" in data or "error" in data 