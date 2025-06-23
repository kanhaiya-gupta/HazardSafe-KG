#!/usr/bin/env python3
"""
Test script for NLP & RAG Pipeline
Tests document processing, entity extraction, and knowledge graph population
"""

import asyncio
import argparse
import sys
import os
import logging
from pathlib import Path
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from nlp_rag.document_to_kg_pipeline import DocumentToKGPipeline
from nlp_rag.processors.document_processor import DocumentProcessor
from nlp_rag.information_extraction.entity_extractor import EntityExtractor
from nlp_rag.information_extraction.relationship_extractor import RelationshipExtractor
from kg.services import KnowledgeGraphService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NLP_RAGPipelineTester:
    def __init__(self):
        self.pipeline = DocumentToKGPipeline()
        self.document_processor = DocumentProcessor()
        self.entity_extractor = EntityExtractor()
        self.relationship_extractor = RelationshipExtractor()
        self.kg_service = KnowledgeGraphService()
        
    async def initialize(self):
        """Initialize the pipeline"""
        try:
            await self.pipeline.initialize()
            logger.info("✅ Pipeline initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Pipeline initialization failed: {e}")
            return False
    
    async def test_document_processing(self, document_path, doc_type="safety"):
        """Test document processing"""
        logger.info(f"Testing Document Processing: {document_path}")
        
        try:
            # Process document
            result = await self.pipeline.process_document_to_kg(document_path, doc_type)
            
            if result["success"]:
                logger.info(f"✅ Document processing successful")
                logger.info(f"Extracted text length: {len(result.get('text', ''))}")
                logger.info(f"Entities found: {len(result.get('entities', []))}")
                logger.info(f"Relationships found: {len(result.get('relationships', []))}")
                
                return result
            else:
                logger.error(f"❌ Document processing failed: {result.get('error', 'Unknown error')}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Document processing error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_entity_extraction(self, text):
        """Test entity extraction from text"""
        logger.info("Testing Entity Extraction...")
        
        try:
            # Extract chemical compounds
            chemical_compounds = self.entity_extractor.extract_chemical_compounds(text)
            
            # Extract hazard entities
            hazard_entities = self.entity_extractor.extract_hazard_entities(text)
            
            # Extract property entities
            property_entities = self.entity_extractor.extract_property_entities(text)
            
            # Extract safety entities
            safety_entities = self.entity_extractor.extract_safety_entities(text)
            
            total_entities = len(chemical_compounds) + len(hazard_entities) + len(property_entities) + len(safety_entities)
            
            logger.info(f"✅ Entity extraction completed")
            logger.info(f"Chemical compounds: {len(chemical_compounds)}")
            logger.info(f"Hazard entities: {len(hazard_entities)}")
            logger.info(f"Property entities: {len(property_entities)}")
            logger.info(f"Safety entities: {len(safety_entities)}")
            logger.info(f"Total entities: {total_entities}")
            
            return {
                "success": True,
                "chemical_compounds": chemical_compounds,
                "hazard_entities": hazard_entities,
                "property_entities": property_entities,
                "safety_entities": safety_entities,
                "total_entities": total_entities
            }
            
        except Exception as e:
            logger.error(f"❌ Entity extraction error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_relationship_extraction(self, text, entities):
        """Test relationship extraction"""
        logger.info("Testing Relationship Extraction...")
        
        try:
            # Extract relationships
            relationships = self.relationship_extractor.extract_relationships(text, entities)
            
            # Categorize relationships
            chemical_hazard_rels = [r for r in relationships if r["type"] == "HAS_HAZARD_CLASS"]
            storage_rels = [r for r in relationships if r["type"] in ["STORED_IN", "LOCATED_AT"]]
            compatibility_rels = [r for r in relationships if r["type"] in ["COMPATIBLE_WITH", "INCOMPATIBLE_WITH"]]
            testing_rels = [r for r in relationships if r["type"] in ["TESTED_WITH", "ASSESSED_FOR"]]
            
            logger.info(f"✅ Relationship extraction completed")
            logger.info(f"Chemical-hazard relationships: {len(chemical_hazard_rels)}")
            logger.info(f"Storage relationships: {len(storage_rels)}")
            logger.info(f"Compatibility relationships: {len(compatibility_rels)}")
            logger.info(f"Testing relationships: {len(testing_rels)}")
            logger.info(f"Total relationships: {len(relationships)}")
            
            return {
                "success": True,
                "relationships": relationships,
                "chemical_hazard_rels": chemical_hazard_rels,
                "storage_rels": storage_rels,
                "compatibility_rels": compatibility_rels,
                "testing_rels": testing_rels
            }
            
        except Exception as e:
            logger.error(f"❌ Relationship extraction error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_batch_processing(self, document_paths, doc_types=None):
        """Test batch document processing"""
        logger.info(f"Testing Batch Processing: {len(document_paths)} documents")
        
        try:
            if doc_types is None:
                doc_types = ["safety"] * len(document_paths)
            
            # Process batch
            result = await self.pipeline.process_batch_documents_to_kg(document_paths, doc_types)
            
            if result["success"]:
                logger.info(f"✅ Batch processing completed")
                logger.info(f"Successfully processed: {len(result.get('successful', []))}")
                logger.info(f"Failed documents: {len(result.get('failed', []))}")
                logger.info(f"Total entities extracted: {result.get('total_entities', 0)}")
                logger.info(f"Total relationships extracted: {result.get('total_relationships', 0)}")
                
                return result
            else:
                logger.error(f"❌ Batch processing failed: {result.get('error', 'Unknown error')}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Batch processing error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_kg_integration(self, entities, relationships):
        """Test knowledge graph integration"""
        logger.info("Testing Knowledge Graph Integration...")
        
        try:
            stored_entities = 0
            stored_relationships = 0
            
            # Store entities
            for entity in entities:
                if entity["type"] == "chemical_compound":
                    await self.kg_service.create_substance(entity["data"])
                    stored_entities += 1
                elif entity["type"] == "hazard":
                    await self.kg_service.create_hazard(entity["data"])
                    stored_entities += 1
                elif entity["type"] == "property":
                    await self.kg_service.create_property(entity["data"])
                    stored_entities += 1
            
            # Store relationships
            for relationship in relationships:
                await self.kg_service.create_relationship(relationship)
                stored_relationships += 1
            
            logger.info(f"✅ Knowledge Graph integration completed")
            logger.info(f"Stored entities: {stored_entities}")
            logger.info(f"Stored relationships: {stored_relationships}")
            
            return {
                "success": True,
                "stored_entities": stored_entities,
                "stored_relationships": stored_relationships
            }
            
        except Exception as e:
            logger.error(f"❌ Knowledge Graph integration error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_rag_query(self, query):
        """Test RAG query functionality"""
        logger.info(f"Testing RAG Query: {query}")
        
        try:
            # Query the RAG system
            result = await self.pipeline.query_rag_system(query)
            
            if result["success"]:
                logger.info(f"✅ RAG query successful")
                logger.info(f"Answer: {result.get('answer', 'No answer')}")
                logger.info(f"Sources: {len(result.get('sources', []))}")
                logger.info(f"Confidence: {result.get('confidence', 0):.2f}")
                
                return result
            else:
                logger.error(f"❌ RAG query failed: {result.get('error', 'Unknown error')}")
                return result
                
        except Exception as e:
            logger.error(f"❌ RAG query error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_document_classification(self, document_path):
        """Test document classification"""
        logger.info(f"Testing Document Classification: {document_path}")
        
        try:
            # Classify document
            doc_type = await self.pipeline.classify_document(document_path)
            
            logger.info(f"✅ Document classification completed")
            logger.info(f"Classified as: {doc_type}")
            
            return {
                "success": True,
                "document_type": doc_type
            }
            
        except Exception as e:
            logger.error(f"❌ Document classification error: {e}")
            return {"success": False, "error": str(e)}

async def main():
    parser = argparse.ArgumentParser(description="Test NLP & RAG Pipeline")
    parser.add_argument("--type", choices=["pdf", "csv", "json", "all"], 
                       help="Test specific document type")
    parser.add_argument("--document", help="Path to specific document")
    parser.add_argument("--batch", help="Path to directory with documents")
    parser.add_argument("--query", help="RAG query to test")
    parser.add_argument("--text", help="Text for entity extraction test")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    tester = NLP_RAGPipelineTester()
    
    # Initialize pipeline
    if not await tester.initialize():
        logger.error("Failed to initialize pipeline")
        return
    
    if args.document:
        # Test single document
        result = await tester.test_document_processing(args.document)
        print(json.dumps(result, indent=2))
        
    elif args.text:
        # Test entity extraction
        entity_result = await tester.test_entity_extraction(args.text)
        if entity_result["success"]:
            # Test relationship extraction
            all_entities = (entity_result["chemical_compounds"] + 
                          entity_result["hazard_entities"] + 
                          entity_result["property_entities"] + 
                          entity_result["safety_entities"])
            rel_result = await tester.test_relationship_extraction(args.text, all_entities)
            print(json.dumps({"entities": entity_result, "relationships": rel_result}, indent=2))
        else:
            print(json.dumps(entity_result, indent=2))
            
    elif args.query:
        # Test RAG query
        result = await tester.test_rag_query(args.query)
        print(json.dumps(result, indent=2))
        
    elif args.batch:
        # Test batch processing
        import glob
        documents = glob.glob(f"{args.batch}/*")
        result = await tester.test_batch_processing(documents)
        print(json.dumps(result, indent=2))
        
    else:
        # Run comprehensive tests
        logger.info("Running comprehensive NLP & RAG tests...")
        
        # Test with sample data
        sample_text = """
        Sulfuric acid (H2SO4) is a highly corrosive substance with CAS number 7664-93-9. 
        It should be stored in glass containers and requires proper PPE including gloves and goggles.
        This substance is incompatible with organic materials and can cause severe burns.
        """
        
        # Test entity extraction
        entity_result = await tester.test_entity_extraction(sample_text)
        
        # Test relationship extraction
        all_entities = (entity_result["chemical_compounds"] + 
                      entity_result["hazard_entities"] + 
                      entity_result["property_entities"] + 
                      entity_result["safety_entities"])
        rel_result = await tester.test_relationship_extraction(sample_text, all_entities)
        
        # Test KG integration
        kg_result = await tester.test_kg_integration(all_entities, rel_result["relationships"])
        
        # Summary
        results = {
            "entity_extraction": entity_result,
            "relationship_extraction": rel_result,
            "kg_integration": kg_result
        }
        
        logger.info(f"\n{'='*50}")
        logger.info(f"NLP & RAG PIPELINE TEST SUMMARY")
        logger.info(f"{'='*50}")
        
        for test_name, result in results.items():
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
            if not result.get("success", False):
                logger.error(f"  Error: {result.get('error', 'Unknown error')}")
        
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(main()) 