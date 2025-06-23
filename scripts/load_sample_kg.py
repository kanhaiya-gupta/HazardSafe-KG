#!/usr/bin/env python3
"""
Script to load sample knowledge graph data into Neo4j database.
This script demonstrates how to populate the HazardSafe-KG system with sample data.
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kg.neo4j.database import Neo4jDatabase

def load_sample_data():
    """Load sample knowledge graph data into Neo4j."""
    
    print("🚀 Loading sample knowledge graph data into Neo4j...")
    
    try:
        # Initialize database connection
        db = Neo4jDatabase()
        
        # Check if database is connected
        if not db.is_connected():
            print("❌ Failed to connect to Neo4j database")
            print("Please ensure Neo4j is running and accessible")
            return False
        
        print("✅ Connected to Neo4j database")
        
        # Load the Cypher script
        cypher_file = project_root / "data" / "kg" / "load_sample_data.cypher"
        
        if not cypher_file.exists():
            print(f"❌ Cypher script not found: {cypher_file}")
            return False
        
        print(f"📖 Reading Cypher script from: {cypher_file}")
        
        with open(cypher_file, 'r', encoding='utf-8') as f:
            cypher_script = f.read()
        
        # Split the script into individual statements
        statements = [stmt.strip() for stmt in cypher_script.split(';') if stmt.strip()]
        
        print(f"📝 Found {len(statements)} Cypher statements to execute")
        
        # Execute each statement
        for i, statement in enumerate(statements, 1):
            if statement and not statement.startswith('//'):
                try:
                    print(f"  [{i}/{len(statements)}] Executing: {statement[:50]}...")
                    result = db.execute_cypher(statement)
                    print(f"    ✅ Statement executed successfully")
                except Exception as e:
                    print(f"    ❌ Error executing statement: {e}")
                    print(f"    Statement: {statement}")
                    return False
        
        print("✅ All Cypher statements executed successfully")
        
        # Verify the data was loaded
        print("🔍 Verifying loaded data...")
        
        # Count nodes by type
        node_counts = db.execute_cypher("""
            MATCH (n) 
            RETURN labels(n) as NodeType, count(n) as Count 
            ORDER BY NodeType
        """)
        
        print("📊 Node counts by type:")
        for record in node_counts:
            node_type = record['NodeType'][0] if record['NodeType'] else 'Unknown'
            count = record['Count']
            print(f"  - {node_type}: {count} nodes")
        
        # Count relationships by type
        relationship_counts = db.execute_cypher("""
            MATCH ()-[r]->()
            RETURN type(r) as RelationshipType, count(r) as Count 
            ORDER BY RelationshipType
        """)
        
        print("📊 Relationship counts by type:")
        for record in relationship_counts:
            rel_type = record['RelationshipType']
            count = record['Count']
            print(f"  - {rel_type}: {count} relationships")
        
        print("✅ Sample knowledge graph data loaded successfully!")
        print("\n🎯 Sample data includes:")
        print("  - 5 Chemical substances (H2SO4, NaOH, HCl, Toluene, Acetone)")
        print("  - 2 Hazard classes (Corrosive, Flammable)")
        print("  - 2 Regulations (OSHA, EPA)")
        print("  - 2 Storage locations (Lab, Warehouse)")
        print("  - 2 PPE types (Gloves, Goggles)")
        print("  - 2 Procedures (Spill Response, Waste Disposal)")
        print("  - 30 relationships connecting all components")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading sample data: {e}")
        return False

def main():
    """Main function to run the sample data loader."""
    
    print("=" * 60)
    print("HazardSafe-KG Sample Knowledge Graph Data Loader")
    print("=" * 60)
    
    success = load_sample_data()
    
    if success:
        print("\n🎉 Sample data loading completed successfully!")
        print("\n📋 Next steps:")
        print("  1. Open the web interface to explore the knowledge graph")
        print("  2. Try the example queries in the Knowledge Graph section")
        print("  3. Use the interactive visualization to explore relationships")
        print("  4. Test the RAG system with sample documents")
    else:
        print("\n💥 Sample data loading failed!")
        print("\n🔧 Troubleshooting:")
        print("  1. Ensure Neo4j is running and accessible")
        print("  2. Check database connection settings")
        print("  3. Verify the Cypher script syntax")
        print("  4. Check Neo4j logs for detailed error messages")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 