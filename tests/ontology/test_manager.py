"""
Tests for ontology manager functionality.
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from ontology.manager import OntologyManager


class TestOntologyManager:
    """Test cases for OntologyManager class."""
    
    def test_ontology_manager_initialization(self):
        """Test OntologyManager initialization."""
        manager = OntologyManager()
        assert manager is not None
        assert hasattr(manager, 'ontology')
    
    def test_load_ontology_from_file(self, temp_data_dir):
        """Test loading ontology from file."""
        # Create a sample ontology file
        ontology_file = os.path.join(temp_data_dir, "test_ontology.ttl")
        with open(ontology_file, 'w') as f:
            f.write("""
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

<http://example.com/HazardousSubstance> a owl:Class ;
    rdfs:label "Hazardous Substance" .
            """)
        
        manager = OntologyManager()
        result = manager.load_ontology(ontology_file)
        assert result is True
    
    def test_load_ontology_invalid_file(self):
        """Test loading ontology from non-existent file."""
        manager = OntologyManager()
        with pytest.raises(FileNotFoundError):
            manager.load_ontology("non_existent_file.ttl")
    
    def test_get_classes(self, sample_ontology_data):
        """Test retrieving ontology classes."""
        manager = OntologyManager()
        # Mock the ontology data
        manager.ontology = sample_ontology_data
        
        classes = manager.get_classes()
        assert len(classes) == 3
        assert any(cls["name"] == "HazardousSubstance" for cls in classes)
        assert any(cls["name"] == "Container" for cls in classes)
        assert any(cls["name"] == "SafetyTest" for cls in classes)
    
    def test_get_relationships(self, sample_ontology_data):
        """Test retrieving ontology relationships."""
        manager = OntologyManager()
        manager.ontology = sample_ontology_data
        
        relationships = manager.get_relationships()
        assert len(relationships) == 2
        assert any(rel["type"] == "STORED_IN" for rel in relationships)
        assert any(rel["type"] == "TESTED_BY" for rel in relationships)
    
    def test_add_class(self):
        """Test adding a new class to ontology."""
        manager = OntologyManager()
        manager.ontology = {"classes": [], "relationships": []}
        
        result = manager.add_class("NewClass", ["property1", "property2"])
        assert result is True
        assert len(manager.ontology["classes"]) == 1
        assert manager.ontology["classes"][0]["name"] == "NewClass"
    
    def test_add_relationship(self):
        """Test adding a new relationship to ontology."""
        manager = OntologyManager()
        manager.ontology = {"classes": [], "relationships": []}
        
        result = manager.add_relationship("ClassA", "ClassB", "RELATES_TO")
        assert result is True
        assert len(manager.ontology["relationships"]) == 1
        assert manager.ontology["relationships"][0]["type"] == "RELATES_TO"
    
    def test_validate_ontology(self, sample_ontology_data):
        """Test ontology validation."""
        manager = OntologyManager()
        manager.ontology = sample_ontology_data
        
        validation_result = manager.validate_ontology()
        assert validation_result["valid"] is True
        assert len(validation_result["errors"]) == 0
    
    def test_validate_ontology_with_errors(self):
        """Test ontology validation with errors."""
        manager = OntologyManager()
        manager.ontology = {
            "classes": [{"name": "ClassA"}],  # Missing properties
            "relationships": [{"source": "NonExistentClass", "target": "ClassA", "type": "RELATES_TO"}]
        }
        
        validation_result = manager.validate_ontology()
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
    
    def test_export_ontology(self, temp_data_dir, sample_ontology_data):
        """Test exporting ontology to file."""
        manager = OntologyManager()
        manager.ontology = sample_ontology_data
        
        export_file = os.path.join(temp_data_dir, "exported_ontology.ttl")
        result = manager.export_ontology(export_file)
        assert result is True
        assert os.path.exists(export_file)
    
    def test_search_classes(self, sample_ontology_data):
        """Test searching for classes by name."""
        manager = OntologyManager()
        manager.ontology = sample_ontology_data
        
        results = manager.search_classes("Hazardous")
        assert len(results) == 1
        assert results[0]["name"] == "HazardousSubstance"
    
    def test_get_class_properties(self, sample_ontology_data):
        """Test getting properties of a specific class."""
        manager = OntologyManager()
        manager.ontology = sample_ontology_data
        
        properties = manager.get_class_properties("HazardousSubstance")
        assert properties == ["name", "cas_number", "risk_level"]
    
    def test_get_class_properties_nonexistent(self, sample_ontology_data):
        """Test getting properties of non-existent class."""
        manager = OntologyManager()
        manager.ontology = sample_ontology_data
        
        properties = manager.get_class_properties("NonExistentClass")
        assert properties == [] 