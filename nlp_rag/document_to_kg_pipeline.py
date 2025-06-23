# nlp_rag/document_to_kg_pipeline.py
"""
Document to Knowledge Graph Pipeline

Coordinates the complete pipeline from document ingestion to knowledge graph storage.
Integrates all nlp_rag components for processing PDFs, Word documents, and images.
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import asyncio
import uuid
from datetime import datetime

# Import existing nlp_rag components
from .processors.document_processor import DocumentProcessor
from .processors.vector_store import VectorStore
from .information_extraction.entity_extractor import EntityExtractor
from .information_extraction.relationship_extractor import RelationshipExtractor
from .information_extraction.text_processor import TextProcessor

# Import KG components
from kg.services import KnowledgeGraphService
from kg.models import HazardousSubstance, Container, SafetyTest, RiskAssessment, Location, RelationshipType

# Import validation components
from validation.rules import ValidationRules

logger = logging.getLogger(__name__)

class DocumentToKGPipeline:
    """Complete pipeline from document ingestion to knowledge graph storage."""
    
    def __init__(self):
        """Initialize all pipeline components."""
        self.document_processor = DocumentProcessor()
        self.entity_extractor = EntityExtractor()
        self.relationship_extractor = RelationshipExtractor()
        self.text_processor = TextProcessor()
        self.vector_store = VectorStore()
        self.kg_service = KnowledgeGraphService()
        self.validation_rules = ValidationRules()
        
        # Document type classifiers
        self.document_classifiers = {
            "safety": ["safety", "hazard", "risk", "danger", "toxic", "corrosive", "flammable"],
            "engineering": ["engineering", "technical", "specification", "design", "process"],
            "regulatory": ["regulation", "compliance", "standard", "requirement", "law"],
            "research": ["research", "study", "analysis", "experiment", "investigation"]
        }
    
    async def initialize(self):
        """Initialize all pipeline components."""
        await self.kg_service.initialize()
        await self.vector_store.initialize()
        logger.info("Document-to-KG pipeline initialized")
    
    async def close(self):
        """Close all pipeline connections."""
        await self.kg_service.close()
        logger.info("Document-to-KG pipeline closed")
    
    async def process_document_to_kg(self, file_path: str, doc_type: str = "auto") -> Dict[str, Any]:
        """
        Complete pipeline: Document → KG
        
        Args:
            file_path: Path to the document
            doc_type: Document type (auto, safety, engineering, regulatory, research)
            
        Returns:
            Processing results with KG entities created
        """
        try:
            logger.info(f"Starting document-to-KG pipeline for: {file_path}")
            
            # Step 1: Document Ingestion and Text Extraction
            ingestion_result = await self._ingest_document(file_path, doc_type)
            if not ingestion_result["success"]:
                return ingestion_result
            
            document_data = ingestion_result["document"]
            
            # Step 2: Content Classification (if auto)
            if doc_type == "auto":
                doc_type = self._classify_document(document_data["content"]["text"])
                document_data["doc_type"] = doc_type
            
            # Step 3: Entity Recognition
            entity_result = await self._extract_entities(document_data)
            if not entity_result["success"]:
                return entity_result
            
            # Step 4: Relationship Extraction
            relationship_result = await self._extract_relationships(document_data, entity_result["entities"])
            if not relationship_result["success"]:
                return relationship_result
            
            # Step 5: Text Chunking and Vector Embeddings
            vector_result = await self._create_vector_embeddings(document_data)
            if not vector_result["success"]:
                return vector_result
            
            # Step 6: Ontology Validation
            validation_result = await self._validate_entities(entity_result["entities"])
            if not validation_result["success"]:
                return validation_result
            
            # Step 7: Knowledge Graph Storage
            kg_result = await self._store_in_knowledge_graph(
                document_data, 
                entity_result["entities"], 
                relationship_result["relationships"]
            )
            
            return {
                "success": True,
                "pipeline_results": {
                    "ingestion": ingestion_result,
                    "entity_extraction": entity_result,
                    "relationship_extraction": relationship_result,
                    "vector_embeddings": vector_result,
                    "ontology_validation": validation_result,
                    "knowledge_graph": kg_result
                },
                "summary": {
                    "document_id": document_data["document_id"],
                    "doc_type": doc_type,
                    "entities_extracted": len(entity_result["entities"]),
                    "relationships_extracted": len(relationship_result["relationships"]),
                    "kg_nodes_created": kg_result.get("nodes_created", 0),
                    "kg_relationships_created": kg_result.get("relationships_created", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in document-to-KG pipeline: {e}")
            return {
                "success": False,
                "error": f"Pipeline error: {str(e)}"
            }
    
    async def _ingest_document(self, file_path: str, doc_type: str) -> Dict[str, Any]:
        """Step 1: Document ingestion and text extraction."""
        try:
            result = self.document_processor.process_document(file_path, doc_type)
            
            if result["success"]:
                # Add document ID and metadata
                document_data = result["document"]
                document_data["document_id"] = str(uuid.uuid4())
                document_data["processing_date"] = datetime.now().isoformat()
                
                logger.info(f"Document ingested: {document_data['document_id']}")
                return {"success": True, "document": document_data}
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error in document ingestion: {e}")
            return {"success": False, "error": str(e)}
    
    def _classify_document(self, text: str) -> str:
        """Classify document type based on content."""
        text_lower = text.lower()
        
        scores = {}
        for doc_type, keywords in self.document_classifiers.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[doc_type] = score
        
        # Return the document type with highest score, default to "general"
        if scores:
            best_type = max(scores, key=scores.get)
            return best_type if scores[best_type] > 0 else "general"
        return "general"
    
    async def _extract_entities(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3: Extract entities from document text."""
        try:
            text = document_data["content"]["text"]
            
            # Extract entities using the entity extractor
            entities = self.entity_extractor.extract_entities(text)
            
            # Extract chemical compounds specifically
            chemical_compounds = self.entity_extractor.extract_chemical_compounds(text)
            
            # Extract safety information
            safety_info = self.entity_extractor.extract_safety_information(text)
            
            # Process entities for KG storage
            processed_entities = []
            for entity in entities:
                processed_entity = {
                    "text": entity.text,
                    "entity_type": entity.entity_type,
                    "confidence": entity.confidence,
                    "properties": entity.properties,
                    "document_id": document_data["document_id"],
                    "source_text": text[entity.start_pos:entity.end_pos + 50]  # Context
                }
                processed_entities.append(processed_entity)
            
            logger.info(f"Extracted {len(processed_entities)} entities from document")
            
            return {
                "success": True,
                "entities": processed_entities,
                "chemical_compounds": chemical_compounds,
                "safety_info": safety_info
            }
            
        except Exception as e:
            logger.error(f"Error in entity extraction: {e}")
            return {"success": False, "error": str(e)}
    
    async def _extract_relationships(self, document_data: Dict[str, Any], entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Step 4: Extract relationships between entities."""
        try:
            text = document_data["content"]["text"]
            
            # Extract relationships using the relationship extractor
            relationships = self.relationship_extractor.extract_relationships(text, entities)
            
            # Process relationships for KG storage
            processed_relationships = []
            for rel in relationships:
                processed_rel = {
                    "source_entity": rel["source"],
                    "target_entity": rel["target"],
                    "relationship_type": rel["type"],
                    "confidence": rel.get("confidence", 0.8),
                    "properties": rel.get("properties", {}),
                    "document_id": document_data["document_id"]
                }
                processed_relationships.append(processed_rel)
            
            logger.info(f"Extracted {len(processed_relationships)} relationships from document")
            
            return {
                "success": True,
                "relationships": processed_relationships
            }
            
        except Exception as e:
            logger.error(f"Error in relationship extraction: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_vector_embeddings(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Step 5: Create vector embeddings for semantic search."""
        try:
            text = document_data["content"]["text"]
            document_id = document_data["document_id"]
            
            # Process text
            processed_text = self.text_processor.preprocess_text(text)
            
            # Create chunks for embedding
            chunks = self.text_processor.create_chunks(processed_text, chunk_size=1000, overlap=200)
            
            # Store in vector database
            for i, chunk in enumerate(chunks):
                chunk_id = f"{document_id}_chunk_{i}"
                await self.vector_store.add_document(
                    document_id=chunk_id,
                    text=chunk,
                    metadata={
                        "document_id": document_id,
                        "chunk_index": i,
                        "doc_type": document_data.get("doc_type", "general")
                    }
                )
            
            logger.info(f"Created vector embeddings for {len(chunks)} chunks")
            
            return {
                "success": True,
                "chunks_created": len(chunks),
                "document_id": document_id
            }
            
        except Exception as e:
            logger.error(f"Error in vector embedding creation: {e}")
            return {"success": False, "error": str(e)}
    
    async def _validate_entities(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Step 6: Validate entities against ontology rules."""
        try:
            validation_results = {
                "valid_entities": [],
                "invalid_entities": [],
                "warnings": []
            }
            
            for entity in entities:
                # Validate chemical names
                if entity["entity_type"].startswith("chemical"):
                    if not self.validation_rules.is_valid_chemical_name(entity["text"]):
                        validation_results["invalid_entities"].append({
                            "entity": entity,
                            "reason": "Invalid chemical name format"
                        })
                        continue
                
                # Validate hazard classes
                if entity["entity_type"].startswith("hazard"):
                    if not self.validation_rules.is_valid_hazard_class(entity["text"]):
                        validation_results["warnings"].append({
                            "entity": entity,
                            "reason": "Unknown hazard class"
                        })
                
                # Validate CAS numbers
                if "cas_number" in entity["entity_type"]:
                    if not self.validation_rules.is_valid_cas_number(entity["text"]):
                        validation_results["invalid_entities"].append({
                            "entity": entity,
                            "reason": "Invalid CAS number format"
                        })
                        continue
                
                validation_results["valid_entities"].append(entity)
            
            logger.info(f"Validated {len(entities)} entities: {len(validation_results['valid_entities'])} valid, {len(validation_results['invalid_entities'])} invalid")
            
            return {
                "success": True,
                "validation_results": validation_results
            }
            
        except Exception as e:
            logger.error(f"Error in entity validation: {e}")
            return {"success": False, "error": str(e)}
    
    async def _store_in_knowledge_graph(self, document_data: Dict[str, Any], 
                                      entities: List[Dict[str, Any]], 
                                      relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Step 7: Store entities and relationships in the knowledge graph."""
        try:
            nodes_created = 0
            relationships_created = 0
            errors = []
            
            # Create nodes for entities
            entity_nodes = {}
            for entity in entities:
                try:
                    if entity["entity_type"].startswith("chemical"):
                        # Create HazardousSubstance node
                        substance_data = {
                            "name": entity["text"],
                            "chemical_formula": entity.get("properties", {}).get("formula", ""),
                            "hazard_class": entity.get("properties", {}).get("hazard_class", ""),
                            "description": entity.get("source_text", "")[:200],
                            "source_document": document_data["document_id"]
                        }
                        
                        result = await self.kg_service.create_substance(substance_data)
                        if result["success"]:
                            entity_nodes[entity["text"]] = result["substance_id"]
                            nodes_created += 1
                        else:
                            errors.append(f"Failed to create substance node: {result['message']}")
                    
                    elif entity["entity_type"].startswith("hazard"):
                        # Create hazard class node (if not exists)
                        if entity["text"] not in entity_nodes:
                            # For now, just track hazard classes
                            entity_nodes[entity["text"]] = f"hazard_{entity['text']}"
                    
                except Exception as e:
                    errors.append(f"Error creating node for entity {entity['text']}: {str(e)}")
            
            # Create relationships
            for rel in relationships:
                try:
                    source_id = entity_nodes.get(rel["source_entity"])
                    target_id = entity_nodes.get(rel["target_entity"])
                    
                    if source_id and target_id:
                        if rel["relationship_type"] == "HAS_HAZARD_CLASS":
                            # Create relationship between substance and hazard
                            result = await self.kg_service.create_relationship(
                                source_id, target_id, "HAS_HAZARD_CLASS", 
                                {"source_document": document_data["document_id"]}
                            )
                            if result:
                                relationships_created += 1
                        
                        elif rel["relationship_type"] == "STORED_IN":
                            # Create storage relationship
                            result = await self.kg_service.create_storage_relationship(
                                source_id, target_id, rel.get("properties", {}).get("quantity", 1.0)
                            )
                            if result["success"]:
                                relationships_created += 1
                
                except Exception as e:
                    errors.append(f"Error creating relationship: {str(e)}")
            
            logger.info(f"Created {nodes_created} nodes and {relationships_created} relationships in KG")
            
            return {
                "success": True,
                "nodes_created": nodes_created,
                "relationships_created": relationships_created,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Error storing in knowledge graph: {e}")
            return {"success": False, "error": str(e)}
    
    async def batch_process_documents(self, file_paths: List[str], doc_type: str = "auto") -> Dict[str, Any]:
        """Process multiple documents in batch."""
        results = {
            "successful": 0,
            "failed": 0,
            "documents": [],
            "errors": []
        }
        
        for file_path in file_paths:
            try:
                result = await self.process_document_to_kg(file_path, doc_type)
                if result["success"]:
                    results["successful"] += 1
                    results["documents"].append(result)
                else:
                    results["failed"] += 1
                    results["errors"].append({
                        "file_path": file_path,
                        "error": result.get("error", "Unknown error")
                    })
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "file_path": file_path,
                    "error": str(e)
                })
        
        return results

# Global pipeline instance
document_pipeline = DocumentToKGPipeline()

async def init_document_pipeline():
    """Initialize the global document pipeline."""
    await document_pipeline.initialize()

async def close_document_pipeline():
    """Close the global document pipeline."""
    await document_pipeline.close() 