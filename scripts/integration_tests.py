#!/usr/bin/env python3
"""
Integration Test Script for HazardSafe-KG
Tests end-to-end workflows and module interactions
"""

import asyncio
import argparse
import sys
import os
import logging
import json
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from ontology.ontology_to_kg_pipeline import OntologyToKGPipeline
from nlp_rag.document_to_kg_pipeline import DocumentToKGPipeline
from kg.services import KnowledgeGraphService
from validation.validator import DataValidator
from quality.metrics import QualityMetrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IntegrationTester:
    def __init__(self):
        self.ontology_pipeline = OntologyToKGPipeline()
        self.document_pipeline = DocumentToKGPipeline()
        self.kg_service = KnowledgeGraphService()
        self.validator = DataValidator()
        self.quality_metrics = QualityMetrics()
        
    async def initialize(self):
        """Initialize all components"""
        try:
            await self.document_pipeline.initialize()
            logger.info("✅ All components initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    async def test_ontology_to_kg_integration(self):
        """Test complete ontology-to-KG integration"""
        logger.info("Testing Ontology-to-KG Integration...")
        
        try:
            start_time = time.time()
            
            # Step 1: Run ontology pipeline
            ontology_result = await self.ontology_pipeline.run_pipeline("data/ontology")
            
            if not ontology_result["success"]:
                logger.error(f"Ontology pipeline failed: {ontology_result.get('error', 'Unknown error')}")
                return {"success": False, "error": "Ontology pipeline failed"}
            
            # Step 2: Validate KG data
            kg_data = await self.kg_service.get_all_substances()
            validation_result = await self.validator.validate_data(kg_data, "substances")
            
            # Step 3: Assess quality
            quality_result = self.quality_metrics.calculate_overall_quality_score(kg_data)
            
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"✅ Ontology-to-KG integration completed in {duration:.2f} seconds")
            logger.info(f"KG entities: {len(kg_data)}")
            logger.info(f"Validation passed: {validation_result['valid']}")
            logger.info(f"Quality score: {quality_result['overall_score']:.2%}")
            
            return {
                "success": True,
                "duration": duration,
                "kg_entities": len(kg_data),
                "validation_passed": validation_result['valid'],
                "quality_score": quality_result['overall_score'],
                "ontology_result": ontology_result,
                "validation_result": validation_result,
                "quality_result": quality_result
            }
            
        except Exception as e:
            logger.error(f"❌ Ontology-to-KG integration error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_document_to_kg_integration(self):
        """Test complete document-to-KG integration"""
        logger.info("Testing Document-to-KG Integration...")
        
        try:
            start_time = time.time()
            
            # Step 1: Process documents
            documents = ["data/documents/substances.csv", "data/documents/safety_sheet.pdf"]
            doc_result = await self.document_pipeline.process_batch_documents_to_kg(documents)
            
            if not doc_result["success"]:
                logger.error(f"Document pipeline failed: {doc_result.get('error', 'Unknown error')}")
                return {"success": False, "error": "Document pipeline failed"}
            
            # Step 2: Validate extracted entities
            entities = doc_result.get("entities", [])
            validation_results = []
            
            for entity in entities:
                validation_result = await self.validator.validate_data(entity, "substances")
                validation_results.append(validation_result)
            
            # Step 3: Assess quality
            if entities:
                quality_result = self.quality_metrics.calculate_overall_quality_score(entities)
            else:
                quality_result = {"overall_score": 0.0, "quality_grade": "F"}
            
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"✅ Document-to-KG integration completed in {duration:.2f} seconds")
            logger.info(f"Extracted entities: {len(entities)}")
            logger.info(f"Validation passed: {sum(1 for r in validation_results if r['valid'])}/{len(validation_results)}")
            logger.info(f"Quality score: {quality_result['overall_score']:.2%}")
            
            return {
                "success": True,
                "duration": duration,
                "extracted_entities": len(entities),
                "validation_passed": sum(1 for r in validation_results if r['valid']),
                "validation_total": len(validation_results),
                "quality_score": quality_result['overall_score'],
                "doc_result": doc_result,
                "validation_results": validation_results,
                "quality_result": quality_result
            }
            
        except Exception as e:
            logger.error(f"❌ Document-to-KG integration error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_validation_quality_integration(self):
        """Test validation and quality integration"""
        logger.info("Testing Validation-Quality Integration...")
        
        try:
            start_time = time.time()
            
            # Step 1: Get data from KG
            substances = await self.kg_service.get_all_substances()
            containers = await self.kg_service.get_all_containers()
            tests = await self.kg_service.get_all_tests()
            
            all_data = substances + containers + tests
            
            # Step 2: Validate all data
            validation_results = []
            for data in all_data:
                data_type = type(data).__name__.lower()
                validation_result = await self.validator.validate_data(data, data_type)
                validation_results.append(validation_result)
            
            # Step 3: Assess quality
            quality_result = self.quality_metrics.calculate_overall_quality_score(all_data)
            
            # Step 4: Generate quality report
            from quality.reports import QualityReporter
            reporter = QualityReporter()
            report_path = reporter.generate_quality_report(quality_result, "integration_test")
            
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"✅ Validation-Quality integration completed in {duration:.2f} seconds")
            logger.info(f"Total data items: {len(all_data)}")
            logger.info(f"Validation passed: {sum(1 for r in validation_results if r['valid'])}/{len(validation_results)}")
            logger.info(f"Quality score: {quality_result['overall_score']:.2%}")
            logger.info(f"Quality report: {report_path}")
            
            return {
                "success": True,
                "duration": duration,
                "total_data_items": len(all_data),
                "validation_passed": sum(1 for r in validation_results if r['valid']),
                "validation_total": len(validation_results),
                "quality_score": quality_result['overall_score'],
                "report_path": report_path,
                "validation_results": validation_results,
                "quality_result": quality_result
            }
            
        except Exception as e:
            logger.error(f"❌ Validation-Quality integration error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_cross_module_data_flow(self):
        """Test data flow across all modules"""
        logger.info("Testing Cross-Module Data Flow...")
        
        try:
            start_time = time.time()
            
            # Step 1: Load ontology and create initial KG
            ontology_result = await self.ontology_pipeline.run_pipeline("data/ontology")
            
            # Step 2: Process documents and add to KG
            documents = ["data/documents/substances.csv"]
            doc_result = await self.document_pipeline.process_batch_documents_to_kg(documents)
            
            # Step 3: Query KG for combined data
            query = """
            MATCH (s:Substance)
            OPTIONAL MATCH (s)-[:HAS_HAZARD]->(h:Hazard)
            OPTIONAL MATCH (s)-[:STORED_IN]->(c:Container)
            RETURN s.name, h.type, c.name
            LIMIT 10
            """
            kg_results = await self.kg_service.execute_query(query)
            
            # Step 4: Validate combined data
            validation_results = []
            for result in kg_results:
                validation_result = await self.validator.validate_data(result, "substances")
                validation_results.append(validation_result)
            
            # Step 5: Assess overall quality
            quality_result = self.quality_metrics.calculate_overall_quality_score(kg_results)
            
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"✅ Cross-module data flow completed in {duration:.2f} seconds")
            logger.info(f"KG query results: {len(kg_results)}")
            logger.info(f"Validation passed: {sum(1 for r in validation_results if r['valid'])}/{len(validation_results)}")
            logger.info(f"Quality score: {quality_result['overall_score']:.2%}")
            
            return {
                "success": True,
                "duration": duration,
                "kg_results": len(kg_results),
                "validation_passed": sum(1 for r in validation_results if r['valid']),
                "validation_total": len(validation_results),
                "quality_score": quality_result['overall_score'],
                "ontology_result": ontology_result,
                "doc_result": doc_result,
                "kg_results_data": kg_results,
                "validation_results": validation_results,
                "quality_result": quality_result
            }
            
        except Exception as e:
            logger.error(f"❌ Cross-module data flow error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_performance_benchmarks(self):
        """Test performance benchmarks"""
        logger.info("Testing Performance Benchmarks...")
        
        try:
            benchmarks = {}
            
            # Benchmark 1: Ontology pipeline
            start_time = time.time()
            ontology_result = await self.ontology_pipeline.run_pipeline("data/ontology")
            ontology_duration = time.time() - start_time
            benchmarks["ontology_pipeline"] = {
                "duration": ontology_duration,
                "success": ontology_result["success"]
            }
            
            # Benchmark 2: Document processing
            start_time = time.time()
            doc_result = await self.document_pipeline.process_batch_documents_to_kg(["data/documents/substances.csv"])
            doc_duration = time.time() - start_time
            benchmarks["document_processing"] = {
                "duration": doc_duration,
                "success": doc_result["success"]
            }
            
            # Benchmark 3: KG queries
            start_time = time.time()
            queries = [
                "MATCH (s:Substance) RETURN count(s)",
                "MATCH (s:Substance)-[:HAS_HAZARD]->(h:Hazard) RETURN s.name, h.type LIMIT 10",
                "MATCH (s:Substance)-[:STORED_IN]->(c:Container) RETURN s.name, c.name LIMIT 10"
            ]
            
            query_results = []
            for query in queries:
                result = await self.kg_service.execute_query(query)
                query_results.append(result)
            
            query_duration = time.time() - start_time
            benchmarks["kg_queries"] = {
                "duration": query_duration,
                "queries_executed": len(queries),
                "results": len(query_results)
            }
            
            # Benchmark 4: Validation
            substances = await self.kg_service.get_all_substances()
            start_time = time.time()
            validation_results = []
            for substance in substances[:10]:  # Test first 10
                result = await self.validator.validate_data(substance, "substances")
                validation_results.append(result)
            validation_duration = time.time() - start_time
            benchmarks["validation"] = {
                "duration": validation_duration,
                "items_validated": len(validation_results)
            }
            
            # Benchmark 5: Quality assessment
            start_time = time.time()
            quality_result = self.quality_metrics.calculate_overall_quality_score(substances)
            quality_duration = time.time() - start_time
            benchmarks["quality_assessment"] = {
                "duration": quality_duration,
                "quality_score": quality_result["overall_score"]
            }
            
            logger.info(f"✅ Performance benchmarks completed")
            logger.info(f"Ontology pipeline: {ontology_duration:.2f}s")
            logger.info(f"Document processing: {doc_duration:.2f}s")
            logger.info(f"KG queries: {query_duration:.2f}s")
            logger.info(f"Validation: {validation_duration:.2f}s")
            logger.info(f"Quality assessment: {quality_duration:.2f}s")
            
            return {
                "success": True,
                "benchmarks": benchmarks
            }
            
        except Exception as e:
            logger.error(f"❌ Performance benchmarks error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms"""
        logger.info("Testing Error Handling and Recovery...")
        
        try:
            error_tests = []
            
            # Test 1: Invalid ontology file
            try:
                await self.ontology_pipeline.run_pipeline("nonexistent_directory")
                error_tests.append({"test": "invalid_ontology_path", "handled": False})
            except Exception as e:
                error_tests.append({"test": "invalid_ontology_path", "handled": True, "error": str(e)})
            
            # Test 2: Invalid document
            try:
                await self.document_pipeline.process_document_to_kg("nonexistent_file.pdf", "safety")
                error_tests.append({"test": "invalid_document", "handled": False})
            except Exception as e:
                error_tests.append({"test": "invalid_document", "handled": True, "error": str(e)})
            
            # Test 3: Invalid KG query
            try:
                await self.kg_service.execute_query("INVALID CYPHER QUERY")
                error_tests.append({"test": "invalid_query", "handled": False})
            except Exception as e:
                error_tests.append({"test": "invalid_query", "handled": True, "error": str(e)})
            
            # Test 4: Invalid validation data
            try:
                await self.validator.validate_data({"invalid": "data"}, "unknown_type")
                error_tests.append({"test": "invalid_validation", "handled": False})
            except Exception as e:
                error_tests.append({"test": "invalid_validation", "handled": True, "error": str(e)})
            
            handled_errors = sum(1 for test in error_tests if test["handled"])
            total_tests = len(error_tests)
            
            logger.info(f"✅ Error handling tests completed")
            logger.info(f"Errors handled: {handled_errors}/{total_tests}")
            
            return {
                "success": True,
                "error_tests": error_tests,
                "handled_errors": handled_errors,
                "total_tests": total_tests
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling test error: {e}")
            return {"success": False, "error": str(e)}

async def main():
    parser = argparse.ArgumentParser(description="Integration Tests for HazardSafe-KG")
    parser.add_argument("--scenario", choices=["ontology_to_kg", "document_to_kg", "validation_quality", "cross_module", "performance", "error_handling", "all"], 
                       help="Test specific integration scenario")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    tester = IntegrationTester()
    
    # Initialize components
    if not await tester.initialize():
        logger.error("Failed to initialize components")
        return
    
    if args.scenario == "ontology_to_kg":
        result = await tester.test_ontology_to_kg_integration()
    elif args.scenario == "document_to_kg":
        result = await tester.test_document_to_kg_integration()
    elif args.scenario == "validation_quality":
        result = await tester.test_validation_quality_integration()
    elif args.scenario == "cross_module":
        result = await tester.test_cross_module_data_flow()
    elif args.scenario == "performance":
        result = await tester.test_performance_benchmarks()
    elif args.scenario == "error_handling":
        result = await tester.test_error_handling_and_recovery()
    else:
        # Run all integration tests
        logger.info("Running all integration tests...")
        
        results = {}
        results["ontology_to_kg"] = await tester.test_ontology_to_kg_integration()
        results["document_to_kg"] = await tester.test_document_to_kg_integration()
        results["validation_quality"] = await tester.test_validation_quality_integration()
        results["cross_module"] = await tester.test_cross_module_data_flow()
        results["performance"] = await tester.test_performance_benchmarks()
        results["error_handling"] = await tester.test_error_handling_and_recovery()
        
        # Summary
        successful_tests = sum(1 for r in results.values() if r.get("success", False))
        total_tests = len(results)
        
        logger.info(f"\n{'='*50}")
        logger.info(f"INTEGRATION TEST SUMMARY")
        logger.info(f"{'='*50}")
        logger.info(f"Successful tests: {successful_tests}/{total_tests}")
        
        for test_name, result in results.items():
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
            if not result.get("success", False):
                logger.error(f"  Error: {result.get('error', 'Unknown error')}")
        
        return results
    
    return result

if __name__ == "__main__":
    asyncio.run(main()) 