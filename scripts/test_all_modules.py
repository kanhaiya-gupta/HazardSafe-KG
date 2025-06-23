#!/usr/bin/env python3
"""
Simple Test Script for All Modules
Demonstrates the scripting approach for HazardSafe-KG development
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_ontology_module():
    """Test ontology module functionality"""
    logger.info("Testing Ontology Module...")
    
    try:
        # Import ontology components
        from ontology.manager import OntologyManager
        from ontology.ontology_to_kg_pipeline import OntologyToKGPipeline
        
        # Initialize components
        ontology_manager = OntologyManager()
        pipeline = OntologyToKGPipeline()
        
        # Test basic functionality
        logger.info("✅ Ontology module imports successful")
        logger.info("✅ Ontology components initialized")
        
        return {"success": True, "message": "Ontology module ready"}
        
    except Exception as e:
        logger.error(f"❌ Ontology module error: {e}")
        return {"success": False, "error": str(e)}

async def test_nlp_rag_module():
    """Test NLP & RAG module functionality"""
    logger.info("Testing NLP & RAG Module...")
    
    try:
        # Import NLP & RAG components
        from nlp_rag.document_to_kg_pipeline import DocumentToKGPipeline
        from nlp_rag.processors.document_processor import DocumentProcessor
        
        # Initialize components
        pipeline = DocumentToKGPipeline()
        processor = DocumentProcessor()
        
        # Test basic functionality
        logger.info("✅ NLP & RAG module imports successful")
        logger.info("✅ NLP & RAG components initialized")
        
        return {"success": True, "message": "NLP & RAG module ready"}
        
    except Exception as e:
        logger.error(f"❌ NLP & RAG module error: {e}")
        return {"success": False, "error": str(e)}

async def test_kg_module():
    """Test knowledge graph module functionality"""
    logger.info("Testing Knowledge Graph Module...")
    
    try:
        # Import KG components
        from kg.services import KnowledgeGraphService
        from kg.models import Substance, Container, Test, Assessment
        
        # Initialize components
        kg_service = KnowledgeGraphService()
        
        # Test basic functionality
        logger.info("✅ Knowledge Graph module imports successful")
        logger.info("✅ Knowledge Graph components initialized")
        
        return {"success": True, "message": "Knowledge Graph module ready"}
        
    except Exception as e:
        logger.error(f"❌ Knowledge Graph module error: {e}")
        return {"success": False, "error": str(e)}

async def test_validation_module():
    """Test validation module functionality"""
    logger.info("Testing Validation Module...")
    
    try:
        # Import validation components
        from validation.validator import DataValidator
        from validation.rules import BusinessRules
        
        # Initialize components
        validator = DataValidator()
        rules = BusinessRules()
        
        # Test basic functionality
        logger.info("✅ Validation module imports successful")
        logger.info("✅ Validation components initialized")
        
        return {"success": True, "message": "Validation module ready"}
        
    except Exception as e:
        logger.error(f"❌ Validation module error: {e}")
        return {"success": False, "error": str(e)}

async def test_quality_module():
    """Test quality module functionality"""
    logger.info("Testing Quality Module...")
    
    try:
        # Import quality components
        from quality.metrics import QualityMetrics
        from quality.reports import QualityReporter
        
        # Initialize components
        metrics = QualityMetrics()
        reporter = QualityReporter()
        
        # Test basic functionality
        logger.info("✅ Quality module imports successful")
        logger.info("✅ Quality components initialized")
        
        return {"success": True, "message": "Quality module ready"}
        
    except Exception as e:
        logger.error(f"❌ Quality module error: {e}")
        return {"success": False, "error": str(e)}

async def test_sample_data_creation():
    """Test sample data creation"""
    logger.info("Testing Sample Data Creation...")
    
    try:
        # Create sample data directories
        data_dirs = [
            "data/ontology",
            "data/documents", 
            "data/substances",
            "data/containers",
            "data/tests"
        ]
        
        for dir_path in data_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
        
        # Create sample TTL file
        sample_ttl = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix haz: <http://hazardsafe.kg/ontology#> .

haz:HazardousSubstance a rdfs:Class ;
    rdfs:label "Hazardous Substance" ;
    rdfs:comment "A chemical substance with hazardous properties" .

haz:hasHazardClass a rdf:Property ;
    rdfs:domain haz:HazardousSubstance ;
    rdfs:range haz:HazardClass ."""
        
        with open("data/ontology/sample.ttl", "w") as f:
            f.write(sample_ttl)
        
        # Create sample CSV file
        sample_csv = """name,formula,cas_number,hazard_class
Sulfuric Acid,H2SO4,7664-93-9,corrosive
Sodium Hydroxide,NaOH,1310-73-2,corrosive
Methanol,CH3OH,67-56-1,flammable"""
        
        with open("data/documents/substances.csv", "w") as f:
            f.write(sample_csv)
        
        logger.info("✅ Sample data created successfully")
        
        return {"success": True, "message": "Sample data created"}
        
    except Exception as e:
        logger.error(f"❌ Sample data creation error: {e}")
        return {"success": False, "error": str(e)}

async def main():
    """Main test function"""
    logger.info("Starting HazardSafe-KG Module Tests")
    logger.info("=" * 50)
    
    # Test all modules
    test_results = {}
    
    test_results["ontology"] = await test_ontology_module()
    test_results["nlp_rag"] = await test_nlp_rag_module()
    test_results["kg"] = await test_kg_module()
    test_results["validation"] = await test_validation_module()
    test_results["quality"] = await test_quality_module()
    test_results["sample_data"] = await test_sample_data_creation()
    
    # Summary
    successful_modules = sum(1 for r in test_results.values() if r.get("success", False))
    total_modules = len(test_results)
    
    logger.info("=" * 50)
    logger.info("TEST SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Successful modules: {successful_modules}/{total_modules}")
    
    for module_name, result in test_results.items():
        status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
        logger.info(f"{module_name.upper()}: {status}")
        if result.get("success", False):
            logger.info(f"  Message: {result.get('message', 'No message')}")
        else:
            logger.error(f"  Error: {result.get('error', 'Unknown error')}")
    
    logger.info("=" * 50)
    
    if successful_modules == total_modules:
        logger.info("🎉 All modules are ready for development!")
        logger.info("Next steps:")
        logger.info("1. Run specific module tests: python scripts/test_ontology_pipeline.py")
        logger.info("2. Run integration tests: python scripts/integration_tests.py")
        logger.info("3. Start backend development with sample data")
        logger.info("4. Connect to frontend when backend is stable")
    else:
        logger.warning("⚠️  Some modules need attention before development")
        logger.info("Check the errors above and fix import issues")
    
    return test_results

if __name__ == "__main__":
    asyncio.run(main()) 