# NLP & RAG System - Document to Knowledge Graph Pipeline

## Overview

The NLP & RAG (Retrieval-Augmented Generation) system is a comprehensive pipeline that processes unstructured documents (PDFs, Word documents, images) and extracts structured information to populate the HazardSafe-KG knowledge graph. This system combines natural language processing, computer vision, and knowledge graph technologies to create a powerful document analysis and information extraction platform.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Documents     │    │   NLP & RAG     │    │  Knowledge      │
│   (PDF/Word/    │───▶│   Pipeline      │───▶│  Graph          │
│   Images)       │    │                 │    │  (Neo4j)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Vector Store   │
                       │  (Embeddings)   │
                       └─────────────────┘
```

## Document-to-KG Pipeline

### 1. Document Ingestion
- **Supported Formats**: PDF, Word (.docx), Text (.txt), JSON, Images (.jpg, .png, .tiff)
- **OCR Capabilities**: Text extraction from images using Tesseract
- **Metadata Extraction**: Document properties, page information, tables

### 2. Content Classification
- **Automatic Classification**: Safety, Engineering, Regulatory, Research documents
- **Keyword-based Detection**: Identifies document type based on content analysis

### 3. Entity Recognition
- **Chemical Entities**: Formulas (H2SO4), names, CAS numbers
- **Hazard Entities**: Corrosive, toxic, flammable, explosive
- **Property Entities**: Physical state, color, odor, solubility
- **Safety Entities**: PPE requirements, storage conditions

### 4. Relationship Extraction
- **Chemical-Hazard**: HAS_HAZARD_CLASS relationships
- **Storage Relationships**: STORED_IN, LOCATED_AT
- **Compatibility**: COMPATIBLE_WITH, INCOMPATIBLE_WITH
- **Testing**: TESTED_WITH, ASSESSED_FOR

### 5. Vector Embeddings
- **Text Chunking**: Semantic segmentation of documents
- **Embedding Generation**: Vector representations for semantic search
- **Vector Storage**: Efficient retrieval and similarity search

### 6. Ontology Validation
- **SHACL-like Validation**: Ensures entities conform to schema
- **Chemical Validation**: CAS number format, chemical formula validation
- **Hazard Validation**: Recognized hazard classes and properties

### 7. Knowledge Graph Storage
- **Neo4j Integration**: Graph database for complex relationships
- **Node Creation**: Substances, containers, tests, assessments
- **Relationship Creation**: Semantic connections between entities

## Module Structure

```
nlp_rag/
├── README.md                           # This file
├── __init__.py                         # Module initialization
├── document_to_kg_pipeline.py          # Main pipeline coordinator
├── config/                             # Configuration files
│   ├── __init__.py
│   ├── model_config.py                 # AI model configurations
│   ├── pipeline_config.py              # Pipeline settings
│   └── retriever_config.py             # Retrieval configurations
├── models/                             # AI model implementations
│   ├── __init__.py
│   ├── embedding_models.py             # Vector embedding models
│   ├── llm_models.py                   # Large language models
│   └── retriever_models.py             # Retrieval models
├── processors/                         # Document processing
│   ├── __init__.py
│   ├── document_processor.py           # Document extraction and processing
│   ├── chunking.py                     # Text chunking strategies
│   ├── text_extractor.py               # Text extraction utilities
│   └── vector_store.py                 # Vector database operations
├── information_extraction/             # NLP and entity extraction
│   ├── __init__.py
│   ├── entity_extractor.py             # Named entity recognition
│   ├── relationship_extractor.py       # Relationship extraction
│   └── text_processor.py               # Text preprocessing
├── retrieval/                          # Information retrieval
│   ├── __init__.py
│   ├── retriever.py                    # Document retrieval
│   ├── reranker.py                     # Result reranking
│   └── search.py                       # Search algorithms
├── generation/                         # Response generation
│   ├── __init__.py
│   ├── prompt_templates.py             # LLM prompt templates
│   └── response_generator.py           # Answer generation
└── utils/                              # Utility functions
    ├── __init__.py
    ├── cache.py                        # Caching mechanisms
    └── logging.py                      # Logging utilities
```

## Key Components

### Document Processor (`processors/document_processor.py`)
Handles document ingestion and text extraction from various file formats.

**Features:**
- PDF text extraction with layout preservation
- Word document processing with table extraction
- Image OCR with preprocessing
- Metadata extraction and document structuring

**Usage:**
```python
from nlp_rag.processors.document_processor import DocumentProcessor

processor = DocumentProcessor()
result = processor.process_document("safety_data_sheet.pdf", "safety")
```

### Entity Extractor (`information_extraction/entity_extractor.py`)
Extracts chemical entities, hazards, and properties from text.

**Features:**
- Chemical formula recognition (H2SO4, NaOH)
- CAS number validation
- Hazard classification (corrosive, toxic, flammable)
- Property extraction (physical state, color, odor)

**Usage:**
```python
from nlp_rag.information_extraction.entity_extractor import EntityExtractor

extractor = EntityExtractor()
entities = extractor.extract_entities("H2SO4 is a corrosive acid")
chemical_compounds = extractor.extract_chemical_compounds(text)
```

### Relationship Extractor (`information_extraction/relationship_extractor.py`)
Identifies relationships between extracted entities.

**Features:**
- Chemical-hazard relationships
- Storage and location relationships
- Compatibility relationships
- Testing and assessment relationships

**Usage:**
```python
from nlp_rag.information_extraction.relationship_extractor import RelationshipExtractor

extractor = RelationshipExtractor()
relationships = extractor.extract_relationships(text, entities)
```

### Document-to-KG Pipeline (`document_to_kg_pipeline.py`)
Coordinates the complete pipeline from document ingestion to knowledge graph storage.

**Features:**
- End-to-end document processing
- Automatic document classification
- Batch processing capabilities
- Error handling and logging

**Usage:**
```python
from nlp_rag.document_to_kg_pipeline import DocumentToKGPipeline

pipeline = DocumentToKGPipeline()
await pipeline.initialize()

result = await pipeline.process_document_to_kg("document.pdf", "safety")
```

## API Endpoints

### Document Processing
- `POST /nlp_rag/document-to-kg` - Process single document
- `POST /nlp_rag/batch-document-to-kg` - Process multiple documents
- `GET /nlp_rag/document-pipeline-status` - Get pipeline status

### RAG System
- `POST /nlp_rag/query` - Query the RAG system
- `GET /nlp_rag/documents` - Get processed documents
- `POST /nlp_rag/upload` - Upload documents to RAG system

### NLP Analysis
- `POST /nlp_rag/nlp/analyze` - Analyze text with NLP
- `POST /nlp_rag/nlp/upload-analyze` - Upload and analyze text
- `GET /nlp_rag/nlp/models` - Get available NLP models

## Configuration

### Model Configuration (`config/model_config.py`)
Configure AI models for different tasks:

```python
LLM_MODELS = {
    "gpt-4": {"api_key": "your-key", "model": "gpt-4"},
    "gpt-3.5-turbo": {"api_key": "your-key", "model": "gpt-3.5-turbo"},
    "claude-3": {"api_key": "your-key", "model": "claude-3-sonnet"}
}

EMBEDDING_MODELS = {
    "text-embedding-ada-002": {"api_key": "your-key"},
    "all-MiniLM-L6-v2": {"model": "sentence-transformers/all-MiniLM-L6-v2"}
}
```

### Pipeline Configuration (`config/pipeline_config.py`)
Configure pipeline behavior:

```python
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_TOKENS = 4096
CONFIDENCE_THRESHOLD = 0.8
```

## Usage Examples

### Example 1: Process Safety Data Sheet
```python
from nlp_rag.document_to_kg_pipeline import document_pipeline

# Initialize pipeline
await document_pipeline.initialize()

# Process PDF safety data sheet
result = await document_pipeline.process_document_to_kg(
    "sulfuric_acid_sds.pdf", 
    "safety"
)

print(f"Extracted {result['summary']['entities_extracted']} entities")
print(f"Created {result['summary']['kg_nodes_created']} KG nodes")
```

### Example 2: Batch Process Documents
```python
# Process multiple documents
file_paths = [
    "chemical_safety.pdf",
    "storage_guidelines.docx", 
    "test_protocols.pdf"
]

result = await document_pipeline.batch_process_documents(
    file_paths, 
    "auto"
)

print(f"Successfully processed {result['successful']} documents")
```

### Example 3: Query RAG System
```python
import requests

# Query the RAG system
response = requests.post("/nlp_rag/query", json={
    "question": "What containers are suitable for storing sulfuric acid?",
    "context_type": "safety",
    "max_results": 5,
    "llm_model": "gpt-3.5-turbo"
})

print(response.json()["answer"])
```

## Dependencies

### Required Packages
```bash
pip install fastapi uvicorn
pip install PyPDF2 pdfplumber python-docx
pip install opencv-python pillow pytesseract
pip install spacy nltk transformers
pip install sentence-transformers
pip install neo4j
pip install numpy pandas
```

### Optional Dependencies
```bash
# For advanced OCR
pip install easyocr

# For chemical structure recognition
pip install rdkit

# For advanced NLP
pip install transformers torch
```

## Performance Considerations

### Optimization Tips
1. **Batch Processing**: Use batch operations for multiple documents
2. **Caching**: Enable caching for repeated queries
3. **Model Selection**: Choose appropriate models for your use case
4. **Chunking**: Optimize chunk size for your document types
5. **Vector Storage**: Use efficient vector databases for large datasets

### Memory Management
- Process documents in batches to manage memory usage
- Use streaming for large documents
- Implement cleanup procedures for temporary files

## Error Handling

The pipeline includes comprehensive error handling:

- **File Format Errors**: Unsupported file types
- **Processing Errors**: OCR failures, extraction errors
- **Validation Errors**: Invalid entities or relationships
- **Storage Errors**: Database connection issues

All errors are logged and returned with descriptive messages.

## Monitoring and Logging

### Logging Configuration
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Key Metrics
- Document processing time
- Entity extraction accuracy
- Knowledge graph population statistics
- Vector embedding quality

## Contributing

When contributing to the NLP & RAG system:

1. **Follow the existing code structure**
2. **Add comprehensive tests** for new features
3. **Update documentation** for API changes
4. **Use type hints** for all functions
5. **Follow PEP 8** coding standards

## Troubleshooting

### Common Issues

**OCR Not Working**
- Ensure Tesseract is installed: `apt-get install tesseract-ocr`
- Check image quality and preprocessing

**Entity Extraction Poor Performance**
- Verify spaCy model is installed: `python -m spacy download en_core_web_sm`
- Check text preprocessing quality

**Knowledge Graph Connection Issues**
- Verify Neo4j is running and accessible
- Check connection credentials in configuration

**Memory Issues**
- Reduce batch size for large documents
- Implement document streaming for very large files

## Future Enhancements

### Planned Features
- **Multi-language Support**: Process documents in multiple languages
- **Advanced OCR**: Better image preprocessing and text recognition
- **Chemical Structure Recognition**: Extract molecular structures from images
- **Real-time Processing**: Stream processing for live documents
- **Advanced Analytics**: Document similarity and trend analysis

### Integration Opportunities
- **External APIs**: Integrate with chemical databases
- **Machine Learning**: Custom entity recognition models
- **Cloud Storage**: Support for cloud document storage
- **Workflow Automation**: Integration with business processes

---

For more information, see the main [HazardSafe-KG README](../README.md) or contact the development team. 