"""
Hazardous Substances Data Ingestion Pipeline

This module handles the ingestion of safety-relevant technical documents
and data related to hazardous substances, containers, and safety protocols.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import pandas as pd
import json
import csv
from datetime import datetime
import hashlib
import uuid

# Import core modules
from kg.neo4j.database import Neo4jDatabase
from ontology.src.manager import OntologyManager
from rag.vector_store import VectorStore
from validation.rules import ValidationEngine

logger = logging.getLogger(__name__)

class HazardousDataIngestion:
    """Main ingestion pipeline for hazardous substances data."""
    
    def __init__(self):
        self.neo4j_db = Neo4jDatabase()
        self.ontology_manager = OntologyManager()
        self.vector_store = VectorStore()
        self.validation_engine = ValidationEngine()
        
    async def initialize(self):
        """Initialize all components."""
        await self.neo4j_db.connect()
        await self.ontology_manager.load_ontology_files()
        await self.vector_store.initialize()
        
    async def close(self):
        """Close all connections."""
        await self.neo4j_db.disconnect()
        
    async def ingest_csv_data(self, file_path: str, data_type: str) -> Dict[str, Any]:
        """Ingest CSV data for hazardous substances, containers, or tests."""
        try:
            logger.info(f"Ingesting CSV data from {file_path} for type: {data_type}")
            
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Validate data structure
            validation_result = await self.validation_engine.validate_csv_structure(
                df, data_type
            )
            
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "errors": validation_result["errors"],
                    "message": "Data validation failed"
                }
            
            # Process data based on type
            if data_type == "substances":
                return await self._ingest_substances(df)
            elif data_type == "containers":
                return await self._ingest_containers(df)
            elif data_type == "tests":
                return await self._ingest_tests(df)
            elif data_type == "assessments":
                return await self._ingest_assessments(df)
            else:
                return {
                    "success": False,
                    "message": f"Unknown data type: {data_type}"
                }
                
        except Exception as e:
            logger.error(f"Error ingesting CSV data: {e}")
            return {
                "success": False,
                "message": f"Error ingesting data: {str(e)}"
            }
    
    async def _ingest_substances(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Ingest hazardous substances data."""
        try:
            ingested_count = 0
            errors = []
            
            for _, row in df.iterrows():
                try:
                    # Create substance node
                    substance_data = {
                        "id": row.get("id", str(uuid.uuid4())),
                        "name": row["name"],
                        "chemical_formula": row.get("chemical_formula", ""),
                        "molecular_weight": float(row.get("molecular_weight", 0)),
                        "hazard_class": row.get("hazard_class", ""),
                        "flash_point": row.get("flash_point", ""),
                        "boiling_point": float(row.get("boiling_point", 0)),
                        "melting_point": float(row.get("melting_point", 0)),
                        "density": float(row.get("density", 0)),
                        "description": row.get("description", ""),
                        "created_at": datetime.now().isoformat()
                    }
                    
                    # Validate against ontology
                    validation = await self.ontology_manager.validate_substance(substance_data)
                    if not validation["valid"]:
                        errors.append(f"Substance {row['name']}: {validation['errors']}")
                        continue
                    
                    # Add to Neo4j
                    node_id = await self.neo4j_db.create_node(
                        ["HazardousSubstance"], substance_data
                    )
                    
                    if node_id:
                        ingested_count += 1
                        logger.info(f"Ingested substance: {row['name']}")
                    
                except Exception as e:
                    errors.append(f"Error processing substance {row.get('name', 'Unknown')}: {e}")
            
            return {
                "success": True,
                "ingested_count": ingested_count,
                "errors": errors,
                "message": f"Successfully ingested {ingested_count} substances"
            }
            
        except Exception as e:
            logger.error(f"Error in substance ingestion: {e}")
            return {
                "success": False,
                "message": f"Error ingesting substances: {str(e)}"
            }
    
    async def _ingest_containers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Ingest container data."""
        try:
            ingested_count = 0
            errors = []
            
            for _, row in df.iterrows():
                try:
                    container_data = {
                        "id": row.get("id", str(uuid.uuid4())),
                        "name": row["name"],
                        "material": row.get("material", ""),
                        "capacity": float(row.get("capacity", 0)),
                        "unit": row.get("unit", "L"),
                        "pressure_rating": float(row.get("pressure_rating", 0)),
                        "temperature_rating": float(row.get("temperature_rating", 0)),
                        "manufacturer": row.get("manufacturer", ""),
                        "model": row.get("model", ""),
                        "created_at": datetime.now().isoformat()
                    }
                    
                    # Add to Neo4j
                    node_id = await self.neo4j_db.create_node(
                        ["Container"], container_data
                    )
                    
                    if node_id:
                        ingested_count += 1
                        logger.info(f"Ingested container: {row['name']}")
                    
                except Exception as e:
                    errors.append(f"Error processing container {row.get('name', 'Unknown')}: {e}")
            
            return {
                "success": True,
                "ingested_count": ingested_count,
                "errors": errors,
                "message": f"Successfully ingested {ingested_count} containers"
            }
            
        except Exception as e:
            logger.error(f"Error in container ingestion: {e}")
            return {
                "success": False,
                "message": f"Error ingesting containers: {str(e)}"
            }
    
    async def _ingest_tests(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Ingest safety test data."""
        try:
            ingested_count = 0
            errors = []
            
            for _, row in df.iterrows():
                try:
                    test_data = {
                        "id": row.get("id", str(uuid.uuid4())),
                        "name": row["name"],
                        "test_type": row.get("test_type", ""),
                        "description": row.get("description", ""),
                        "standard": row.get("standard", ""),
                        "method": row.get("method", ""),
                        "duration": float(row.get("duration", 0)),
                        "temperature": float(row.get("temperature", 0)),
                        "pressure": float(row.get("pressure", 0)),
                        "created_at": datetime.now().isoformat()
                    }
                    
                    # Add to Neo4j
                    node_id = await self.neo4j_db.create_node(
                        ["SafetyTest"], test_data
                    )
                    
                    if node_id:
                        ingested_count += 1
                        logger.info(f"Ingested test: {row['name']}")
                    
                except Exception as e:
                    errors.append(f"Error processing test {row.get('name', 'Unknown')}: {e}")
            
            return {
                "success": True,
                "ingested_count": ingested_count,
                "errors": errors,
                "message": f"Successfully ingested {ingested_count} tests"
            }
            
        except Exception as e:
            logger.error(f"Error in test ingestion: {e}")
            return {
                "success": False,
                "message": f"Error ingesting tests: {str(e)}"
            }
    
    async def _ingest_assessments(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Ingest risk assessment data."""
        try:
            ingested_count = 0
            errors = []
            
            for _, row in df.iterrows():
                try:
                    assessment_data = {
                        "id": row.get("id", str(uuid.uuid4())),
                        "title": row["title"],
                        "substance_id": row.get("substance_id", ""),
                        "risk_level": row.get("risk_level", ""),
                        "hazards": row.get("hazards", ""),
                        "mitigation": row.get("mitigation", ""),
                        "ppe_required": row.get("ppe_required", ""),
                        "storage_requirements": row.get("storage_requirements", ""),
                        "emergency_procedures": row.get("emergency_procedures", ""),
                        "assessor": row.get("assessor", ""),
                        "date": row.get("date", datetime.now().isoformat()),
                        "created_at": datetime.now().isoformat()
                    }
                    
                    # Add to Neo4j
                    node_id = await self.neo4j_db.create_node(
                        ["RiskAssessment"], assessment_data
                    )
                    
                    if node_id:
                        ingested_count += 1
                        logger.info(f"Ingested assessment: {row['title']}")
                    
                except Exception as e:
                    errors.append(f"Error processing assessment {row.get('title', 'Unknown')}: {e}")
            
            return {
                "success": True,
                "ingested_count": ingested_count,
                "errors": errors,
                "message": f"Successfully ingested {ingested_count} assessments"
            }
            
        except Exception as e:
            logger.error(f"Error in assessment ingestion: {e}")
            return {
                "success": False,
                "message": f"Error ingesting assessments: {str(e)}"
            }
    
    async def ingest_documents(self, file_path: str, doc_type: str) -> Dict[str, Any]:
        """Ingest documents for RAG system."""
        try:
            logger.info(f"Ingesting document: {file_path} of type: {doc_type}")
            
            # Read and process document
            document_data = await self._process_document(file_path, doc_type)
            
            if not document_data:
                return {
                    "success": False,
                    "message": "Failed to process document"
                }
            
            # Add to vector store
            success = await self.vector_store.add_documents([document_data])
            
            if success:
                return {
                    "success": True,
                    "document_id": document_data["id"],
                    "message": "Document ingested successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to add document to vector store"
                }
                
        except Exception as e:
            logger.error(f"Error ingesting document: {e}")
            return {
                "success": False,
                "message": f"Error ingesting document: {str(e)}"
            }
    
    async def _process_document(self, file_path: str, doc_type: str) -> Optional[Dict[str, Any]]:
        """Process document and extract text content."""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            # Generate document ID
            doc_id = str(uuid.uuid4())
            
            # Read file content based on type
            if file_path.suffix.lower() == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
                content = df.to_string()
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    content = json.dumps(data, indent=2)
            else:
                # For other formats, try to read as text
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Create document data
            document_data = {
                "id": doc_id,
                "text": content,
                "source": str(file_path),
                "type": doc_type,
                "created_at": datetime.now().isoformat(),
                "file_size": file_path.stat().st_size,
                "file_type": file_path.suffix.lower()
            }
            
            return document_data
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            return None
    
    async def create_relationships(self, relationship_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create relationships between entities in the knowledge graph."""
        try:
            relationship_type = relationship_data["type"]
            source_id = relationship_data["source_id"]
            target_id = relationship_data["target_id"]
            properties = relationship_data.get("properties", {})
            
            # Add to Neo4j
            success = await self.neo4j_db.create_relationship(
                source_id, target_id, relationship_type, properties
            )
            
            if success:
                return {
                    "success": True,
                    "message": f"Relationship {relationship_type} created successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to create relationship"
                }
                
        except Exception as e:
            logger.error(f"Error creating relationship: {e}")
            return {
                "success": False,
                "message": f"Error creating relationship: {str(e)}"
            }
    
    async def get_ingestion_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics."""
        try:
            # Get database stats
            db_stats = await self.neo4j_db.get_graph_stats()
            
            # Get vector store stats
            vs_stats = await self.vector_store.get_stats()
            
            return {
                "database": db_stats,
                "vector_store": vs_stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting ingestion stats: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global ingestion instance
ingestion_pipeline = HazardousDataIngestion()

async def init_ingestion():
    """Initialize the ingestion pipeline."""
    await ingestion_pipeline.initialize()

async def close_ingestion():
    """Close the ingestion pipeline."""
    await ingestion_pipeline.close()
