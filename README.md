# HazardSafe-KG: Unified Safety Analysis Platform

A comprehensive software platform for structured analysis and processing of safety-relevant technical documents in the field of hazardous substances. The platform integrates ontology management, knowledge graph generation, retrieval-augmented generation, and validation systems for comprehensive safety analysis.

## 🏗️ Architecture Overview

```
HazardSafe-KG/
├── webapp/                 # FastAPI GUI hub
│   ├── app.py             # Main FastAPI application
│   ├── ontology/          # Ontology management module
│   ├── kg/               # Knowledge Graph module
│   ├── rag/              # RAG system module
│   ├── static/           # CSS, JS, and assets
│   └── templates/        # HTML templates
├── ontology/             # Ontology source files
├── kg/                   # Knowledge Graph storage
├── ingestion/            # Document ingestion pipeline
├── validation/           # Safety validation rules
├── data/                 # Data storage
├── tests/                # Test suite
└── main.py              # Application entry point
```

## 🧠 Module 1: Ontology & Knowledge Graph

### Overview
The ontology module provides semantic modeling of safety concepts using OWL, RDF, and SHACL technologies. It enables structured representation of hazardous substances, containers, tests, and risk assessments.

### Key Features
- **Class Management**: Create and manage ontology classes (HazardousSubstance, Container, SafetyTest, RiskAssessment)
- **Property Definition**: Define data properties with domains, ranges, and constraints
- **Relationship Modeling**: Establish semantic relationships between concepts
- **Validation**: SHACL-based constraint validation
- **Export**: OWL/RDF and SHACL export capabilities

### API Endpoints
```
GET  /ontology/           # Ontology dashboard
GET  /ontology/stats      # Get ontology statistics
GET  /ontology/classes    # List all classes
POST /ontology/classes    # Create new class
GET  /ontology/properties # List all properties
POST /ontology/properties # Create new property
GET  /ontology/relationships # List all relationships
POST /ontology/relationships # Create new relationship
GET  /ontology/export/owl # Export as OWL/RDF
GET  /ontology/export/shacl # Export SHACL constraints
GET  /ontology/validate   # Validate ontology consistency
```

### Sample Ontology Structure
```turtle
@prefix hs: <http://hazardsafe-kg.org/ontology#> .

hs:HazardousSubstance
    a owl:Class ;
    rdfs:label "Hazardous Substance" ;
    rdfs:comment "A chemical substance that poses risks to health, safety, or the environment" .

hs:Container
    a owl:Class ;
    rdfs:label "Container" ;
    rdfs:comment "A vessel designed to safely store and transport hazardous substances" .

hs:stored_in
    a owl:ObjectProperty ;
    rdfs:domain hs:HazardousSubstance ;
    rdfs:range hs:Container ;
    rdfs:label "stored in" .
```

## 📊 Module 2: Knowledge Graph

### Overview
The knowledge graph module provides interactive exploration and querying of safety data using Neo4j and graph visualization. It enables complex relationship analysis and safety insights discovery.

### Key Features
- **Interactive Visualization**: D3.js-based graph visualization with zoom, pan, and node interaction
- **Multi-Query Support**: Cypher, SPARQL, and natural language queries
- **Path Finding**: Discover connections between safety entities
- **Search & Filter**: Advanced search with node type filtering
- **Recommendations**: AI-powered entity recommendations
- **Export**: Graph data export in multiple formats

### API Endpoints
```
GET  /kg/                 # KG dashboard
GET  /kg/stats           # Get KG statistics
GET  /kg/nodes           # List nodes (with optional filtering)
GET  /kg/relationships   # List relationships
POST /kg/query           # Execute graph queries
GET  /kg/visualize       # Get visualization data
GET  /kg/node/{id}       # Get specific node details
GET  /kg/search          # Search nodes
GET  /kg/path            # Find paths between nodes
GET  /kg/recommendations # Get entity recommendations
```

### Sample Cypher Queries
```cypher
// Find all hazardous substances
MATCH (n:HazardousSubstance) RETURN n

// Find substances and their containers
MATCH (s:HazardousSubstance)-[r:STORED_IN]->(c:Container) 
RETURN s, r, c

// Find safety tests for containers
MATCH (c:Container)-[r:VALIDATED_BY]->(t:SafetyTest) 
RETURN c, r, t
```

### Graph Visualization Features
- **Force-directed layout** with D3.js
- **Color-coded nodes** by entity type
- **Interactive relationships** with labels
- **Node details modal** with properties
- **Zoom and pan** controls
- **Responsive design** for different screen sizes

## 🔍 Module 3: Retrieval-Augmented Generation (RAG)

### Overview
The RAG module provides AI-powered document analysis and question answering using vector search and language models. It enables intelligent extraction of safety information from technical documents.

### Key Features
- **Document Processing**: Upload and process safety documents (PDFs, technical specs, SDS)
- **Vector Search**: Semantic document retrieval using embeddings
- **Question Answering**: AI-powered responses with source citations
- **Safety Validation**: Automated validation against safety standards
- **Query History**: Track and analyze user queries
- **Smart Suggestions**: Context-aware query suggestions

### API Endpoints
```
GET  /rag/               # RAG dashboard
GET  /rag/stats          # Get RAG statistics
GET  /rag/documents      # List documents
POST /rag/upload         # Upload new document
POST /rag/query          # Ask questions
POST /rag/validate       # Validate safety requirements
GET  /rag/search         # Search documents
GET  /rag/history        # Query history
GET  /rag/suggestions    # Query suggestions
```

### Document Types Supported
- **Safety Data Sheets (SDS)**: Chemical safety information
- **Technical Specifications**: Container and equipment specs
- **Test Protocols**: Safety testing procedures
- **Regulatory Documents**: Compliance requirements
- **Risk Assessments**: Safety evaluation reports

### Sample RAG Queries
```
Q: "What containers are suitable for storing sulfuric acid?"
A: "Polyethylene containers are suitable for storing sulfuric acid. These containers have a pressure rating of 2.0 bar and temperature rating of 60°C. The material is resistant to most acids and bases."

Q: "What safety measures are required for chemical storage?"
A: "Safety measures include proper ventilation, PPE (personal protective equipment), and spill containment procedures. Storage areas must have proper ventilation and emergency response equipment."
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- FastAPI
- Uvicorn
- Neo4j (for production)
- Vector database (Pinecone, Weaviate, etc.)
- LLM API (OpenAI, Anthropic, etc.)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd HazardSafe-KG

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the application
python main.py
```

### Configuration
Create a `.env` file with the following variables:
```env
# Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Vector Database
VECTOR_DB_URL=your_vector_db_url
VECTOR_DB_API_KEY=your_api_key

# LLM API
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Application
DEBUG=True
SECRET_KEY=your_secret_key
```

## 🔧 Development

### Project Structure
```
HazardSafe-KG/
├── webapp/
│   ├── app.py              # Main FastAPI app
│   ├── ontology/
│   │   └── routes.py       # Ontology API routes
│   ├── kg/
│   │   └── routes.py       # Knowledge Graph API routes
│   ├── rag/
│   │   └── routes.py       # RAG API routes
│   ├── static/
│   │   ├── css/
│   │   │   └── main.css    # Main styles
│   │   └── js/
│   │       ├── main.js     # Common utilities
│   │       ├── ontology.js # Ontology management
│   │       └── kg.js       # Knowledge Graph visualization
│   └── templates/
│       ├── index.html      # Main dashboard
│       ├── ontology/
│       │   └── index.html  # Ontology management UI
│       ├── kg/
│       │   └── index.html  # Knowledge Graph UI
│       └── rag/
│           └── index.html  # RAG system UI
├── ontology/
│   └── src/                # Ontology source files
├── kg/
│   └── neo4j/              # Neo4j configuration
├── ingestion/
│   └── haz_ingest.py       # Document ingestion
├── validation/
│   └── rules.py            # Safety validation rules
├── data/                   # Data storage
├── tests/                  # Test suite
├── main.py                 # Application entry point
└── README.md              # This file
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific module tests
pytest tests/test_ontology.py
pytest tests/test_kg.py
pytest tests/test_rag.py
```

### API Documentation
Once the application is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## 🔒 Security & Authentication

### Current State
- Basic CORS configuration
- No authentication implemented
- Development mode enabled

### Planned Security Features
- JWT-based authentication
- Role-based access control
- API rate limiting
- Input validation and sanitization
- Audit logging

## 🚧 Roadmap

### Phase 1: Core Platform ✅ COMPLETED
- ✅ Basic FastAPI structure with modular architecture
- ✅ Ontology management UI with multi-format support (TTL, OWL, RDF/XML, JSON-LD, N-Triples, Notation3, TriG, SHACL)
- ✅ Knowledge Graph visualization with D3.js and interactive features
- ✅ RAG system interface with document upload and query capabilities
- ✅ Sample data and comprehensive API endpoints
- ✅ Error handling and responsive UI design
- ✅ Neo4j database connection and basic operations
- ✅ Vector store infrastructure (Pinecone, Weaviate, ChromaDB support)

### Phase 2: Real Integrations 🔄 IN PROGRESS
- 🔄 **Neo4j Integration**: ✅ Connected and operational, 🔄 Enhanced with real data and advanced queries
- 🔄 **Vector Database Integration**: ✅ Infrastructure ready, 🔄 Choose and configure primary vector store
- 🔄 **LLM Integration**: 📋 OpenAI/Anthropic API integration for safety analysis
- 🔄 **Document Processing Pipeline**: ✅ Basic structure, 🔄 Enhanced with embedding models
- 🔄 **Advanced Validation Logic**: ✅ SHACL framework, 🔄 Real-time validation and compliance checking

#### Phase 2A: Enhanced Neo4j Integration (Next Priority)
- 📋 Import real hazardous substance data
- 📋 Create comprehensive knowledge graph schema
- 📋 Add advanced Cypher queries for safety analysis
- 📋 Implement path finding and recommendation algorithms

#### Phase 2B: Vector Database Selection & Configuration
- 📋 Choose primary vector store (Pinecone/Weaviate/ChromaDB)
- 📋 Integrate embedding models (OpenAI, HuggingFace)
- 📋 Process safety documents and regulations
- 📋 Create semantic search capabilities

#### Phase 2C: LLM Integration for Safety Analysis
- 📋 OpenAI GPT-4 for safety recommendations
- 📋 Anthropic Claude for risk assessment
- 📋 Context-aware safety queries
- 📋 Automated safety report generation

#### Phase 2D: Advanced Validation & Compliance
- 📋 Real-time ontology validation
- 📋 Custom safety rule validation
- 📋 Automated data validation and quality assurance
- 📋 Regulatory compliance checking

### Phase 3: Advanced Features 📋 PLANNED
- 📋 User authentication and authorization
- 📋 Advanced graph algorithms and analytics
- 📋 Machine learning safety predictions
- 📋 Real-time safety monitoring
- 📋 Performance optimization and scalability

### Phase 4: Production Ready 📋 FUTURE
- 📋 Comprehensive testing suite
- 📋 Deployment automation
- 📋 Monitoring and logging infrastructure
- 📋 Security hardening
- 📋 Documentation and training materials

## 🎯 Current Focus: Phase 2A - Enhanced Neo4j Integration

The platform is now ready for real data integration and advanced knowledge graph operations. The next steps involve:

1. **Data Import**: Import actual hazardous substance databases
2. **Schema Enhancement**: Create comprehensive safety ontologies
3. **Advanced Queries**: Implement safety analysis algorithms
4. **Graph Analytics**: Add path finding and recommendation features

**Ready to proceed with Phase 2A implementation!** 🚀

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Private License

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the development team
- Check the documentation at `/docs` when running the application

## 🙏 Acknowledgments

- FastAPI for the web framework
- D3.js for graph visualization
- Bootstrap for UI components
- Neo4j for graph database
- OpenAI/Anthropic for LLM capabilities
