"""
Tests for ontology validation functionality.
"""
import pytest
from ontology.validator import OntologyValidator


class TestOntologyValidator:
    """Test cases for OntologyValidator class."""
    
    def test_validator_initialization(self):
        """Test OntologyValidator initialization."""
        validator = OntologyValidator()
        assert validator is not None
    
    def test_validate_class_structure_valid(self):
        """Test validation of valid class structure."""
        validator = OntologyValidator()
        valid_class = {
            "name": "HazardousSubstance",
            "properties": ["name", "cas_number", "risk_level"]
        }
        
        result = validator.validate_class(valid_class)
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_class_structure_invalid(self):
        """Test validation of invalid class structure."""
        validator = OntologyValidator()
        invalid_class = {
            "name": "",  # Empty name
            "properties": []  # No properties
        }
        
        result = validator.validate_class(invalid_class)
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_validate_relationship_structure_valid(self):
        """Test validation of valid relationship structure."""
        validator = OntologyValidator()
        valid_relationship = {
            "source": "HazardousSubstance",
            "target": "Container",
            "type": "STORED_IN"
        }
        
        result = validator.validate_relationship(valid_relationship)
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_relationship_structure_invalid(self):
        """Test validation of invalid relationship structure."""
        validator = OntologyValidator()
        invalid_relationship = {
            "source": "",  # Empty source
            "target": "",  # Empty target
            "type": ""     # Empty type
        }
        
        result = validator.validate_relationship(invalid_relationship)
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_validate_property_structure_valid(self):
        """Test validation of valid property structure."""
        validator = OntologyValidator()
        valid_property = {
            "name": "cas_number",
            "domain": "HazardousSubstance",
            "range": "string"
        }
        
        result = validator.validate_property(valid_property)
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_property_structure_invalid(self):
        """Test validation of invalid property structure."""
        validator = OntologyValidator()
        invalid_property = {
            "name": "",  # Empty name
            "domain": "",  # Empty domain
            "range": ""    # Empty range
        }
        
        result = validator.validate_property(invalid_property)
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_validate_ontology_consistency(self, sample_ontology_data):
        """Test validation of ontology consistency."""
        validator = OntologyValidator()
        
        result = validator.validate_ontology_consistency(sample_ontology_data)
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_ontology_consistency_inconsistent(self):
        """Test validation of inconsistent ontology."""
        validator = OntologyValidator()
        inconsistent_data = {
            "classes": [{"name": "ClassA", "properties": ["prop1"]}],
            "relationships": [
                {"source": "NonExistentClass", "target": "ClassA", "type": "RELATES_TO"}
            ]
        }
        
        result = validator.validate_ontology_consistency(inconsistent_data)
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_validate_circular_references(self):
        """Test validation for circular references."""
        validator = OntologyValidator()
        data_with_circular_ref = {
            "classes": [
                {"name": "ClassA", "properties": ["prop1"]},
                {"name": "ClassB", "properties": ["prop2"]}
            ],
            "relationships": [
                {"source": "ClassA", "target": "ClassB", "type": "RELATES_TO"},
                {"source": "ClassB", "target": "ClassA", "type": "RELATES_TO"}
            ]
        }
        
        result = validator.validate_circular_references(data_with_circular_ref)
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_validate_no_circular_references(self, sample_ontology_data):
        """Test validation with no circular references."""
        validator = OntologyValidator()
        
        result = validator.validate_circular_references(sample_ontology_data)
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_class_names_unique(self):
        """Test validation of unique class names."""
        validator = OntologyValidator()
        data_with_duplicate_names = {
            "classes": [
                {"name": "TestClass", "properties": ["prop1"]},
                {"name": "TestClass", "properties": ["prop2"]}  # Duplicate name
            ]
        }
        
        result = validator.validate_class_names_unique(data_with_duplicate_names)
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_validate_class_names_unique_valid(self, sample_ontology_data):
        """Test validation of unique class names with valid data."""
        validator = OntologyValidator()
        
        result = validator.validate_class_names_unique(sample_ontology_data)
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_property_names_unique(self):
        """Test validation of unique property names within a class."""
        validator = OntologyValidator()
        data_with_duplicate_properties = {
            "classes": [
                {"name": "TestClass", "properties": ["prop1", "prop1"]}  # Duplicate property
            ]
        }
        
        result = validator.validate_property_names_unique(data_with_duplicate_properties)
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_validate_property_names_unique_valid(self, sample_ontology_data):
        """Test validation of unique property names with valid data."""
        validator = OntologyValidator()
        
        result = validator.validate_property_names_unique(sample_ontology_data)
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_comprehensive_validation(self, sample_ontology_data):
        """Test comprehensive validation of complete ontology."""
        validator = OntologyValidator()
        
        result = validator.validate_comprehensive(sample_ontology_data)
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert "structure" in result
        assert "consistency" in result
        assert "circular_references" in result 