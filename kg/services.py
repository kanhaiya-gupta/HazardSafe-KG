"""
Business logic and graph operations for HazardSafe-KG knowledge graph.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import uuid
from .database import Neo4jDatabase
from .models import (
    HazardousSubstance, Container, SafetyTest, RiskAssessment, Location,
    RelationshipType, GRAPH_SCHEMA
)

logger = logging.getLogger(__name__)

class KnowledgeGraphService:
    """Service layer for knowledge graph operations."""
    
    def __init__(self):
        self.db = Neo4jDatabase()
        
    async def initialize(self):
        """Initialize the service and database connection."""
        await self.db.connect()
        await self.db.initialize_schema()
        
    async def close(self):
        """Close database connection."""
        await self.db.disconnect()
        
    # Substance operations
    async def create_substance(self, substance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new hazardous substance node."""
        try:
            substance_id = substance_data.get("id", str(uuid.uuid4()))
            substance_data["id"] = substance_id
            substance_data["created_at"] = datetime.now().isoformat()
            substance_data["updated_at"] = datetime.now().isoformat()
            
            node_id = await self.db.create_node(["HazardousSubstance"], substance_data)
            
            if node_id:
                logger.info(f"Created substance: {substance_data['name']}")
                return {
                    "success": True,
                    "substance_id": node_id,
                    "message": f"Successfully created substance: {substance_data['name']}"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to create substance node"
                }
                
        except Exception as e:
            logger.error(f"Error creating substance: {e}")
            return {
                "success": False,
                "message": f"Error creating substance: {str(e)}"
            }
    
    async def get_substance(self, substance_id: str) -> Optional[Dict[str, Any]]:
        """Get a substance by ID."""
        try:
            result = await self.db.execute_query(
                "MATCH (s:HazardousSubstance {id: $substance_id}) RETURN s",
                {"substance_id": substance_id}
            )
            return result[0]["s"] if result else None
        except Exception as e:
            logger.error(f"Error getting substance: {e}")
            return None
    
    async def search_substances(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search substances by name or chemical formula."""
        try:
            query = """
            MATCH (s:HazardousSubstance)
            WHERE s.name CONTAINS $search_term 
               OR s.chemical_formula CONTAINS $search_term
               OR s.cas_number CONTAINS $search_term
            RETURN s
            LIMIT $limit
            """
            return await self.db.execute_query(query, {
                "search_term": search_term,
                "limit": limit
            })
        except Exception as e:
            logger.error(f"Error searching substances: {e}")
            return []
    
    async def get_substances_by_hazard_class(self, hazard_class: str) -> List[Dict[str, Any]]:
        """Get all substances with a specific hazard class."""
        try:
            query = """
            MATCH (s:HazardousSubstance)
            WHERE s.hazard_class = $hazard_class
            RETURN s
            """
            return await self.db.execute_query(query, {"hazard_class": hazard_class})
        except Exception as e:
            logger.error(f"Error getting substances by hazard class: {e}")
            return []
    
    # Container operations
    async def create_container(self, container_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new container node."""
        try:
            container_id = container_data.get("id", str(uuid.uuid4()))
            container_data["id"] = container_id
            container_data["created_at"] = datetime.now().isoformat()
            container_data["updated_at"] = datetime.now().isoformat()
            
            node_id = await self.db.create_node(["Container"], container_data)
            
            if node_id:
                logger.info(f"Created container: {container_data['name']}")
                return {
                    "success": True,
                    "container_id": node_id,
                    "message": f"Successfully created container: {container_data['name']}"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to create container node"
                }
                
        except Exception as e:
            logger.error(f"Error creating container: {e}")
            return {
                "success": False,
                "message": f"Error creating container: {str(e)}"
            }
    
    async def get_compatible_containers(self, substance_id: str) -> List[Dict[str, Any]]:
        """Get containers compatible with a substance."""
        try:
            # Get substance hazard class
            substance = await self.get_substance(substance_id)
            if not substance:
                return []
            
            hazard_class = substance.get("hazard_class", "")
            
            # Define compatibility rules
            incompatibilities = {
                "corrosive": ["aluminum", "carbon_steel"],
                "oxidizing": ["plastic"],
                "flammable": ["plastic"]  # depending on flash point
            }
            
            incompatible_materials = incompatibilities.get(hazard_class, [])
            
            query = """
            MATCH (c:Container)
            WHERE NOT c.material IN $incompatible_materials
            RETURN c
            """
            return await self.db.execute_query(query, {
                "incompatible_materials": incompatible_materials
            })
        except Exception as e:
            logger.error(f"Error getting compatible containers: {e}")
            return []
    
    # Relationship operations
    async def create_storage_relationship(self, substance_id: str, container_id: str, 
                                        quantity: float = 1.0) -> Dict[str, Any]:
        """Create a STORED_IN relationship between substance and container."""
        try:
            properties = {
                "quantity": quantity,
                "date_stored": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat()
            }
            
            success = await self.db.create_relationship(
                substance_id, container_id, "STORED_IN", properties
            )
            
            if success:
                return {
                    "success": True,
                    "message": f"Created storage relationship between substance {substance_id} and container {container_id}"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to create storage relationship"
                }
                
        except Exception as e:
            logger.error(f"Error creating storage relationship: {e}")
            return {
                "success": False,
                "message": f"Error creating storage relationship: {str(e)}"
            }
    
    async def create_compatibility_relationship(self, substance1_id: str, substance2_id: str,
                                              is_compatible: bool, notes: str = "") -> Dict[str, Any]:
        """Create compatibility relationship between two substances."""
        try:
            relationship_type = (RelationshipType.COMPATIBLE_WITH if is_compatible 
                               else RelationshipType.INCOMPATIBLE_WITH)
            
            properties = {
                "notes": notes,
                "created_at": datetime.now().isoformat()
            }
            
            if is_compatible:
                properties["compatibility_level"] = "safe"
            else:
                properties["incompatibility_reason"] = notes
            
            success = await self.db.create_relationship(
                substance1_id, substance2_id, relationship_type, properties
            )
            
            if success:
                return {
                    "success": True,
                    "message": f"Created compatibility relationship between substances"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to create compatibility relationship"
                }
                
        except Exception as e:
            logger.error(f"Error creating compatibility relationship: {e}")
            return {
                "success": False,
                "message": f"Error creating compatibility relationship: {str(e)}"
            }
    
    # Test operations
    async def create_test(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new safety test node."""
        try:
            test_id = test_data.get("id", str(uuid.uuid4()))
            test_data["id"] = test_id
            test_data["created_at"] = datetime.now().isoformat()
            test_data["updated_at"] = datetime.now().isoformat()
            
            node_id = await self.db.create_node(["SafetyTest"], test_data)
            
            if node_id:
                logger.info(f"Created test: {test_data.get('name', 'Unknown')}")
                return {
                    "success": True,
                    "test_id": node_id,
                    "message": f"Successfully created test: {test_data.get('name', 'Unknown')}"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to create test node"
                }
                
        except Exception as e:
            logger.error(f"Error creating test: {e}")
            return {
                "success": False,
                "message": f"Error creating test: {str(e)}"
            }
    
    async def get_test(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get a test by ID."""
        try:
            result = await self.db.execute_query(
                "MATCH (t:SafetyTest {id: $test_id}) RETURN t",
                {"test_id": test_id}
            )
            return result[0]["t"] if result else None
        except Exception as e:
            logger.error(f"Error getting test: {e}")
            return None
    
    async def search_tests(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search tests by name or type."""
        try:
            query = """
            MATCH (t:SafetyTest)
            WHERE t.name CONTAINS $search_term 
               OR t.test_type CONTAINS $search_term
            RETURN t
            LIMIT $limit
            """
            return await self.db.execute_query(query, {
                "search_term": search_term,
                "limit": limit
            })
        except Exception as e:
            logger.error(f"Error searching tests: {e}")
            return []
    
    # Assessment operations
    async def create_assessment(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new risk assessment node."""
        try:
            assessment_id = assessment_data.get("id", str(uuid.uuid4()))
            assessment_data["id"] = assessment_id
            assessment_data["created_at"] = datetime.now().isoformat()
            assessment_data["updated_at"] = datetime.now().isoformat()
            
            node_id = await self.db.create_node(["RiskAssessment"], assessment_data)
            
            if node_id:
                logger.info(f"Created assessment: {assessment_data.get('title', 'Unknown')}")
                return {
                    "success": True,
                    "assessment_id": node_id,
                    "message": f"Successfully created assessment: {assessment_data.get('title', 'Unknown')}"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to create assessment node"
                }
                
        except Exception as e:
            logger.error(f"Error creating assessment: {e}")
            return {
                "success": False,
                "message": f"Error creating assessment: {str(e)}"
            }
    
    async def get_assessment(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Get an assessment by ID."""
        try:
            result = await self.db.execute_query(
                "MATCH (a:RiskAssessment {id: $assessment_id}) RETURN a",
                {"assessment_id": assessment_id}
            )
            return result[0]["a"] if result else None
        except Exception as e:
            logger.error(f"Error getting assessment: {e}")
            return None
    
    async def search_assessments(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search assessments by title or risk level."""
        try:
            query = """
            MATCH (a:RiskAssessment)
            WHERE a.title CONTAINS $search_term 
               OR a.risk_level CONTAINS $search_term
            RETURN a
            LIMIT $limit
            """
            return await self.db.execute_query(query, {
                "search_term": search_term,
                "limit": limit
            })
        except Exception as e:
            logger.error(f"Error searching assessments: {e}")
            return []
    
    async def create_assessment_relationship(self, substance_id: str, assessment_id: str) -> Dict[str, Any]:
        """Create an ASSESSED_FOR relationship between substance and assessment."""
        try:
            properties = {
                "created_at": datetime.now().isoformat()
            }
            
            success = await self.db.create_relationship(
                substance_id, assessment_id, "ASSESSED_FOR", properties
            )
            
            if success:
                return {
                    "success": True,
                    "message": f"Created assessment relationship between substance {substance_id} and assessment {assessment_id}"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to create assessment relationship"
                }
                
        except Exception as e:
            logger.error(f"Error creating assessment relationship: {e}")
            return {
                "success": False,
                "message": f"Error creating assessment relationship: {str(e)}"
            }

    # Analytics and queries
    async def get_substance_network(self, substance_id: str, depth: int = 2) -> Dict[str, Any]:
        """Get the network of relationships around a substance."""
        try:
            query = f"""
            MATCH path = (s:HazardousSubstance {{id: $substance_id}})-[*1..{depth}]-(related)
            RETURN path
            """
            result = await self.db.execute_query(query, {"substance_id": substance_id})
            
            # Process the result to extract nodes and relationships
            nodes = set()
            relationships = set()
            
            for record in result:
                path = record["path"]
                # Extract nodes and relationships from path
                # This is a simplified version - you might want to process the path more carefully
                nodes.add(str(path.start_node))
                nodes.add(str(path.end_node))
                for rel in path.relationships:
                    relationships.add(str(rel))
            
            return {
                "substance_id": substance_id,
                "nodes": list(nodes),
                "relationships": list(relationships),
                "network_depth": depth
            }
            
        except Exception as e:
            logger.error(f"Error getting substance network: {e}")
            return {
                "substance_id": substance_id,
                "nodes": [],
                "relationships": [],
                "error": str(e)
            }
    
    async def get_risk_analysis(self, substance_id: str) -> Dict[str, Any]:
        """Perform risk analysis for a substance."""
        try:
            # Get substance details
            substance = await self.get_substance(substance_id)
            if not substance:
                return {"error": "Substance not found"}
            
            # Get related assessments
            query = """
            MATCH (s:HazardousSubstance {id: $substance_id})-[:ASSESSED_FOR]->(ra:RiskAssessment)
            RETURN ra
            ORDER BY ra.assessment_date DESC
            LIMIT 5
            """
            assessments = await self.db.execute_query(query, {"substance_id": substance_id})
            
            # Get storage information
            storage_query = """
            MATCH (s:HazardousSubstance {id: $substance_id})-[:STORED_IN]->(c:Container)
            RETURN c
            """
            containers = await self.db.execute_query(storage_query, {"substance_id": substance_id})
            
            # Get compatibility information
            compat_query = """
            MATCH (s:HazardousSubstance {id: $substance_id})-[r:COMPATIBLE_WITH|INCOMPATIBLE_WITH]-(other:HazardousSubstance)
            RETURN type(r) as relationship_type, other.name as other_substance, r.notes as notes
            """
            compatibility = await self.db.execute_query(compat_query, {"substance_id": substance_id})
            
            return {
                "substance": substance,
                "assessments": assessments,
                "storage": containers,
                "compatibility": compatibility,
                "risk_factors": {
                    "hazard_class": substance.get("hazard_class"),
                    "flash_point": substance.get("flash_point"),
                    "boiling_point": substance.get("boiling_point"),
                    "storage_count": len(containers),
                    "assessment_count": len(assessments)
                }
            }
            
        except Exception as e:
            logger.error(f"Error performing risk analysis: {e}")
            return {"error": str(e)}
    
    async def get_graph_statistics(self) -> Dict[str, Any]:
        """Get comprehensive graph statistics."""
        try:
            return await self.db.get_graph_stats()
        except Exception as e:
            logger.error(f"Error getting graph statistics: {e}")
            return {"error": str(e)}
    
    # Batch operations
    async def batch_create_substances(self, substances_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create multiple substances in a batch."""
        results = {
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        for substance_data in substances_data:
            result = await self.create_substance(substance_data)
            if result["success"]:
                results["successful"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(result["message"])
        
        return results
    
    async def batch_create_relationships(self, relationships_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create multiple relationships in a batch."""
        results = {
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        for rel_data in relationships_data:
            rel_type = rel_data.get("type")
            if rel_type == "STORED_IN":
                result = await self.create_storage_relationship(
                    rel_data["substance_id"], 
                    rel_data["container_id"], 
                    rel_data.get("quantity", 1.0)
                )
            elif rel_type in ["COMPATIBLE_WITH", "INCOMPATIBLE_WITH"]:
                result = await self.create_compatibility_relationship(
                    rel_data["substance1_id"],
                    rel_data["substance2_id"],
                    rel_type == "COMPATIBLE_WITH",
                    rel_data.get("notes", "")
                )
            else:
                result = {"success": False, "message": f"Unknown relationship type: {rel_type}"}
            
            if result["success"]:
                results["successful"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(result["message"])
        
        return results 