"""
Tests for ontology parsing functionality.
"""
import pytest
import tempfile
import os
from ontology.parser import OntologyParser


class TestOntologyParser:
    """Test cases for OntologyParser class."""
    
    def test_parser_initialization(self):
        """Test OntologyParser initialization."""
        parser = OntologyParser()
        assert parser is not None
    
    def test_parse_turtle_file(self, temp_data_dir):
        """Test parsing Turtle format ontology file."""
        # Create a sample Turtle file
        turtle_file = os.path.join(temp_data_dir, "test.ttl")
        with open(turtle_file, 'w') as f:
            f.write("""
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

<http://example.com/HazardousSubstance> a owl:Class ;
    rdfs:label "Hazardous Substance" ;
    rdfs:comment "A substance that poses a risk to health or safety" .

<http://example.com/name> a owl:DatatypeProperty ;
    rdfs:domain <http://example.com/HazardousSubstance> ;
    rdfs:range xsd:string .
            """)
        
        parser = OntologyParser()
        result = parser.parse_turtle(turtle_file)
        assert result is not None
        assert "classes" in result
        assert "properties" in result
    
    def test_parse_rdf_xml_file(self, temp_data_dir):
        """Test parsing RDF/XML format ontology file."""
        # Create a sample RDF/XML file
        rdf_file = os.path.join(temp_data_dir, "test.rdf")
        with open(rdf_file, 'w') as f:
            f.write("""
<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
         xmlns:owl="http://www.w3.org/2002/07/owl#">
    <owl:Class rdf:about="http://example.com/HazardousSubstance">
        <rdfs:label>Hazardous Substance</rdfs:label>
    </owl:Class>
</rdf:RDF>
            """)
        
        parser = OntologyParser()
        result = parser.parse_rdf_xml(rdf_file)
        assert result is not None
    
    def test_parse_json_ld_file(self, temp_data_dir):
        """Test parsing JSON-LD format ontology file."""
        # Create a sample JSON-LD file
        jsonld_file = os.path.join(temp_data_dir, "test.jsonld")
        with open(jsonld_file, 'w') as f:
            f.write("""
{
    "@context": {
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "owl": "http://www.w3.org/2002/07/owl#"
    },
    "@graph": [
        {
            "@id": "http://example.com/HazardousSubstance",
            "@type": "owl:Class",
            "rdfs:label": "Hazardous Substance"
        }
    ]
}
            """)
        
        parser = OntologyParser()
        result = parser.parse_json_ld(jsonld_file)
        assert result is not None
    
    def test_parse_invalid_file(self):
        """Test parsing invalid file format."""
        parser = OntologyParser()
        with pytest.raises(ValueError):
            parser.parse_file("invalid_file.xyz")
    
    def test_extract_classes(self):
        """Test extracting classes from parsed ontology."""
        parser = OntologyParser()
        parsed_data = {
            "classes": [
                {"name": "HazardousSubstance", "properties": ["name", "cas_number"]},
                {"name": "Container", "properties": ["type", "capacity"]}
            ]
        }
        
        classes = parser.extract_classes(parsed_data)
        assert len(classes) == 2
        assert any(cls["name"] == "HazardousSubstance" for cls in classes)
    
    def test_extract_properties(self):
        """Test extracting properties from parsed ontology."""
        parser = OntologyParser()
        parsed_data = {
            "properties": [
                {"name": "name", "domain": "HazardousSubstance", "range": "string"},
                {"name": "cas_number", "domain": "HazardousSubstance", "range": "string"}
            ]
        }
        
        properties = parser.extract_properties(parsed_data)
        assert len(properties) == 2
        assert any(prop["name"] == "name" for prop in properties)
    
    def test_extract_relationships(self):
        """Test extracting relationships from parsed ontology."""
        parser = OntologyParser()
        parsed_data = {
            "relationships": [
                {"source": "HazardousSubstance", "target": "Container", "type": "STORED_IN"},
                {"source": "HazardousSubstance", "target": "SafetyTest", "type": "TESTED_BY"}
            ]
        }
        
        relationships = parser.extract_relationships(parsed_data)
        assert len(relationships) == 2
        assert any(rel["type"] == "STORED_IN" for rel in relationships)
    
    def test_validate_parsed_data(self):
        """Test validation of parsed ontology data."""
        parser = OntologyParser()
        valid_data = {
            "classes": [{"name": "TestClass", "properties": ["prop1"]}],
            "relationships": [{"source": "TestClass", "target": "TestClass", "type": "RELATES_TO"}]
        }
        
        result = parser.validate_parsed_data(valid_data)
        assert result["valid"] is True
    
    def test_validate_parsed_data_invalid(self):
        """Test validation of invalid parsed ontology data."""
        parser = OntologyParser()
        invalid_data = {
            "classes": [{"name": ""}],  # Empty name
            "relationships": [{"source": "NonExistent", "target": "Class", "type": "RELATES_TO"}]
        }
        
        result = parser.validate_parsed_data(invalid_data)
        assert result["valid"] is False
        assert len(result["errors"]) > 0 