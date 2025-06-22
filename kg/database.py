"""
Neo4j database operations for HazardSafe-KG knowledge graph.
"""

from typing import Optional, Dict, Any, List
import logging
from neo4j import GraphDatabase, Driver
from neo4j.exceptions import ServiceUnavailable, AuthError
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class Neo4jDatabase:
    """Neo4j database connection and operations."""
    
    def __init__(self):
        self.driver: Optional[Driver] = None
        self.connected = False
        
        # Get configuration from environment or use defaults
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")
        
    async def connect(self) -> bool:
        """Establish connection to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            
            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()
            
            self.connected = True
            logger.info("Successfully connected to Neo4j database")
            return True
            
        except (ServiceUnavailable, AuthError) as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Close Neo4j database connection."""
        if self.driver:
            self.driver.close()
            self.connected = False
            logger.info("Disconnected from Neo4j database")
    
    async def execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results."""
        if not self.connected:
            raise ConnectionError("Not connected to Neo4j database")
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    async def create_node(self, labels: List[str], properties: Dict[str, Any]) -> str:
        """Create a new node with given labels and properties."""
        labels_str = ":".join(labels)
        properties_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
        
        query = f"CREATE (n:{labels_str} {{{properties_str}}}) RETURN n.id as id"
        
        result = await self.execute_query(query, properties)
        return result[0]["id"] if result else None
    
    async def create_relationship(self, start_node_id: str, end_node_id: str, 
                                relationship_type: str, properties: Dict[str, Any] = None) -> bool:
        """Create a relationship between two nodes."""
        properties = properties or {}
        properties_str = ", ".join([f"{k}: ${k}" for k in properties.keys()]) if properties else ""
        
        query = f"""
        MATCH (a), (b)
        WHERE a.id = $start_id AND b.id = $end_id
        CREATE (a)-[r:{relationship_type} {{{properties_str}}}]->(b)
        RETURN r
        """
        
        params = {"start_id": start_node_id, "end_id": end_node_id, **properties}
        result = await self.execute_query(query, params)
        return len(result) > 0
    
    async def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a node by ID."""
        query = "MATCH (n {id: $node_id}) RETURN n"
        result = await self.execute_query(query, {"node_id": node_id})
        return result[0] if result else None
    
    async def get_nodes_by_label(self, label: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get nodes by label."""
        query = f"MATCH (n:{label}) RETURN n LIMIT {limit}"
        return await self.execute_query(query)
    
    async def search_nodes(self, search_term: str, label: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search nodes by text in properties."""
        if label:
            query = f"""
            MATCH (n:{label})
            WHERE any(prop in keys(n) WHERE toString(n[prop]) CONTAINS $search_term)
            RETURN n LIMIT {limit}
            """
        else:
            query = f"""
            MATCH (n)
            WHERE any(prop in keys(n) WHERE toString(n[prop]) CONTAINS $search_term)
            RETURN n LIMIT {limit}
            """
        
        return await self.execute_query(query, {"search_term": search_term})
    
    async def get_graph_stats(self) -> Dict[str, int]:
        """Get knowledge graph statistics."""
        queries = [
            "MATCH (n) RETURN count(n) as nodes",
            "MATCH ()-[r]->() RETURN count(r) as relationships",
            "MATCH (n) RETURN count(distinct labels(n)) as node_types",
            "MATCH ()-[r]->() RETURN count(distinct type(r)) as relationship_types"
        ]
        
        stats = {}
        for query in queries:
            result = await self.execute_query(query)
            if result:
                key = list(result[0].keys())[0]
                stats[key] = result[0][key]
        
        return stats
    
    async def initialize_schema(self):
        """Initialize database schema with constraints and indexes."""
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:HazardousSubstance) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Container) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:SafetyTest) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:RiskAssessment) REQUIRE n.id IS UNIQUE"
        ]
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS FOR (n:HazardousSubstance) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Container) ON (n.material)",
            "CREATE INDEX IF NOT EXISTS FOR (n:SafetyTest) ON (n.test_type)",
            "CREATE INDEX IF NOT EXISTS FOR (n:RiskAssessment) ON (n.risk_level)"
        ]
        
        for constraint in constraints:
            try:
                await self.execute_query(constraint)
            except Exception as e:
                logger.warning(f"Could not create constraint: {e}")
        
        for index in indexes:
            try:
                await self.execute_query(index)
            except Exception as e:
                logger.warning(f"Could not create index: {e}")
    
    async def import_csv_data(self, csv_file: str, node_label: str) -> Dict[str, Any]:
        """Import CSV data into Neo4j."""
        try:
            # Load CSV file
            query = f"""
            LOAD CSV WITH HEADERS FROM 'file:///{csv_file}' AS row
            CREATE (n:{node_label})
            SET n += row
            RETURN count(n) as imported_count
            """
            
            result = await self.execute_query(query)
            imported_count = result[0]["imported_count"] if result else 0
            
            return {
                "success": True,
                "imported_count": imported_count,
                "message": f"Successfully imported {imported_count} {node_label} nodes"
            }
            
        except Exception as e:
            logger.error(f"Error importing CSV data: {e}")
            return {
                "success": False,
                "message": f"Error importing data: {str(e)}"
            }
    
    async def get_path_between_nodes(self, start_id: str, end_id: str, 
                                   max_length: int = 5) -> List[Dict[str, Any]]:
        """Find paths between two nodes."""
        query = f"""
        MATCH path = (start)-[*1..{max_length}]-(end)
        WHERE start.id = $start_id AND end.id = $end_id
        RETURN path
        LIMIT 10
        """
        
        result = await self.execute_query(query, {"start_id": start_id, "end_id": end_id})
        return result
    
    async def get_recommendations(self, node_id: str, relationship_type: str = None, 
                                limit: int = 10) -> List[Dict[str, Any]]:
        """Get recommendations based on node relationships."""
        if relationship_type:
            query = f"""
            MATCH (n)-[r:{relationship_type}]-(related)
            WHERE n.id = $node_id
            RETURN related, count(r) as strength
            ORDER BY strength DESC
            LIMIT {limit}
            """
        else:
            query = f"""
            MATCH (n)-[r]-(related)
            WHERE n.id = $node_id
            RETURN related, type(r) as relationship_type, count(r) as strength
            ORDER BY strength DESC
            LIMIT {limit}
            """
        
        return await self.execute_query(query, {"node_id": node_id})
    
    async def export_graph_data(self, format: str = "json") -> Dict[str, Any]:
        """Export graph data in specified format."""
        try:
            if format == "json":
                # Export nodes and relationships as JSON
                nodes_query = """
                MATCH (n)
                RETURN n
                """
                relationships_query = """
                MATCH ()-[r]->()
                RETURN r
                """
                
                nodes = await self.execute_query(nodes_query)
                relationships = await self.execute_query(relationships_query)
                
                return {
                    "nodes": nodes,
                    "relationships": relationships,
                    "export_time": str(datetime.now())
                }
            else:
                return {
                    "success": False,
                    "message": f"Unsupported export format: {format}"
                }
                
        except Exception as e:
            logger.error(f"Error exporting graph data: {e}")
            return {
                "success": False,
                "message": f"Error exporting data: {str(e)}"
            }

# Global database instance
neo4j_db = Neo4jDatabase()

async def get_database() -> Neo4jDatabase:
    """Get the database instance."""
    return neo4j_db

async def init_database():
    """Initialize database connections."""
    await neo4j_db.connect()
    await neo4j_db.initialize_schema()

async def close_database():
    """Close database connections.""" 