#!/usr/bin/env python3
"""
Test script for Ontology Pipeline
Tests the complete ontology-to-KG pipeline and individual steps
"""

import asyncio
import argparse
import sys
import os
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from ontology.manager import OntologyManager
from ontology.ontology_to_kg_pipeline import OntologyToKGPipeline
from kg.services import KnowledgeGraphService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OntologyPipelineTester:
    def __init__(self):
        self.ontology_manager = OntologyManager()
        self.pipeline = OntologyToKGPipeline()
        self.kg_service = KnowledgeGraphService()
        
    async def test_ontology_ingestion(self, ontology_dir="data/ontology"):
        """Test Step 1: Ontology File Ingestion"""
        logger.info("Testing Ontology Ingestion...")
        
        try:
            # Test loading ontology files
            success = await self.ontology_manager.load_ontology_files(ontology_dir)
            
            if success:
                graph_size = len(self.ontology_manager.graph)
                logger.info(f"✅ Ontology ingestion successful: {graph_size} triples loaded")
                
                # Print sample triples
                sample_triples = list(self.ontology_manager.graph)[:5]
                logger.info(f"Sample triples: {sample_triples}")
                
                return {
                    "success": True,
                    "triples_count": graph_size,
                    "sample_triples": sample_triples
                }
            else:
                logger.error("❌ Ontology ingestion failed")
                return {"success": False, "error": "Failed to load ontology files"}
                
        except Exception as e:
            logger.error(f"❌ Ontology ingestion error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_ontology_management(self):
        """Test Step 2: Ontology Management"""
        logger.info("Testing Ontology Management...")
        
        try:
            # Extract ontology schema
            schema = await self.pipeline._extract_ontology_schema()
            
            # Extract SHACL constraints
            shacl_constraints = await self.pipeline._extract_shacl_constraints()
            
            logger.info(f"✅ Ontology management successful")
            logger.info(f"Classes found: {len(schema.get('classes', []))}")
            logger.info(f"Properties found: {len(schema.get('properties', []))}")
            logger.info(f"SHACL constraints: {len(shacl_constraints)}")
            
            return {
                "success": True,
                "classes_count": len(schema.get('classes', [])),
                "properties_count": len(schema.get('properties', [])),
                "shacl_constraints_count": len(shacl_constraints)
            }
            
        except Exception as e:
            logger.error(f"❌ Ontology management error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_shacl_validation(self):
        """Test Step 3: SHACL Validation"""
        logger.info("Testing SHACL Validation...")
        
        try:
            # Extract entities from RDF
            entities = await self.pipeline._extract_entities_from_rdf()
            
            # Validate entities with SHACL
            validated_entities = []
            validation_errors = []
            
            for entity in entities:
                validation_result = await self.pipeline._validate_entity_with_shacl(entity)
                if validation_result["valid"]:
                    validated_entities.append(entity)
                else:
                    validation_errors.append(validation_result["errors"])
            
            logger.info(f"✅ SHACL validation completed")
            logger.info(f"Valid entities: {len(validated_entities)}")
            logger.info(f"Validation errors: {len(validation_errors)}")
            
            return {
                "success": True,
                "valid_entities": len(validated_entities),
                "validation_errors": len(validation_errors),
                "total_entities": len(entities)
            }
            
        except Exception as e:
            logger.error(f"❌ SHACL validation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_data_quality_check(self):
        """Test Step 4: Data Quality Check"""
        logger.info("Testing Data Quality Check...")
        
        try:
            # Assess data quality
            quality_metrics = await self.pipeline._assess_data_quality()
            
            completeness = quality_metrics.get("completeness", 0)
            accuracy = quality_metrics.get("accuracy", 0)
            consistency = quality_metrics.get("consistency", 0)
            
            # Calculate overall quality score
            quality_score = (completeness * 0.3 + accuracy * 0.4 + consistency * 0.3)
            
            logger.info(f"✅ Data quality assessment completed")
            logger.info(f"Completeness: {completeness:.2%}")
            logger.info(f"Accuracy: {accuracy:.2%}")
            logger.info(f"Consistency: {consistency:.2%}")
            logger.info(f"Overall Quality Score: {quality_score:.2%}")
            
            return {
                "success": True,
                "completeness": completeness,
                "accuracy": accuracy,
                "consistency": consistency,
                "overall_score": quality_score
            }
            
        except Exception as e:
            logger.error(f"❌ Data quality check error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_kg_storage(self):
        """Test Step 5: Knowledge Graph Storage"""
        logger.info("Testing Knowledge Graph Storage...")
        
        try:
            # Convert RDF to KG format
            kg_data = await self.pipeline._convert_rdf_to_kg_format()
            
            # Store in Neo4j
            stored_entities = 0
            stored_relationships = 0
            
            for entity in kg_data.get("entities", []):
                if entity["type"] == "HazardousSubstance":
                    await self.kg_service.create_substance(entity["data"])
                    stored_entities += 1
                elif entity["type"] == "Container":
                    await self.kg_service.create_container(entity["data"])
                    stored_entities += 1
                elif entity["type"] == "Test":
                    await self.kg_service.create_test(entity["data"])
                    stored_entities += 1
                elif entity["type"] == "Assessment":
                    await self.kg_service.create_assessment(entity["data"])
                    stored_entities += 1
            
            for relationship in kg_data.get("relationships", []):
                await self.kg_service.create_relationship(relationship)
                stored_relationships += 1
            
            logger.info(f"✅ Knowledge Graph storage completed")
            logger.info(f"Stored entities: {stored_entities}")
            logger.info(f"Stored relationships: {stored_relationships}")
            
            return {
                "success": True,
                "stored_entities": stored_entities,
                "stored_relationships": stored_relationships
            }
            
        except Exception as e:
            logger.error(f"❌ Knowledge Graph storage error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_complete_pipeline(self, ontology_dir="data/ontology"):
        """Test complete ontology-to-KG pipeline"""
        logger.info("Testing Complete Ontology-to-KG Pipeline...")
        
        try:
            # Run complete pipeline
            result = await self.pipeline.run_pipeline(ontology_dir)
            
            if result["success"]:
                logger.info("✅ Complete pipeline executed successfully")
                logger.info(f"Pipeline results: {result}")
            else:
                logger.error(f"❌ Pipeline failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Complete pipeline error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_kg_queries(self):
        """Test knowledge graph queries"""
        logger.info("Testing Knowledge Graph Queries...")
        
        try:
            # Test basic queries
            queries = [
                "MATCH (s:Substance) RETURN count(s) as substance_count",
                "MATCH (c:Container) RETURN count(c) as container_count",
                "MATCH (t:Test) RETURN count(t) as test_count",
                "MATCH (s:Substance)-[:HAS_HAZARD]->(h:Hazard) RETURN s.name, h.type LIMIT 5"
            ]
            
            results = {}
            for i, query in enumerate(queries):
                result = await self.kg_service.execute_query(query)
                results[f"query_{i+1}"] = result
                logger.info(f"Query {i+1} result: {result}")
            
            return {"success": True, "query_results": results}
            
        except Exception as e:
            logger.error(f"❌ KG queries error: {e}")
            return {"success": False, "error": str(e)}

async def main():
    parser = argparse.ArgumentParser(description="Test Ontology Pipeline")
    parser.add_argument("--step", choices=["ingestion", "management", "validation", "quality", "storage", "complete", "queries"], 
                       help="Test specific step or complete pipeline")
    parser.add_argument("--ontology-dir", default="data/ontology", help="Ontology directory path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    tester = OntologyPipelineTester()
    
    if args.step == "ingestion":
        result = await tester.test_ontology_ingestion(args.ontology_dir)
    elif args.step == "management":
        result = await tester.test_ontology_management()
    elif args.step == "validation":
        result = await tester.test_shacl_validation()
    elif args.step == "quality":
        result = await tester.test_data_quality_check()
    elif args.step == "storage":
        result = await tester.test_kg_storage()
    elif args.step == "queries":
        result = await tester.test_kg_queries()
    elif args.step == "complete":
        result = await tester.test_complete_pipeline(args.ontology_dir)
    else:
        # Run all tests
        logger.info("Running all ontology pipeline tests...")
        
        results = {}
        results["ingestion"] = await tester.test_ontology_ingestion(args.ontology_dir)
        results["management"] = await tester.test_ontology_management()
        results["validation"] = await tester.test_shacl_validation()
        results["quality"] = await tester.test_data_quality_check()
        results["storage"] = await tester.test_kg_storage()
        results["queries"] = await tester.test_kg_queries()
        
        # Summary
        successful_steps = sum(1 for r in results.values() if r.get("success", False))
        total_steps = len(results)
        
        logger.info(f"\n{'='*50}")
        logger.info(f"ONTOLOGY PIPELINE TEST SUMMARY")
        logger.info(f"{'='*50}")
        logger.info(f"Successful steps: {successful_steps}/{total_steps}")
        
        for step, result in results.items():
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            logger.info(f"{step.capitalize()}: {status}")
            if not result.get("success", False):
                logger.error(f"  Error: {result.get('error', 'Unknown error')}")
        
        return results
    
    return result

if __name__ == "__main__":
    asyncio.run(main()) 