#!/usr/bin/env python3
"""
Test script for Knowledge Graph Operations
Tests CRUD operations, queries, and graph analytics
"""

import asyncio
import argparse
import sys
import os
import logging
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from kg.services import KnowledgeGraphService
from kg.models import Substance, Container, Test, Assessment, Hazard, Property
from kg.queries import KnowledgeGraphQueries

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KnowledgeGraphTester:
    def __init__(self):
        self.kg_service = KnowledgeGraphService()
        self.queries = KnowledgeGraphQueries()
        
    async def test_create_operations(self):
        """Test create operations"""
        logger.info("Testing Create Operations...")
        
        try:
            # Create substances
            substances_data = [
                {
                    "name": "Sulfuric Acid",
                    "formula": "H2SO4",
                    "cas_number": "7664-93-9",
                    "molecular_weight": 98.08,
                    "density": 1.84,
                    "melting_point": 10.31,
                    "boiling_point": 337.0
                },
                {
                    "name": "Sodium Hydroxide",
                    "formula": "NaOH",
                    "cas_number": "1310-73-2",
                    "molecular_weight": 40.00,
                    "density": 2.13,
                    "melting_point": 318.0,
                    "boiling_point": 1388.0
                },
                {
                    "name": "Methanol",
                    "formula": "CH3OH",
                    "cas_number": "67-56-1",
                    "molecular_weight": 32.04,
                    "density": 0.792,
                    "melting_point": -97.6,
                    "boiling_point": 64.7
                }
            ]
            
            created_substances = []
            for substance_data in substances_data:
                substance = await self.kg_service.create_substance(substance_data)
                created_substances.append(substance)
                logger.info(f"Created substance: {substance.name} (ID: {substance.id})")
            
            # Create containers
            containers_data = [
                {
                    "name": "Glass Bottle 1L",
                    "material": "glass",
                    "capacity": 1.0,
                    "pressure_rating": 1.0,
                    "temperature_rating": 100.0,
                    "manufacturer": "LabSupply Co."
                },
                {
                    "name": "Steel Drum 200L",
                    "material": "stainless_steel",
                    "capacity": 200.0,
                    "pressure_rating": 5.0,
                    "temperature_rating": 200.0,
                    "manufacturer": "Industrial Containers Ltd."
                }
            ]
            
            created_containers = []
            for container_data in containers_data:
                container = await self.kg_service.create_container(container_data)
                created_containers.append(container)
                logger.info(f"Created container: {container.name} (ID: {container.id})")
            
            # Create hazards
            hazards_data = [
                {"type": "corrosive", "description": "Causes severe burns"},
                {"type": "toxic", "description": "Harmful if inhaled or ingested"},
                {"type": "flammable", "description": "Easily ignited"}
            ]
            
            created_hazards = []
            for hazard_data in hazards_data:
                hazard = await self.kg_service.create_hazard(hazard_data)
                created_hazards.append(hazard)
                logger.info(f"Created hazard: {hazard.type} (ID: {hazard.id})")
            
            # Create tests
            tests_data = [
                {
                    "name": "Compatibility Test 1",
                    "test_type": "storage",
                    "standard": "ASTM D543",
                    "duration": 24,
                    "temperature": 25.0,
                    "pressure": 1.0,
                    "result": "pass"
                },
                {
                    "name": "Corrosion Test 1",
                    "test_type": "material",
                    "standard": "ISO 9227",
                    "duration": 168,
                    "temperature": 35.0,
                    "pressure": 1.0,
                    "result": "fail"
                }
            ]
            
            created_tests = []
            for test_data in tests_data:
                test = await self.kg_service.create_test(test_data)
                created_tests.append(test)
                logger.info(f"Created test: {test.name} (ID: {test.id})")
            
            # Create relationships
            relationships = [
                # Substance-Hazard relationships
                {"source": created_substances[0].id, "target": created_hazards[0].id, "type": "HAS_HAZARD"},
                {"source": created_substances[1].id, "target": created_hazards[0].id, "type": "HAS_HAZARD"},
                {"source": created_substances[2].id, "target": created_hazards[2].id, "type": "HAS_HAZARD"},
                
                # Substance-Container relationships
                {"source": created_substances[0].id, "target": created_containers[0].id, "type": "STORED_IN"},
                {"source": created_substances[1].id, "target": created_containers[0].id, "type": "STORED_IN"},
                {"source": created_substances[2].id, "target": created_containers[1].id, "type": "STORED_IN"},
                
                # Test relationships
                {"source": created_tests[0].id, "target": created_substances[0].id, "type": "TESTED_ON"},
                {"source": created_tests[1].id, "target": created_substances[1].id, "type": "TESTED_ON"}
            ]
            
            created_relationships = []
            for rel_data in relationships:
                relationship = await self.kg_service.create_relationship(rel_data)
                created_relationships.append(relationship)
                logger.info(f"Created relationship: {rel_data['type']}")
            
            logger.info(f"✅ Create operations completed successfully")
            logger.info(f"Created {len(created_substances)} substances")
            logger.info(f"Created {len(created_containers)} containers")
            logger.info(f"Created {len(created_hazards)} hazards")
            logger.info(f"Created {len(created_tests)} tests")
            logger.info(f"Created {len(created_relationships)} relationships")
            
            return {
                "success": True,
                "substances": len(created_substances),
                "containers": len(created_containers),
                "hazards": len(created_hazards),
                "tests": len(created_tests),
                "relationships": len(created_relationships)
            }
            
        except Exception as e:
            logger.error(f"❌ Create operations error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_query_operations(self):
        """Test query operations"""
        logger.info("Testing Query Operations...")
        
        try:
            # Basic queries
            basic_queries = [
                ("Substance count", "MATCH (s:Substance) RETURN count(s) as count"),
                ("Container count", "MATCH (c:Container) RETURN count(c) as count"),
                ("Hazard count", "MATCH (h:Hazard) RETURN count(h) as count"),
                ("Test count", "MATCH (t:Test) RETURN count(t) as count")
            ]
            
            basic_results = {}
            for name, query in basic_queries:
                result = await self.kg_service.execute_query(query)
                basic_results[name] = result
                logger.info(f"{name}: {result}")
            
            # Complex queries
            complex_queries = [
                ("Substances with hazards", """
                    MATCH (s:Substance)-[:HAS_HAZARD]->(h:Hazard)
                    RETURN s.name, h.type
                    LIMIT 5
                """),
                ("Storage relationships", """
                    MATCH (s:Substance)-[:STORED_IN]->(c:Container)
                    RETURN s.name, c.name, c.material
                    LIMIT 5
                """),
                ("Test results", """
                    MATCH (t:Test)-[:TESTED_ON]->(s:Substance)
                    RETURN t.name, s.name, t.result, t.test_type
                    LIMIT 5
                """),
                ("Hazard distribution", """
                    MATCH (h:Hazard)<-[:HAS_HAZARD]-(s:Substance)
                    RETURN h.type, count(s) as substance_count
                    ORDER BY substance_count DESC
                """)
            ]
            
            complex_results = {}
            for name, query in complex_queries:
                result = await self.kg_service.execute_query(query)
                complex_results[name] = result
                logger.info(f"{name}: {len(result)} results")
            
            # Graph analytics
            analytics_queries = [
                ("Degree centrality", """
                    MATCH (n)
                    RETURN n.name, size((n)--()) as degree
                    ORDER BY degree DESC
                    LIMIT 10
                """),
                ("Path analysis", """
                    MATCH path = (s:Substance)-[:HAS_HAZARD]->(h:Hazard)
                    RETURN s.name, h.type, length(path) as path_length
                    LIMIT 5
                """)
            ]
            
            analytics_results = {}
            for name, query in analytics_queries:
                result = await self.kg_service.execute_query(query)
                analytics_results[name] = result
                logger.info(f"{name}: {len(result)} results")
            
            logger.info(f"✅ Query operations completed successfully")
            
            return {
                "success": True,
                "basic_queries": basic_results,
                "complex_queries": complex_results,
                "analytics_queries": analytics_results
            }
            
        except Exception as e:
            logger.error(f"❌ Query operations error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_update_operations(self):
        """Test update operations"""
        logger.info("Testing Update Operations...")
        
        try:
            # Get a substance to update
            substances = await self.kg_service.get_all_substances()
            if not substances:
                logger.warning("No substances found for update test")
                return {"success": False, "error": "No substances available"}
            
            substance = substances[0]
            
            # Update substance
            update_data = {
                "molecular_weight": 99.0,
                "density": 1.85,
                "notes": "Updated for testing purposes"
            }
            
            updated_substance = await self.kg_service.update_substance(substance.id, update_data)
            logger.info(f"Updated substance: {updated_substance.name}")
            logger.info(f"New molecular weight: {updated_substance.molecular_weight}")
            logger.info(f"New density: {updated_substance.density}")
            
            # Update container
            containers = await self.kg_service.get_all_containers()
            if containers:
                container = containers[0]
                container_update = {
                    "capacity": 1.5,
                    "notes": "Capacity increased"
                }
                
                updated_container = await self.kg_service.update_container(container.id, container_update)
                logger.info(f"Updated container: {updated_container.name}")
                logger.info(f"New capacity: {updated_container.capacity}")
            
            logger.info(f"✅ Update operations completed successfully")
            
            return {
                "success": True,
                "updated_substance": updated_substance.id,
                "updated_container": updated_container.id if 'updated_container' in locals() else None
            }
            
        except Exception as e:
            logger.error(f"❌ Update operations error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_delete_operations(self):
        """Test delete operations"""
        logger.info("Testing Delete Operations...")
        
        try:
            # Get entities to delete
            substances = await self.kg_service.get_all_substances()
            containers = await self.kg_service.get_all_containers()
            tests = await self.kg_service.get_all_tests()
            
            deleted_count = 0
            
            # Delete some tests (less critical data)
            for test in tests[:2]:  # Delete first 2 tests
                await self.kg_service.delete_test(test.id)
                deleted_count += 1
                logger.info(f"Deleted test: {test.name}")
            
            # Delete some containers
            for container in containers[:1]:  # Delete first container
                await self.kg_service.delete_container(container.id)
                deleted_count += 1
                logger.info(f"Deleted container: {container.name}")
            
            # Delete some substances
            for substance in substances[:1]:  # Delete first substance
                await self.kg_service.delete_substance(substance.id)
                deleted_count += 1
                logger.info(f"Deleted substance: {substance.name}")
            
            logger.info(f"✅ Delete operations completed successfully")
            logger.info(f"Deleted {deleted_count} entities")
            
            return {
                "success": True,
                "deleted_count": deleted_count
            }
            
        except Exception as e:
            logger.error(f"❌ Delete operations error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_graph_analytics(self):
        """Test graph analytics operations"""
        logger.info("Testing Graph Analytics...")
        
        try:
            # Node count by type
            node_count_query = """
                MATCH (n)
                RETURN labels(n)[0] as node_type, count(n) as count
                ORDER BY count DESC
            """
            node_counts = await self.kg_service.execute_query(node_count_query)
            
            # Relationship count by type
            rel_count_query = """
                MATCH ()-[r]->()
                RETURN type(r) as relationship_type, count(r) as count
                ORDER BY count DESC
            """
            rel_counts = await self.kg_service.execute_query(rel_count_query)
            
            # Connected components
            components_query = """
                CALL gds.wcc.stream('graph')
                YIELD nodeId, componentId
                RETURN componentId, count(nodeId) as component_size
                ORDER BY component_size DESC
            """
            try:
                components = await self.kg_service.execute_query(components_query)
            except:
                components = [{"componentId": 1, "component_size": "N/A (GDS not available)"}]
            
            # Centrality measures
            centrality_query = """
                MATCH (n)
                RETURN n.name, size((n)--()) as degree_centrality
                ORDER BY degree_centrality DESC
                LIMIT 10
            """
            centrality = await self.kg_service.execute_query(centrality_query)
            
            logger.info(f"✅ Graph analytics completed successfully")
            logger.info(f"Node types: {len(node_counts)}")
            logger.info(f"Relationship types: {len(rel_counts)}")
            logger.info(f"Connected components: {len(components)}")
            logger.info(f"Top centrality nodes: {len(centrality)}")
            
            return {
                "success": True,
                "node_counts": node_counts,
                "relationship_counts": rel_counts,
                "components": components,
                "centrality": centrality
            }
            
        except Exception as e:
            logger.error(f"❌ Graph analytics error: {e}")
            return {"success": False, "error": str(e)}

async def main():
    parser = argparse.ArgumentParser(description="Test Knowledge Graph Operations")
    parser.add_argument("--operation", choices=["create", "query", "update", "delete", "analytics", "all"], 
                       help="Test specific operation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    tester = KnowledgeGraphTester()
    
    if args.operation == "create":
        result = await tester.test_create_operations()
    elif args.operation == "query":
        result = await tester.test_query_operations()
    elif args.operation == "update":
        result = await tester.test_update_operations()
    elif args.operation == "delete":
        result = await tester.test_delete_operations()
    elif args.operation == "analytics":
        result = await tester.test_graph_analytics()
    else:
        # Run all tests
        logger.info("Running all knowledge graph operation tests...")
        
        results = {}
        results["create"] = await tester.test_create_operations()
        results["query"] = await tester.test_query_operations()
        results["update"] = await tester.test_update_operations()
        results["analytics"] = await tester.test_graph_analytics()
        results["delete"] = await tester.test_delete_operations()
        
        # Summary
        successful_ops = sum(1 for r in results.values() if r.get("success", False))
        total_ops = len(results)
        
        logger.info(f"\n{'='*50}")
        logger.info(f"KNOWLEDGE GRAPH OPERATIONS TEST SUMMARY")
        logger.info(f"{'='*50}")
        logger.info(f"Successful operations: {successful_ops}/{total_ops}")
        
        for op, result in results.items():
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            logger.info(f"{op.capitalize()}: {status}")
            if not result.get("success", False):
                logger.error(f"  Error: {result.get('error', 'Unknown error')}")
        
        return results
    
    return result

if __name__ == "__main__":
    asyncio.run(main()) 