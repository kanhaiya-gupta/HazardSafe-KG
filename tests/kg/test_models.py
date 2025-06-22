"""
Tests for knowledge graph data models.
"""
import pytest
from kg.models import Node, Relationship, GraphSchema


class TestNode:
    """Test cases for Node class."""
    
    def test_node_creation(self):
        """Test creating a node."""
        node = Node(
            id="1",
            label="HazardousSubstance",
            properties={"name": "Methanol", "cas_number": "67-56-1"}
        )
        
        assert node.id == "1"
        assert node.label == "HazardousSubstance"
        assert node.properties["name"] == "Methanol"
        assert node.properties["cas_number"] == "67-56-1"
    
    def test_node_creation_without_id(self):
        """Test creating a node without ID (auto-generated)."""
        node = Node(
            label="HazardousSubstance",
            properties={"name": "Methanol"}
        )
        
        assert node.id is not None
        assert node.label == "HazardousSubstance"
        assert node.properties["name"] == "Methanol"
    
    def test_node_equality(self):
        """Test node equality comparison."""
        node1 = Node(id="1", label="Test", properties={"name": "Test"})
        node2 = Node(id="1", label="Test", properties={"name": "Test"})
        node3 = Node(id="2", label="Test", properties={"name": "Test"})
        
        assert node1 == node2
        assert node1 != node3
    
    def test_node_to_dict(self):
        """Test converting node to dictionary."""
        node = Node(
            id="1",
            label="HazardousSubstance",
            properties={"name": "Methanol", "cas_number": "67-56-1"}
        )
        
        node_dict = node.to_dict()
        assert node_dict["id"] == "1"
        assert node_dict["label"] == "HazardousSubstance"
        assert node_dict["properties"]["name"] == "Methanol"
    
    def test_node_from_dict(self):
        """Test creating node from dictionary."""
        node_data = {
            "id": "1",
            "label": "HazardousSubstance",
            "properties": {"name": "Methanol", "cas_number": "67-56-1"}
        }
        
        node = Node.from_dict(node_data)
        assert node.id == "1"
        assert node.label == "HazardousSubstance"
        assert node.properties["name"] == "Methanol"
    
    def test_node_validation_valid(self):
        """Test node validation with valid data."""
        node = Node(
            id="1",
            label="HazardousSubstance",
            properties={"name": "Methanol"}
        )
        
        result = node.validate()
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_node_validation_invalid(self):
        """Test node validation with invalid data."""
        node = Node(
            id="",
            label="",
            properties={}
        )
        
        result = node.validate()
        assert result["valid"] is False
        assert len(result["errors"]) > 0


class TestRelationship:
    """Test cases for Relationship class."""
    
    def test_relationship_creation(self):
        """Test creating a relationship."""
        relationship = Relationship(
            id="rel1",
            source_id="1",
            target_id="2",
            type="STORED_IN",
            properties={"since": "2023-01-01"}
        )
        
        assert relationship.id == "rel1"
        assert relationship.source_id == "1"
        assert relationship.target_id == "2"
        assert relationship.type == "STORED_IN"
        assert relationship.properties["since"] == "2023-01-01"
    
    def test_relationship_creation_without_id(self):
        """Test creating a relationship without ID (auto-generated)."""
        relationship = Relationship(
            source_id="1",
            target_id="2",
            type="STORED_IN"
        )
        
        assert relationship.id is not None
        assert relationship.source_id == "1"
        assert relationship.target_id == "2"
        assert relationship.type == "STORED_IN"
    
    def test_relationship_equality(self):
        """Test relationship equality comparison."""
        rel1 = Relationship(id="1", source_id="1", target_id="2", type="TEST")
        rel2 = Relationship(id="1", source_id="1", target_id="2", type="TEST")
        rel3 = Relationship(id="2", source_id="1", target_id="2", type="TEST")
        
        assert rel1 == rel2
        assert rel1 != rel3
    
    def test_relationship_to_dict(self):
        """Test converting relationship to dictionary."""
        relationship = Relationship(
            id="rel1",
            source_id="1",
            target_id="2",
            type="STORED_IN",
            properties={"since": "2023-01-01"}
        )
        
        rel_dict = relationship.to_dict()
        assert rel_dict["id"] == "rel1"
        assert rel_dict["source_id"] == "1"
        assert rel_dict["target_id"] == "2"
        assert rel_dict["type"] == "STORED_IN"
    
    def test_relationship_from_dict(self):
        """Test creating relationship from dictionary."""
        rel_data = {
            "id": "rel1",
            "source_id": "1",
            "target_id": "2",
            "type": "STORED_IN",
            "properties": {"since": "2023-01-01"}
        }
        
        relationship = Relationship.from_dict(rel_data)
        assert relationship.id == "rel1"
        assert relationship.source_id == "1"
        assert relationship.target_id == "2"
        assert relationship.type == "STORED_IN"
    
    def test_relationship_validation_valid(self):
        """Test relationship validation with valid data."""
        relationship = Relationship(
            source_id="1",
            target_id="2",
            type="STORED_IN"
        )
        
        result = relationship.validate()
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_relationship_validation_invalid(self):
        """Test relationship validation with invalid data."""
        relationship = Relationship(
            source_id="",
            target_id="",
            type=""
        )
        
        result = relationship.validate()
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_relationship_self_reference(self):
        """Test relationship with self-reference (source = target)."""
        relationship = Relationship(
            source_id="1",
            target_id="1",
            type="SELF_REFERENCE"
        )
        
        result = relationship.validate()
        # Self-reference might be valid in some cases
        assert "self_reference" in result


class TestGraphSchema:
    """Test cases for GraphSchema class."""
    
    def test_schema_creation(self):
        """Test creating a graph schema."""
        schema = GraphSchema(
            name="HazardousSubstances",
            description="Schema for hazardous substances knowledge graph",
            node_labels=["HazardousSubstance", "Container", "SafetyTest"],
            relationship_types=["STORED_IN", "TESTED_BY", "CONTAINS"]
        )
        
        assert schema.name == "HazardousSubstances"
        assert schema.description == "Schema for hazardous substances knowledge graph"
        assert len(schema.node_labels) == 3
        assert len(schema.relationship_types) == 3
    
    def test_schema_validation_valid(self):
        """Test schema validation with valid data."""
        schema = GraphSchema(
            name="TestSchema",
            description="Test schema",
            node_labels=["Node1", "Node2"],
            relationship_types=["REL1", "REL2"]
        )
        
        result = schema.validate()
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_schema_validation_invalid(self):
        """Test schema validation with invalid data."""
        schema = GraphSchema(
            name="",
            description="",
            node_labels=[],
            relationship_types=[]
        )
        
        result = schema.validate()
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_schema_to_dict(self):
        """Test converting schema to dictionary."""
        schema = GraphSchema(
            name="TestSchema",
            description="Test description",
            node_labels=["Node1"],
            relationship_types=["REL1"]
        )
        
        schema_dict = schema.to_dict()
        assert schema_dict["name"] == "TestSchema"
        assert schema_dict["description"] == "Test description"
        assert schema_dict["node_labels"] == ["Node1"]
        assert schema_dict["relationship_types"] == ["REL1"]
    
    def test_schema_from_dict(self):
        """Test creating schema from dictionary."""
        schema_data = {
            "name": "TestSchema",
            "description": "Test description",
            "node_labels": ["Node1"],
            "relationship_types": ["REL1"]
        }
        
        schema = GraphSchema.from_dict(schema_data)
        assert schema.name == "TestSchema"
        assert schema.description == "Test description"
        assert schema.node_labels == ["Node1"]
        assert schema.relationship_types == ["REL1"] 