"""
Ontology management and RDF operations for HazardSafe-KG platform.
"""

from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import json
from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal, URIRef
from rdflib.plugins.sparql import prepareQuery
from pyshacl import validate
import os
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class OntologyManager:
    """Manages ontology operations including RDF/OWL and SHACL validation."""
    
    def __init__(self):
        self.graph = Graph()
        self.namespace = Namespace("http://hazardsafe-kg.org/ontology#")
        self.graph.bind("hs", self.namespace)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        
        # Load standard namespaces
        self.graph.bind("xsd", "http://www.w3.org/2001/XMLSchema#")
        self.graph.bind("sh", "http://www.w3.org/ns/shacl#")
        self.graph.bind("skos", "http://www.w3.org/2004/02/skos/core#")
        self.graph.bind("dc", "http://purl.org/dc/elements/1.1/")
        self.graph.bind("dcterms", "http://purl.org/dc/terms/")
        
    async def load_ontology_files(self, directory: str = "data/ontology") -> bool:
        """Load ontology files from directory in multiple formats."""
        try:
            ontology_dir = Path(directory)
            if not ontology_dir.exists():
                logger.warning(f"Ontology directory {directory} does not exist")
                return False
            
            # Supported file formats and their parsers
            format_parsers = {
                "*.ttl": self._parse_turtle,
                "*.owl": self._parse_owl,
                "*.rdf": self._parse_rdf_xml,
                "*.xml": self._parse_rdf_xml,
                "*.json": self._parse_json_ld,
                "*.jsonld": self._parse_json_ld,
                "*.nt": self._parse_ntriples,
                "*.n3": self._parse_n3,
                "*.trig": self._parse_trig,
                "*.shacl": self._parse_shacl,
                "*.shapes": self._parse_shacl
            }
            
            loaded_files = 0
            for pattern, parser_func in format_parsers.items():
                for file_path in ontology_dir.rglob(pattern):
                    try:
                        success = await parser_func(file_path)
                        if success:
                            loaded_files += 1
                            logger.info(f"Loaded ontology file: {file_path}")
                        else:
                            logger.warning(f"Failed to load {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to load {file_path}: {e}")
            
            logger.info(f"Loaded {loaded_files} ontology files with {len(self.graph)} triples")
            return loaded_files > 0
            
        except Exception as e:
            logger.error(f"Failed to load ontology files: {e}")
            return False
    
    async def _parse_turtle(self, file_path: Path) -> bool:
        """Parse Turtle (.ttl) files."""
        try:
            self.graph.parse(file_path, format="turtle")
            return True
        except Exception as e:
            logger.error(f"Error parsing Turtle file {file_path}: {e}")
            return False
    
    async def _parse_owl(self, file_path: Path) -> bool:
        """Parse OWL (.owl) files."""
        try:
            self.graph.parse(file_path, format="xml")
            return True
        except Exception as e:
            logger.error(f"Error parsing OWL file {file_path}: {e}")
            return False
    
    async def _parse_rdf_xml(self, file_path: Path) -> bool:
        """Parse RDF/XML (.rdf, .xml) files."""
        try:
            self.graph.parse(file_path, format="xml")
            return True
        except Exception as e:
            logger.error(f"Error parsing RDF/XML file {file_path}: {e}")
            return False
    
    async def _parse_json_ld(self, file_path: Path) -> bool:
        """Parse JSON-LD (.json, .jsonld) files."""
        try:
            self.graph.parse(file_path, format="json-ld")
            return True
        except Exception as e:
            logger.error(f"Error parsing JSON-LD file {file_path}: {e}")
            return False
    
    async def _parse_ntriples(self, file_path: Path) -> bool:
        """Parse N-Triples (.nt) files."""
        try:
            self.graph.parse(file_path, format="nt")
            return True
        except Exception as e:
            logger.error(f"Error parsing N-Triples file {file_path}: {e}")
            return False
    
    async def _parse_n3(self, file_path: Path) -> bool:
        """Parse Notation3 (.n3) files."""
        try:
            self.graph.parse(file_path, format="n3")
            return True
        except Exception as e:
            logger.error(f"Error parsing N3 file {file_path}: {e}")
            return False
    
    async def _parse_trig(self, file_path: Path) -> bool:
        """Parse TriG (.trig) files."""
        try:
            self.graph.parse(file_path, format="trig")
            return True
        except Exception as e:
            logger.error(f"Error parsing TriG file {file_path}: {e}")
            return False
    
    async def _parse_shacl(self, file_path: Path) -> bool:
        """Parse SHACL (.shacl, .shapes) files."""
        try:
            # SHACL files can be in various formats, try common ones
            if file_path.suffix.lower() in ['.ttl', '.n3']:
                self.graph.parse(file_path, format="turtle")
            elif file_path.suffix.lower() in ['.xml', '.rdf']:
                self.graph.parse(file_path, format="xml")
            elif file_path.suffix.lower() in ['.json', '.jsonld']:
                self.graph.parse(file_path, format="json-ld")
            else:
                # Default to turtle
                self.graph.parse(file_path, format="turtle")
            return True
        except Exception as e:
            logger.error(f"Error parsing SHACL file {file_path}: {e}")
            return False
    
    async def export_ontology(self, format: str = "turtle", file_path: Optional[str] = None) -> str:
        """Export ontology in specified format."""
        try:
            if file_path:
                self.graph.serialize(destination=file_path, format=format)
                logger.info(f"Ontology exported to {file_path}")
                return f"Exported to {file_path}"
            else:
                return self.graph.serialize(format=format)
        except Exception as e:
            logger.error(f"Failed to export ontology: {e}")
            return ""
    
    async def get_supported_formats(self) -> List[Dict[str, str]]:
        """Get list of supported ontology formats."""
        return [
            {"extension": ".ttl", "name": "Turtle", "description": "Readable RDF format"},
            {"extension": ".owl", "name": "OWL", "description": "Web Ontology Language"},
            {"extension": ".rdf", "name": "RDF/XML", "description": "XML-based RDF format"},
            {"extension": ".xml", "name": "RDF/XML", "description": "XML-based RDF format"},
            {"extension": ".json", "name": "JSON-LD", "description": "JSON for Linked Data"},
            {"extension": ".jsonld", "name": "JSON-LD", "description": "JSON for Linked Data"},
            {"extension": ".nt", "name": "N-Triples", "description": "Simple line-based RDF format"},
            {"extension": ".n3", "name": "Notation3", "description": "Extended Turtle format"},
            {"extension": ".trig", "name": "TriG", "description": "Turtle for named graphs"},
            {"extension": ".shacl", "name": "SHACL", "description": "Shapes Constraint Language"},
            {"extension": ".shapes", "name": "SHACL", "description": "Shapes Constraint Language"}
        ]
    
    async def convert_format(self, input_file: str, output_format: str, output_file: str) -> bool:
        """Convert ontology from one format to another."""
        try:
            # Create a temporary graph for the input file
            temp_graph = Graph()
            
            # Determine input format from file extension
            input_ext = Path(input_file).suffix.lower()
            format_mapping = {
                ".ttl": "turtle",
                ".owl": "xml",
                ".rdf": "xml",
                ".xml": "xml",
                ".json": "json-ld",
                ".jsonld": "json-ld",
                ".nt": "nt",
                ".n3": "n3",
                ".trig": "trig"
            }
            
            input_format = format_mapping.get(input_ext, "turtle")
            
            # Parse input file
            temp_graph.parse(input_file, format=input_format)
            
            # Export to new format
            temp_graph.serialize(destination=output_file, format=output_format)
            
            logger.info(f"Converted {input_file} to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to convert format: {e}")
            return False

    async def get_classes(self) -> List[Dict[str, Any]]:
        """Get all ontology classes."""
        try:
            query = """
            SELECT ?class ?label ?comment ?superclass
            WHERE {
                ?class a owl:Class .
                OPTIONAL { ?class rdfs:label ?label }
                OPTIONAL { ?class rdfs:comment ?comment }
                OPTIONAL { ?class rdfs:subClassOf ?superclass }
            }
            ORDER BY ?label
            """
            
            results = []
            for row in self.graph.query(query):
                results.append({
                    "uri": str(row[0]),
                    "label": str(row[1]) if row[1] else "",
                    "comment": str(row[2]) if row[2] else "",
                    "superclass": str(row[3]) if row[3] else None
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get classes: {e}")
            return []
    
    async def get_properties(self) -> List[Dict[str, Any]]:
        """Get all ontology properties."""
        try:
            query = """
            SELECT ?property ?label ?comment ?domain ?range ?type
            WHERE {
                ?property a ?type .
                FILTER(?type IN (owl:ObjectProperty, owl:DatatypeProperty))
                OPTIONAL { ?property rdfs:label ?label }
                OPTIONAL { ?property rdfs:comment ?comment }
                OPTIONAL { ?property rdfs:domain ?domain }
                OPTIONAL { ?property rdfs:range ?range }
            }
            ORDER BY ?label
            """
            
            results = []
            for row in self.graph.query(query):
                results.append({
                    "uri": str(row[0]),
                    "label": str(row[1]) if row[1] else "",
                    "comment": str(row[2]) if row[2] else "",
                    "domain": str(row[3]) if row[3] else None,
                    "range": str(row[4]) if row[4] else None,
                    "type": str(row[5]).split("#")[-1] if row[5] else ""
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get properties: {e}")
            return []
    
    async def get_instances(self, class_uri: str = None) -> List[Dict[str, Any]]:
        """Get ontology instances, optionally filtered by class."""
        try:
            if class_uri:
                query = f"""
                SELECT ?instance ?label ?comment
                WHERE {{
                    ?instance a <{class_uri}> .
                    OPTIONAL {{ ?instance rdfs:label ?label }}
                    OPTIONAL {{ ?instance rdfs:comment ?comment }}
                }}
                ORDER BY ?label
                """
            else:
                query = """
                SELECT ?instance ?label ?comment ?class
                WHERE {
                    ?instance a ?class .
                    OPTIONAL { ?instance rdfs:label ?label }
                    OPTIONAL { ?instance rdfs:comment ?comment }
                }
                ORDER BY ?label
                """
            
            results = []
            for row in self.graph.query(query):
                result = {
                    "uri": str(row[0]),
                    "label": str(row[1]) if row[1] else "",
                    "comment": str(row[2]) if row[2] else ""
                }
                if not class_uri and row[3]:
                    result["class"] = str(row[3])
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get instances: {e}")
            return []
    
    async def add_class(self, class_data: Dict[str, Any]) -> bool:
        """Add a new class to the ontology."""
        try:
            class_uri = URIRef(class_data["uri"])
            
            # Add class
            self.graph.add((class_uri, RDF.type, OWL.Class))
            
            # Add label
            if class_data.get("label"):
                self.graph.add((class_uri, RDFS.label, Literal(class_data["label"])))
            
            # Add comment
            if class_data.get("comment"):
                self.graph.add((class_uri, RDFS.comment, Literal(class_data["comment"])))
            
            # Add superclass
            if class_data.get("superclass"):
                superclass_uri = URIRef(class_data["superclass"])
                self.graph.add((class_uri, RDFS.subClassOf, superclass_uri))
            
            logger.info(f"Added class: {class_data['uri']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add class: {e}")
            return False
    
    async def add_property(self, property_data: Dict[str, Any]) -> bool:
        """Add a new property to the ontology."""
        try:
            property_uri = URIRef(property_data["uri"])
            
            # Determine property type
            if property_data.get("type") == "ObjectProperty":
                property_type = OWL.ObjectProperty
            else:
                property_type = OWL.DatatypeProperty
            
            # Add property
            self.graph.add((property_uri, RDF.type, property_type))
            
            # Add label
            if property_data.get("label"):
                self.graph.add((property_uri, RDFS.label, Literal(property_data["label"])))
            
            # Add comment
            if property_data.get("comment"):
                self.graph.add((property_uri, RDFS.comment, Literal(property_data["comment"])))
            
            # Add domain
            if property_data.get("domain"):
                domain_uri = URIRef(property_data["domain"])
                self.graph.add((property_uri, RDFS.domain, domain_uri))
            
            # Add range
            if property_data.get("range"):
                range_uri = URIRef(property_data["range"])
                self.graph.add((property_uri, RDFS.range, range_uri))
            
            logger.info(f"Added property: {property_data['uri']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add property: {e}")
            return False
    
    async def add_instance(self, instance_data: Dict[str, Any]) -> bool:
        """Add a new instance to the ontology."""
        try:
            instance_uri = URIRef(instance_data["uri"])
            class_uri = URIRef(instance_data["class"])
            
            # Add instance
            self.graph.add((instance_uri, RDF.type, class_uri))
            
            # Add label
            if instance_data.get("label"):
                self.graph.add((instance_uri, RDFS.label, Literal(instance_data["label"])))
            
            # Add comment
            if instance_data.get("comment"):
                self.graph.add((instance_uri, RDFS.comment, Literal(instance_data["comment"])))
            
            # Add properties
            for prop_uri, value in instance_data.get("properties", {}).items():
                prop_ref = URIRef(prop_uri)
                if isinstance(value, str) and value.startswith("http"):
                    value_ref = URIRef(value)
                    self.graph.add((instance_uri, prop_ref, value_ref))
                else:
                    self.graph.add((instance_uri, prop_ref, Literal(value)))
            
            logger.info(f"Added instance: {instance_data['uri']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add instance: {e}")
            return False
    
    async def validate_substance(self, substance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate substance data against ontology constraints."""
        try:
            # Create a data graph for validation
            data_graph = Graph()
            data_graph.bind("hs", self.namespace)
            
            # Add substance instance to data graph
            substance_uri = URIRef(f"{self.namespace}{substance_data['id']}")
            substance_class = URIRef(f"{self.namespace}HazardousSubstance")
            
            data_graph.add((substance_uri, RDF.type, substance_class))
            
            # Add properties
            for key, value in substance_data.items():
                if key != "id" and value:
                    prop_uri = URIRef(f"{self.namespace}{key}")
                    data_graph.add((substance_uri, prop_uri, Literal(value)))
            
            # Validate against ontology
            validation_result = await self.validate_data(data_graph)
            
            return {
                "valid": validation_result["conforms"],
                "errors": validation_result["results"] if not validation_result["conforms"] else []
            }
            
        except Exception as e:
            logger.error(f"Error validating substance: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {e}"]
            }
    
    async def validate_data(self, data_graph: Graph, shapes_graph: Graph = None) -> Dict[str, Any]:
        """Validate data against SHACL constraints."""
        try:
            if shapes_graph is None:
                # Use default shapes from ontology
                shapes_graph = self.graph
            
            conforms, results_graph, results_text = validate(
                data_graph,
                shacl_graph=shapes_graph,
                ont_graph=self.graph,
                inference='rdfs'
            )
            
            # Parse validation results
            validation_results = []
            for result in results_graph.query("""
                SELECT ?focusNode ?resultPath ?resultSeverity ?resultMessage
                WHERE {
                    ?result a sh:ValidationResult .
                    ?result sh:focusNode ?focusNode .
                    OPTIONAL { ?result sh:resultPath ?resultPath }
                    OPTIONAL { ?result sh:resultSeverity ?resultSeverity }
                    OPTIONAL { ?result sh:resultMessage ?resultMessage }
                }
            """):
                validation_results.append({
                    "focus_node": str(result[0]),
                    "path": str(result[1]) if result[1] else None,
                    "severity": str(result[2]) if result[2] else None,
                    "message": str(result[3]) if result[3] else None
                })
            
            return {
                "conforms": conforms,
                "results": validation_results,
                "results_text": results_text
            }
            
        except Exception as e:
            logger.error(f"Failed to validate data: {e}")
            return {
                "conforms": False,
                "results": [],
                "results_text": f"Validation error: {e}"
            }
    
    async def get_ontology_stats(self) -> Dict[str, int]:
        """Get ontology statistics."""
        try:
            stats = {}
            
            # Count classes
            class_query = "SELECT (COUNT(?class) AS ?count) WHERE { ?class a owl:Class }"
            result = self.graph.query(class_query)
            stats["classes"] = int(result.bindings[0]["count"])
            
            # Count properties
            prop_query = "SELECT (COUNT(?prop) AS ?count) WHERE { ?prop a ?type . FILTER(?type IN (owl:ObjectProperty, owl:DatatypeProperty)) }"
            result = self.graph.query(prop_query)
            stats["properties"] = int(result.bindings[0]["count"])
            
            # Count instances
            instance_query = "SELECT (COUNT(?instance) AS ?count) WHERE { ?instance a ?class . FILTER(?class != owl:Class) }"
            result = self.graph.query(instance_query)
            stats["instances"] = int(result.bindings[0]["count"])
            
            # Count triples
            stats["triples"] = len(self.graph)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get ontology stats: {e}")
            return {}
    
    async def save_ontology(self, file_path: str, format: str = "turtle") -> bool:
        """Save ontology to file."""
        try:
            self.graph.serialize(destination=file_path, format=format)
            logger.info(f"Ontology saved to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save ontology: {e}")
            return False

# Global ontology manager instance
ontology_manager = OntologyManager()

async def init_ontology_manager():
    """Initialize ontology manager."""
    await ontology_manager.load_ontology_files() 