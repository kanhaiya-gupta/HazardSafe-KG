"""
Tests for Neo4j database functionality.
"""
import pytest
from unittest.mock import Mock, patch
from kg.database import Neo4jDatabase


class TestNeo4jDatabase:
    """Test cases for Neo4jDatabase class."""
    
    @patch('kg.database.GraphDatabase')
    def test_database_initialization(self, mock_graph_db):
        """Test Neo4jDatabase initialization."""
        mock_driver = Mock()
        mock_graph_db.driver.return_value = mock_driver
        
        db = Neo4jDatabase("bolt://localhost:7687", "neo4j", "password")
        assert db is not None
        assert db.uri == "bolt://localhost:7687"
        assert db.username == "neo4j"
        assert db.password == "password"
    
    @patch('kg.database.GraphDatabase')
    def test_connect_success(self, mock_graph_db):
        """Test successful database connection."""
        mock_driver = Mock()
        mock_graph_db.driver.return_value = mock_driver
        
        db = Neo4jDatabase("bolt://localhost:7687", "neo4j", "password")
        result = db.connect()
        assert result is True
        assert db.driver is not None
    
    @patch('kg.database.GraphDatabase')
    def test_connect_failure(self, mock_graph_db):
        """Test database connection failure."""
        mock_graph_db.driver.side_effect = Exception("Connection failed")
        
        db = Neo4jDatabase("bolt://localhost:7687", "neo4j", "password")
        result = db.connect()
        assert result is False
    
    def test_close_connection(self, mock_neo4j_connection):
        """Test closing database connection."""
        db = Neo4jDatabase("bolt://localhost:7687", "neo4j", "password")
        db.driver = mock_neo4j_connection
        
        result = db.close()
        assert result is True
        mock_neo4j_connection.close.assert_called_once()
    
    def test_create_node(self, mock_neo4j_connection):
        """Test creating a node in the database."""
        db = Neo4jDatabase("bolt://localhost:7687", "neo4j", "password")
        db.driver = mock_neo4j_connection
        
        node_data = {
            "label": "HazardousSubstance",
            "properties": {"name": "Methanol", "cas_number": "67-56-1"}
        }
        
        result = db.create_node(node_data)
        assert result is True
        mock_neo4j_connection.run.assert_called_once()
    
    def test_create_relationship(self, mock_neo4j_connection):
        """Test creating a relationship in the database."""
        db = Neo4jDatabase("bolt://localhost:7687", "neo4j", "password")
        db.driver = mock_neo4j_connection
        
        relationship_data = {
            "source_id": "1",
            "target_id": "2",
            "type": "STORED_IN",
            "properties": {"since": "2023-01-01"}
        }
        
        result = db.create_relationship(relationship_data)
        assert result is True
        mock_neo4j_connection.run.assert_called_once()
    
    def test_find_node_by_id(self, mock_neo4j_connection):
        """Test finding a node by ID."""
        db = Neo4jDatabase("bolt://localhost:7687", "neo4j", "password")
        db.driver = mock_neo4j_connection
        
        # Mock the result
        mock_result = Mock()
        mock_result.single.return_value = {"id": "1", "name": "Methanol"}
        mock_neo4j_connection.run.return_value = mock_result
        
        result = db.find_node_by_id("1")
        assert result is not None
        assert result["id"] == "1"
        assert result["name"] == "Methanol"
    
    def test_find_nodes_by_label(self, mock_neo4j_connection):
        """Test finding nodes by label."""
        db = Neo4jDatabase("bolt://localhost:7687", "neo4j", "password")
        db.driver = mock_neo4j_connection
        
        # Mock the result
        mock_result = Mock()
        mock_result.data.return_value = [
            {"id": "1", "name": "Methanol"},
            {"id": "2", "name": "Ethanol"}
        ]
        mock_neo4j_connection.run.return_value = mock_result
        
        result = db.find_nodes_by_label("HazardousSubstance")
        assert len(result) == 2
        assert any(node["name"] == "Methanol" for node in result)
        assert any(node["name"] == "Ethanol" for node in result)
    
    def test_find_nodes_by_property(self, mock_neo4j_connection):
        """Test finding nodes by property."""
        db = Neo4jDatabase("bolt://localhost:7687", "neo4j", "password")
        db.driver = mock_neo4j_connection
        
        # Mock the result
        mock_result = Mock()
        mock_result.data.return_value = [{"id": "1", "name": "Methanol"}]
        mock_neo4j_connection.run.return_value = mock_result
        
        result = db.find_nodes_by_property("HazardousSubstance", "cas_number", "67-56-1")
        assert len(result) == 1
        assert result[0]["name"] == "Methanol"
    
    def test_update_node(self, mock_neo4j_connection):
        """Test updating a node."""
        db = Neo4jDatabase("bolt://localhost:7687", "neo4j", "password")
        db.driver = mock_neo4j_connection
        
        update_data = {
            "id": "1",
            "properties": {"risk_level": "High", "updated_at": "2023-12-01"}
        }
        
        result = db.update_node(update_data)
        assert result is True
        mock_neo4j_connection.run.assert_called_once()
    
    def test_delete_node(self, mock_neo4j_connection):
        """Test deleting a node."""
        db = Neo4jDatabase("bolt://localhost:7687", "neo4j", "password")
        db.driver = mock_neo4j_connection
        
        result = db.delete_node("1")
        assert result is True
        mock_neo4j_connection.run.assert_called_once()
    
    def test_execute_query(self, mock_neo4j_connection):
        """Test executing a custom Cypher query."""
        db = Neo4jDatabase("bolt://localhost:7687", "neo4j", "password")
        db.driver = mock_neo4j_connection
        
        # Mock the result
        mock_result = Mock()
        mock_result.data.return_value = [{"count": 5}]
        mock_neo4j_connection.run.return_value = mock_result
        
        query = "MATCH (n:HazardousSubstance) RETURN count(n) as count"
        result = db.execute_query(query)
        assert result is not None
        assert result[0]["count"] == 5
    
    def test_execute_query_with_parameters(self, mock_neo4j_connection):
        """Test executing a Cypher query with parameters."""
        db = Neo4jDatabase("bolt://localhost:7687", "neo4j", "password")
        db.driver = mock_neo4j_connection
        
        # Mock the result
        mock_result = Mock()
        mock_result.data.return_value = [{"name": "Methanol"}]
        mock_neo4j_connection.run.return_value = mock_result
        
        query = "MATCH (n:HazardousSubstance {cas_number: $cas_number}) RETURN n.name as name"
        parameters = {"cas_number": "67-56-1"}
        
        result = db.execute_query(query, parameters)
        assert result is not None
        assert result[0]["name"] == "Methanol"
    
    def test_get_database_info(self, mock_neo4j_connection):
        """Test getting database information."""
        db = Neo4jDatabase("bolt://localhost:7687", "neo4j", "password")
        db.driver = mock_neo4j_connection
        
        # Mock the result
        mock_result = Mock()
        mock_result.data.return_value = [{"version": "4.4.0"}]
        mock_neo4j_connection.run.return_value = mock_result
        
        info = db.get_database_info()
        assert info is not None
        assert "version" in info
    
    def test_clear_database(self, mock_neo4j_connection):
        """Test clearing all data from database."""
        db = Neo4jDatabase("bolt://localhost:7687", "neo4j", "password")
        db.driver = mock_neo4j_connection
        
        result = db.clear_database()
        assert result is True
        mock_neo4j_connection.run.assert_called_once()
    
    def test_get_statistics(self, mock_neo4j_connection):
        """Test getting database statistics."""
        db = Neo4jDatabase("bolt://localhost:7687", "neo4j", "password")
        db.driver = mock_neo4j_connection
        
        # Mock the result
        mock_result = Mock()
        mock_result.data.return_value = [
            {"label": "HazardousSubstance", "count": 10},
            {"label": "Container", "count": 5}
        ]
        mock_neo4j_connection.run.return_value = mock_result
        
        stats = db.get_statistics()
        assert stats is not None
        assert len(stats) == 2
        assert any(stat["label"] == "HazardousSubstance" for stat in stats) 