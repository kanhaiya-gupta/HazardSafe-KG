"""
Ontology to Knowledge Graph Pipeline
Implements the 5-step process from TTL ontology files to Neo4j knowledge graph.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import asyncio
from datetime import datetime
import uuid

from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal, URIRef, BNode
from rdflib.plugins.sparql import prepareQuery
from pyshacl import validate
import json

from .manager import OntologyManager
from ..kg.services import KnowledgeGraphService
from ..kg.models import HazardousSubstance, Container, SafetyTest, RiskAssessment
from ..validation.validator import DataValidator

logger = logging.getLogger(__name__)

class OntologyToKGPipeline:
    """
    Pipeline for converting ontology files to knowledge graph.
    
    Steps:
    1. Ontology File Ingestion: TTL Ontology Files → Parsed RDF graph
    2. Ontology Management: RDF graph → Ontology schema + SHACL constraints
    3. SHACL Validation: Extracted entities/relations → Ontology-validated RDF triples
    4. Data Quality Check: Validated triples → High-quality data
    5. Knowledge Graph Storage: Validated triples → Nodes/edges in Neo4j
    """
    
    def __init__(self):
        self.ontology_manager = OntologyManager()
        self.kg_service = KnowledgeGraphService()
        self.validator = DataValidator()
        self.rdf_graph = Graph()
        self.shacl_graph = Graph()
        self.validated_triples = []
        self.quality_metrics = {}
        
        # Define HazardSafe-KG namespace
        self.hs_namespace = Namespace("http://hazardsafe-kg.org/ontology#")
        self.rdf_graph.bind("hs", self.hs_namespace)
        
    async def initialize(self):
        """Initialize all components of the pipeline."""
        try:
            await self.kg_service.initialize()
            logger.info("Ontology-to-KG pipeline initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            return False
    
    async def close(self):
        """Close all connections and cleanup."""
        try:
            await self.kg_service.close()
            logger.info("Pipeline connections closed")
        except Exception as e:
            logger.error(f"Error closing pipeline: {e}")
    
    async def run_pipeline(self, ontology_directory: str = "data/ontology") -> Dict[str, Any]:
        """
        Run the complete ontology-to-knowledge graph pipeline.
        
        Args:
            ontology_directory: Directory containing ontology files
            
        Returns:
            Pipeline execution results
        """
        pipeline_results = {
            "step1_ingestion": {},
            "step2_management": {},
            "step3_validation": {},
            "step4_quality": {},
            "step5_storage": {},
            "overall_success": False,
            "total_entities_created": 0,
            "total_relationships_created": 0,
            "quality_score": 0.0,
            "errors": []
        }
        
        try:
            logger.info("Starting Ontology-to-KG pipeline")
            
            # Step 1: Ontology File Ingestion
            logger.info("Step 1: Ontology File Ingestion")
            ingestion_result = await self._step1_ontology_ingestion(ontology_directory)
            pipeline_results["step1_ingestion"] = ingestion_result
            
            if not ingestion_result["success"]:
                pipeline_results["errors"].append("Ontology ingestion failed")
                return pipeline_results
            
            # Step 2: Ontology Management
            logger.info("Step 2: Ontology Management")
            management_result = await self._step2_ontology_management()
            pipeline_results["step2_management"] = management_result
            
            if not management_result["success"]:
                pipeline_results["errors"].append("Ontology management failed")
                return pipeline_results
            
            # Step 3: SHACL Validation
            logger.info("Step 3: SHACL Validation")
            validation_result = await self._step3_shacl_validation()
            pipeline_results["step3_validation"] = validation_result
            
            if not validation_result["success"]:
                pipeline_results["errors"].append("SHACL validation failed")
                return pipeline_results
            
            # Step 4: Data Quality Check
            logger.info("Step 4: Data Quality Check")
            quality_result = await self._step4_data_quality_check()
            pipeline_results["step4_quality"] = quality_result
            pipeline_results["quality_score"] = quality_result.get("quality_score", 0.0)
            
            # Step 5: Knowledge Graph Storage
            logger.info("Step 5: Knowledge Graph Storage")
            storage_result = await self._step5_kg_storage()
            pipeline_results["step5_storage"] = storage_result
            pipeline_results["total_entities_created"] = storage_result.get("entities_created", 0)
            pipeline_results["total_relationships_created"] = storage_result.get("relationships_created", 0)
            
            pipeline_results["overall_success"] = True
            logger.info("Ontology-to-KG pipeline completed successfully")
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            pipeline_results["errors"].append(str(e))
        
        return pipeline_results
    
    async def _step1_ontology_ingestion(self, ontology_directory: str) -> Dict[str, Any]:
        """
        Step 1: TTL Ontology Files → Parsed RDF graph
        
        Args:
            ontology_directory: Directory containing ontology files
            
        Returns:
            Ingestion results
        """
        result = {
            "success": False,
            "files_loaded": 0,
            "total_triples": 0,
            "file_details": [],
            "errors": []
        }
        
        try:
            # Load ontology files using OntologyManager
            success = await self.ontology_manager.load_ontology_files(ontology_directory)
            
            if success:
                # Get the loaded graph from ontology manager
                self.rdf_graph = self.ontology_manager.graph
                result["total_triples"] = len(self.rdf_graph)
                
                # Count loaded files
                ontology_dir = Path(ontology_directory)
                if ontology_dir.exists():
                    for file_path in ontology_dir.rglob("*"):
                        if file_path.is_file() and file_path.suffix.lower() in ['.ttl', '.owl', '.rdf', '.xml', '.json', '.jsonld']:
                            result["files_loaded"] += 1
                            result["file_details"].append({
                                "file": str(file_path),
                                "size": file_path.stat().st_size,
                                "extension": file_path.suffix
                            })
                
                result["success"] = True
                logger.info(f"Step 1 completed: Loaded {result['files_loaded']} files with {result['total_triples']} triples")
            else:
                result["errors"].append("Failed to load ontology files")
                
        except Exception as e:
            logger.error(f"Step 1 failed: {e}")
            result["errors"].append(str(e))
        
        return result
    
    async def _step2_ontology_management(self) -> Dict[str, Any]:
        """
        Step 2: RDF graph → Ontology schema + SHACL constraints
        
        Returns:
            Management results
        """
        result = {
            "success": False,
            "classes_extracted": 0,
            "properties_extracted": 0,
            "shacl_constraints": 0,
            "ontology_schema": {},
            "errors": []
        }
        
        try:
            # Extract ontology schema
            schema = await self._extract_ontology_schema()
            result["ontology_schema"] = schema
            result["classes_extracted"] = len(schema.get("classes", []))
            result["properties_extracted"] = len(schema.get("properties", []))
            
            # Extract SHACL constraints
            shacl_constraints = await self._extract_shacl_constraints()
            result["shacl_constraints"] = len(shacl_constraints)
            
            # Store SHACL graph for validation
            self.shacl_graph = Graph()
            for constraint in shacl_constraints:
                # Add SHACL constraints to graph
                self.shacl_graph.add(constraint)
            
            result["success"] = True
            logger.info(f"Step 2 completed: Extracted {result['classes_extracted']} classes, {result['properties_extracted']} properties, {result['shacl_constraints']} constraints")
            
        except Exception as e:
            logger.error(f"Step 2 failed: {e}")
            result["errors"].append(str(e))
        
        return result
    
    async def _step3_shacl_validation(self) -> Dict[str, Any]:
        """
        Step 3: Extracted entities/relations → Ontology-validated RDF triples
        
        Returns:
            Validation results
        """
        result = {
            "success": False,
            "triples_validated": 0,
            "valid_triples": 0,
            "invalid_triples": 0,
            "validation_errors": [],
            "errors": []
        }
        
        try:
            # Extract entities and relationships from RDF graph
            entities = await self._extract_entities_from_rdf()
            relationships = await self._extract_relationships_from_rdf()
            
            # Validate using SHACL
            validated_data = []
            
            for entity in entities:
                validation_result = await self._validate_entity_with_shacl(entity)
                if validation_result["valid"]:
                    validated_data.append(entity)
                    result["valid_triples"] += 1
                else:
                    result["invalid_triples"] += 1
                    result["validation_errors"].extend(validation_result["errors"])
            
            for relationship in relationships:
                validation_result = await self._validate_relationship_with_shacl(relationship)
                if validation_result["valid"]:
                    validated_data.append(relationship)
                    result["valid_triples"] += 1
                else:
                    result["invalid_triples"] += 1
                    result["validation_errors"].extend(validation_result["errors"])
            
            result["triples_validated"] = len(entities) + len(relationships)
            self.validated_triples = validated_data
            
            result["success"] = result["valid_triples"] > 0
            logger.info(f"Step 3 completed: Validated {result['triples_validated']} triples, {result['valid_triples']} valid, {result['invalid_triples']} invalid")
            
        except Exception as e:
            logger.error(f"Step 3 failed: {e}")
            result["errors"].append(str(e))
        
        return result
    
    async def _step4_data_quality_check(self) -> Dict[str, Any]:
        """
        Step 4: Validated triples → High-quality data (optional compatibility checks)
        
        Returns:
            Quality check results
        """
        result = {
            "success": False,
            "quality_score": 0.0,
            "completeness": 0.0,
            "accuracy": 0.0,
            "consistency": 0.0,
            "quality_issues": [],
            "errors": []
        }
        
        try:
            if not self.validated_triples:
                result["errors"].append("No validated triples to check")
                return result
            
            # Perform data quality assessment
            quality_metrics = await self._assess_data_quality()
            
            result["completeness"] = quality_metrics.get("completeness", 0.0)
            result["accuracy"] = quality_metrics.get("accuracy", 0.0)
            result["consistency"] = quality_metrics.get("consistency", 0.0)
            
            # Calculate overall quality score
            result["quality_score"] = (
                result["completeness"] * 0.3 +
                result["accuracy"] * 0.4 +
                result["consistency"] * 0.3
            )
            
            # Perform compatibility checks
            compatibility_issues = await self._check_compatibility()
            result["quality_issues"].extend(compatibility_issues)
            
            result["success"] = result["quality_score"] >= 0.7  # Minimum quality threshold
            logger.info(f"Step 4 completed: Quality score {result['quality_score']:.2f}")
            
        except Exception as e:
            logger.error(f"Step 4 failed: {e}")
            result["errors"].append(str(e))
        
        return result
    
    async def _step5_kg_storage(self) -> Dict[str, Any]:
        """
        Step 5: Validated triples → Nodes/edges in Neo4j Knowledge Graph
        
        Returns:
            Storage results
        """
        result = {
            "success": False,
            "entities_created": 0,
            "relationships_created": 0,
            "storage_errors": [],
            "errors": []
        }
        
        try:
            if not self.validated_triples:
                result["errors"].append("No validated triples to store")
                return result
            
            # Convert RDF triples to Neo4j nodes and relationships
            kg_data = await self._convert_rdf_to_kg_format()
            
            # Create entities (nodes)
            for entity in kg_data["entities"]:
                try:
                    if entity["type"] == "HazardousSubstance":
                        storage_result = await self.kg_service.create_substance(entity["data"])
                    elif entity["type"] == "Container":
                        storage_result = await self.kg_service.create_container(entity["data"])
                    elif entity["type"] == "SafetyTest":
                        storage_result = await self.kg_service.create_test(entity["data"])
                    elif entity["type"] == "RiskAssessment":
                        storage_result = await self.kg_service.create_assessment(entity["data"])
                    
                    if storage_result.get("success"):
                        result["entities_created"] += 1
                    else:
                        result["storage_errors"].append(storage_result.get("message", "Unknown error"))
                        
                except Exception as e:
                    result["storage_errors"].append(f"Error creating entity: {str(e)}")
            
            # Create relationships (edges)
            for relationship in kg_data["relationships"]:
                try:
                    if relationship["type"] == "STORED_IN":
                        storage_result = await self.kg_service.create_storage_relationship(
                            relationship["source"], relationship["target"], relationship.get("properties", {})
                        )
                    elif relationship["type"] == "COMPATIBLE_WITH":
                        storage_result = await self.kg_service.create_compatibility_relationship(
                            relationship["source"], relationship["target"], 
                            relationship.get("compatible", True), relationship.get("notes", "")
                        )
                    
                    if storage_result.get("success"):
                        result["relationships_created"] += 1
                    else:
                        result["storage_errors"].append(storage_result.get("message", "Unknown error"))
                        
                except Exception as e:
                    result["storage_errors"].append(f"Error creating relationship: {str(e)}")
            
            result["success"] = result["entities_created"] > 0 or result["relationships_created"] > 0
            logger.info(f"Step 5 completed: Created {result['entities_created']} entities, {result['relationships_created']} relationships")
            
        except Exception as e:
            logger.error(f"Step 5 failed: {e}")
            result["errors"].append(str(e))
        
        return result
    
    async def _extract_ontology_schema(self) -> Dict[str, Any]:
        """Extract ontology schema from RDF graph."""
        schema = {
            "classes": [],
            "properties": [],
            "namespaces": {}
        }
        
        try:
            # Extract classes
            class_query = """
            SELECT DISTINCT ?class ?label ?comment
            WHERE {
                ?class a owl:Class .
                OPTIONAL { ?class rdfs:label ?label }
                OPTIONAL { ?class rdfs:comment ?comment }
            }
            """
            
            for row in self.rdf_graph.query(class_query):
                schema["classes"].append({
                    "uri": str(row[0]),
                    "label": str(row[1]) if row[1] else "",
                    "comment": str(row[2]) if row[2] else ""
                })
            
            # Extract properties
            property_query = """
            SELECT DISTINCT ?property ?label ?comment ?domain ?range
            WHERE {
                ?property a ?propertyType .
                FILTER(?propertyType IN (owl:ObjectProperty, owl:DatatypeProperty, rdf:Property))
                OPTIONAL { ?property rdfs:label ?label }
                OPTIONAL { ?property rdfs:comment ?comment }
                OPTIONAL { ?property rdfs:domain ?domain }
                OPTIONAL { ?property rdfs:range ?range }
            }
            """
            
            for row in self.rdf_graph.query(property_query):
                schema["properties"].append({
                    "uri": str(row[0]),
                    "label": str(row[1]) if row[1] else "",
                    "comment": str(row[2]) if row[2] else "",
                    "domain": str(row[3]) if row[3] else "",
                    "range": str(row[4]) if row[4] else ""
                })
            
            # Extract namespaces
            for prefix, namespace in self.rdf_graph.namespaces():
                schema["namespaces"][prefix] = str(namespace)
                
        except Exception as e:
            logger.error(f"Error extracting ontology schema: {e}")
        
        return schema
    
    async def _extract_shacl_constraints(self) -> List[Tuple]:
        """Extract SHACL constraints from RDF graph."""
        constraints = []
        
        try:
            # Look for SHACL shapes in the graph
            shacl_query = """
            SELECT DISTINCT ?shape ?targetClass ?property ?constraint
            WHERE {
                ?shape a sh:NodeShape .
                OPTIONAL { ?shape sh:targetClass ?targetClass }
                OPTIONAL { 
                    ?shape sh:property ?propertyShape .
                    ?propertyShape sh:path ?property .
                    ?propertyShape ?constraintType ?constraint .
                }
            }
            """
            
            for row in self.rdf_graph.query(shacl_query):
                constraints.append(row)
                
        except Exception as e:
            logger.error(f"Error extracting SHACL constraints: {e}")
        
        return constraints
    
    async def _extract_entities_from_rdf(self) -> List[Dict[str, Any]]:
        """Extract entities from RDF graph."""
        entities = []
        
        try:
            # Extract substance entities
            substance_query = """
            SELECT DISTINCT ?substance ?name ?formula ?hazard_class
            WHERE {
                ?substance a hs:HazardousSubstance .
                OPTIONAL { ?substance hs:name ?name }
                OPTIONAL { ?substance hs:chemicalFormula ?formula }
                OPTIONAL { ?substance hs:hazardClass ?hazard_class }
            }
            """
            
            for row in self.rdf_graph.query(substance_query):
                entities.append({
                    "type": "HazardousSubstance",
                    "uri": str(row[0]),
                    "data": {
                        "name": str(row[1]) if row[1] else "",
                        "chemical_formula": str(row[2]) if row[2] else "",
                        "hazard_class": str(row[3]) if row[3] else ""
                    }
                })
            
            # Extract container entities
            container_query = """
            SELECT DISTINCT ?container ?name ?material ?capacity
            WHERE {
                ?container a hs:Container .
                OPTIONAL { ?container hs:name ?name }
                OPTIONAL { ?container hs:material ?material }
                OPTIONAL { ?container hs:capacity ?capacity }
            }
            """
            
            for row in self.rdf_graph.query(container_query):
                entities.append({
                    "type": "Container",
                    "uri": str(row[0]),
                    "data": {
                        "name": str(row[1]) if row[1] else "",
                        "material": str(row[2]) if row[2] else "",
                        "capacity": float(row[3]) if row[3] else 0.0
                    }
                })
                
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
        
        return entities
    
    async def _extract_relationships_from_rdf(self) -> List[Dict[str, Any]]:
        """Extract relationships from RDF graph."""
        relationships = []
        
        try:
            # Extract storage relationships
            storage_query = """
            SELECT DISTINCT ?substance ?container ?quantity
            WHERE {
                ?substance hs:storedIn ?container .
                OPTIONAL { ?substance hs:quantity ?quantity }
            }
            """
            
            for row in self.rdf_graph.query(storage_query):
                relationships.append({
                    "type": "STORED_IN",
                    "source": str(row[0]),
                    "target": str(row[1]),
                    "properties": {
                        "quantity": float(row[2]) if row[2] else 1.0
                    }
                })
            
            # Extract compatibility relationships
            compatibility_query = """
            SELECT DISTINCT ?substance1 ?substance2 ?compatible
            WHERE {
                ?substance1 hs:compatibleWith ?substance2 .
                OPTIONAL { ?substance1 hs:compatibilityStatus ?compatible }
            }
            """
            
            for row in self.rdf_graph.query(compatibility_query):
                relationships.append({
                    "type": "COMPATIBLE_WITH",
                    "source": str(row[0]),
                    "target": str(row[1]),
                    "compatible": bool(row[2]) if row[2] else True
                })
                
        except Exception as e:
            logger.error(f"Error extracting relationships: {e}")
        
        return relationships
    
    async def _validate_entity_with_shacl(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Validate entity using SHACL constraints."""
        result = {
            "valid": True,
            "errors": []
        }
        
        try:
            # Create a temporary graph for validation
            temp_graph = Graph()
            temp_graph.bind("hs", self.hs_namespace)
            
            # Add entity to temp graph
            entity_uri = URIRef(entity["uri"])
            entity_type = URIRef(f"{self.hs_namespace}{entity['type']}")
            temp_graph.add((entity_uri, RDF.type, entity_type))
            
            # Add entity properties
            for key, value in entity["data"].items():
                if value:
                    property_uri = URIRef(f"{self.hs_namespace}{key}")
                    temp_graph.add((entity_uri, property_uri, Literal(value)))
            
            # Validate against SHACL
            if len(self.shacl_graph) > 0:
                validation_result = validate(temp_graph, shacl_graph=self.shacl_graph)
                if not validation_result[0]:
                    result["valid"] = False
                    result["errors"].append("SHACL validation failed")
            
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Validation error: {str(e)}")
        
        return result
    
    async def _validate_relationship_with_shacl(self, relationship: Dict[str, Any]) -> Dict[str, Any]:
        """Validate relationship using SHACL constraints."""
        result = {
            "valid": True,
            "errors": []
        }
        
        try:
            # Basic relationship validation
            if not relationship.get("source") or not relationship.get("target"):
                result["valid"] = False
                result["errors"].append("Missing source or target")
            
            if not relationship.get("type"):
                result["valid"] = False
                result["errors"].append("Missing relationship type")
            
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Validation error: {str(e)}")
        
        return result
    
    async def _assess_data_quality(self) -> Dict[str, float]:
        """Assess data quality of validated triples."""
        metrics = {
            "completeness": 0.0,
            "accuracy": 0.0,
            "consistency": 0.0
        }
        
        try:
            if not self.validated_triples:
                return metrics
            
            total_triples = len(self.validated_triples)
            complete_triples = 0
            accurate_triples = 0
            consistent_triples = 0
            
            for triple in self.validated_triples:
                # Check completeness
                if triple.get("data") and all(triple["data"].values()):
                    complete_triples += 1
                
                # Check accuracy (basic checks)
                if triple.get("type") in ["HazardousSubstance", "Container"]:
                    accurate_triples += 1
                
                # Check consistency
                if triple.get("uri") and triple.get("type"):
                    consistent_triples += 1
            
            metrics["completeness"] = complete_triples / total_triples if total_triples > 0 else 0.0
            metrics["accuracy"] = accurate_triples / total_triples if total_triples > 0 else 0.0
            metrics["consistency"] = consistent_triples / total_triples if total_triples > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error assessing data quality: {e}")
        
        return metrics
    
    async def _check_compatibility(self) -> List[str]:
        """Check chemical compatibility issues."""
        issues = []
        
        try:
            substances = [t for t in self.validated_triples if t.get("type") == "HazardousSubstance"]
            containers = [t for t in self.validated_triples if t.get("type") == "Container"]
            
            # Check for incompatible substance-container combinations
            for substance in substances:
                for container in containers:
                    substance_data = substance.get("data", {})
                    container_data = container.get("data", {})
                    
                    if (substance_data.get("hazard_class") == "corrosive" and 
                        container_data.get("material") in ["aluminum", "carbon_steel"]):
                        issues.append(f"Incompatible: {substance_data.get('name')} (corrosive) with {container_data.get('material')} container")
            
        except Exception as e:
            logger.error(f"Error checking compatibility: {e}")
        
        return issues
    
    async def _convert_rdf_to_kg_format(self) -> Dict[str, Any]:
        """Convert RDF triples to Neo4j knowledge graph format."""
        kg_data = {
            "entities": [],
            "relationships": []
        }
        
        try:
            for triple in self.validated_triples:
                if triple.get("type") in ["HazardousSubstance", "Container", "SafetyTest", "RiskAssessment"]:
                    # Convert to entity
                    entity_data = triple.get("data", {}).copy()
                    entity_data["id"] = str(uuid.uuid4())  # Generate unique ID
                    entity_data["created_at"] = datetime.now().isoformat()
                    entity_data["updated_at"] = datetime.now().isoformat()
                    
                    kg_data["entities"].append({
                        "type": triple["type"],
                        "data": entity_data
                    })
                
                elif triple.get("type") in ["STORED_IN", "COMPATIBLE_WITH"]:
                    # Convert to relationship
                    kg_data["relationships"].append({
                        "type": triple["type"],
                        "source": triple["source"],
                        "target": triple["target"],
                        "properties": triple.get("properties", {}),
                        "compatible": triple.get("compatible", True),
                        "notes": triple.get("notes", "")
                    })
            
        except Exception as e:
            logger.error(f"Error converting RDF to KG format: {e}")
        
        return kg_data

# Convenience function for running the pipeline
async def run_ontology_to_kg_pipeline(ontology_directory: str = "data/ontology") -> Dict[str, Any]:
    """
    Convenience function to run the complete ontology-to-KG pipeline.
    
    Args:
        ontology_directory: Directory containing ontology files
        
    Returns:
        Pipeline execution results
    """
    pipeline = OntologyToKGPipeline()
    
    try:
        await pipeline.initialize()
        results = await pipeline.run_pipeline(ontology_directory)
        return results
    finally:
        await pipeline.close() 