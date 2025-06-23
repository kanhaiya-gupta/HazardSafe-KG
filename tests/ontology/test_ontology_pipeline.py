#!/usr/bin/env python3
"""
Test script for the Ontology to Knowledge Graph Pipeline.
This script demonstrates the 5-step pipeline process.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from ontology.ontology_to_kg_pipeline import OntologyToKGPipeline, run_ontology_to_kg_pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_pipeline_step_by_step():
    """Test the pipeline step by step."""
    logger.info("Testing Ontology-to-KG Pipeline Step by Step")
    
    pipeline = OntologyToKGPipeline()
    
    try:
        # Initialize pipeline
        logger.info("Initializing pipeline...")
        await pipeline.initialize()
        
        # Step 1: Ontology File Ingestion
        logger.info("Step 1: Ontology File Ingestion")
        ingestion_result = await pipeline._step1_ontology_ingestion("data/ontology")
        print(f"Step 1 Result: {ingestion_result['success']}")
        print(f"Files loaded: {ingestion_result['files_loaded']}")
        print(f"Total triples: {ingestion_result['total_triples']}")
        
        if not ingestion_result["success"]:
            logger.error("Step 1 failed")
            return
        
        # Step 2: Ontology Management
        logger.info("Step 2: Ontology Management")
        management_result = await pipeline._step2_ontology_management()
        print(f"Step 2 Result: {management_result['success']}")
        print(f"Classes extracted: {management_result['classes_extracted']}")
        print(f"Properties extracted: {management_result['properties_extracted']}")
        print(f"SHACL constraints: {management_result['shacl_constraints']}")
        
        if not management_result["success"]:
            logger.error("Step 2 failed")
            return
        
        # Step 3: SHACL Validation
        logger.info("Step 3: SHACL Validation")
        validation_result = await pipeline._step3_shacl_validation()
        print(f"Step 3 Result: {validation_result['success']}")
        print(f"Triples validated: {validation_result['triples_validated']}")
        print(f"Valid triples: {validation_result['valid_triples']}")
        print(f"Invalid triples: {validation_result['invalid_triples']}")
        
        if not validation_result["success"]:
            logger.error("Step 3 failed")
            return
        
        # Step 4: Data Quality Check
        logger.info("Step 4: Data Quality Check")
        quality_result = await pipeline._step4_data_quality_check()
        print(f"Step 4 Result: {quality_result['success']}")
        print(f"Quality score: {quality_result['quality_score']:.2f}")
        print(f"Completeness: {quality_result['completeness']:.2f}")
        print(f"Accuracy: {quality_result['accuracy']:.2f}")
        print(f"Consistency: {quality_result['consistency']:.2f}")
        
        # Step 5: Knowledge Graph Storage
        logger.info("Step 5: Knowledge Graph Storage")
        storage_result = await pipeline._step5_kg_storage()
        print(f"Step 5 Result: {storage_result['success']}")
        print(f"Entities created: {storage_result['entities_created']}")
        print(f"Relationships created: {storage_result['relationships_created']}")
        
        logger.info("Pipeline test completed successfully!")
        
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}")
    finally:
        await pipeline.close()

async def test_complete_pipeline():
    """Test the complete pipeline in one go."""
    logger.info("Testing Complete Ontology-to-KG Pipeline")
    
    try:
        results = await run_ontology_to_kg_pipeline("data/ontology")
        
        print("\n=== Pipeline Results ===")
        print(f"Overall Success: {results['overall_success']}")
        print(f"Total Entities Created: {results['total_entities_created']}")
        print(f"Total Relationships Created: {results['total_relationships_created']}")
        print(f"Quality Score: {results['quality_score']:.2f}")
        
        if results['errors']:
            print(f"Errors: {results['errors']}")
        
        # Print step results
        print("\n=== Step Results ===")
        for step_name, step_result in results.items():
            if step_name.startswith('step') and step_name.endswith('_'):
                step_num = step_name[4:-1]
                print(f"Step {step_num}: {step_result.get('success', False)}")
        
        logger.info("Complete pipeline test finished!")
        
    except Exception as e:
        logger.error(f"Complete pipeline test failed: {e}")

async def test_pipeline_status():
    """Test pipeline status checking."""
    logger.info("Testing Pipeline Status")
    
    try:
        from webapp.ontology.routes import get_pipeline_status
        status = await get_pipeline_status()
        
        print("\n=== Pipeline Status ===")
        print(f"Success: {status['success']}")
        if status['success']:
            pipeline_status = status['pipeline_status']
            print(f"Ontology Files Count: {pipeline_status['ontology_files_count']}")
            print(f"Neo4j Connected: {pipeline_status['neo4j_connected']}")
            print(f"Pipeline Ready: {pipeline_status['pipeline_ready']}")
            
            if pipeline_status['ontology_files']:
                print("\nOntology Files:")
                for file_info in pipeline_status['ontology_files']:
                    print(f"  - {file_info['file']} ({file_info['extension']})")
        
        logger.info("Pipeline status test completed!")
        
    except Exception as e:
        logger.error(f"Pipeline status test failed: {e}")

async def main():
    """Main test function."""
    print("=" * 60)
    print("Ontology to Knowledge Graph Pipeline Test")
    print("=" * 60)
    
    # Check if ontology files exist
    ontology_dir = Path("data/ontology")
    if not ontology_dir.exists():
        logger.error(f"Ontology directory {ontology_dir} does not exist")
        return
    
    ontology_files = list(ontology_dir.glob("*.ttl")) + list(ontology_dir.glob("*.owl"))
    if not ontology_files:
        logger.error("No ontology files found")
        return
    
    logger.info(f"Found {len(ontology_files)} ontology files")
    for file_path in ontology_files:
        logger.info(f"  - {file_path}")
    
    print("\n" + "=" * 60)
    
    # Run tests
    try:
        # Test 1: Step by step
        print("\n1. Testing Pipeline Step by Step")
        print("-" * 40)
        await test_pipeline_step_by_step()
        
        print("\n" + "=" * 60)
        
        # Test 2: Complete pipeline
        print("\n2. Testing Complete Pipeline")
        print("-" * 40)
        await test_complete_pipeline()
        
        print("\n" + "=" * 60)
        
        # Test 3: Pipeline status
        print("\n3. Testing Pipeline Status")
        print("-" * 40)
        await test_pipeline_status()
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
    
    print("\n" + "=" * 60)
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(main()) 