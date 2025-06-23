# Document to Knowledge Graph Pipeline

## Overview

The Document to Knowledge Graph Pipeline is a comprehensive system that transforms structured data files (CSV, Excel, JSON) into a Neo4j knowledge graph. This pipeline automates the process of entity extraction, relationship mapping, and knowledge graph creation for hazardous substance management.

## Features

### 🚀 **5-Step Pipeline Process**
1. **Document Upload & Validation** - Upload and validate CSV, Excel, and JSON files
2. **Data Parsing & Structure Analysis** - Parse data and analyze structure for entity/relationship identification
3. **Entity Extraction & Classification** - Extract and classify entities from structured data
4. **Relationship Mapping & Validation** - Map relationships between entities and validate consistency
5. **Knowledge Graph Storage** - Store entities and relationships in Neo4j knowledge graph

### 📁 **Supported File Formats**
- **CSV**: Comma-separated values with headers
- **Excel**: .xlsx and .xls files with multiple sheets
- **JSON**: Structured JSON data arrays or objects

### 🔧 **Advanced Features**
- **Automatic Entity Detection**: Intelligent identification of entities and their properties
- **Relationship Mapping**: Automatic mapping of relationships between entities
- **Data Validation**: Comprehensive validation of data quality and consistency
- **Quality Assessment**: Quality metrics and scoring for processed data
- **Neo4j Integration**: Direct storage in Neo4j graph database
- **Real-time Processing**: Live pipeline status and progress tracking

## Architecture

### Pipeline Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Document      │    │   Data Parsing  │    │   Entity        │
│   Upload        │───▶│   & Analysis    │───▶│   Extraction    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Relationship  │    │   Quality       │    │   Neo4j         │
│   Mapping       │───▶│   Assessment    │───▶│   Storage       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow

1. **Input Processing**: Files are uploaded and validated for format and structure
2. **Schema Analysis**: Automatic detection of data schema and relationships
3. **Entity Recognition**: Identification of entities, properties, and types
4. **Relationship Discovery**: Mapping of relationships between entities
5. **Quality Validation**: Assessment of data quality and consistency
6. **Graph Creation**: Generation of Cypher queries for Neo4j
7. **Storage**: Execution of queries to create knowledge graph

## Usage

### Web Interface

1. **Access Pipeline**: Navigate to `/nlp_rag/pipeline`
2. **Upload Files**: Drag and drop or browse for CSV, Excel, or JSON files
3. **Configure Settings**: Set entity detection, relationship mapping, and validation options
4. **Run Pipeline**: Click "Run Pipeline" to start the transformation process
5. **Monitor Progress**: Track pipeline progress through the 5-step visualization
6. **View Results**: Examine created entities, relationships, and quality metrics

### API Endpoints

#### Upload Documents
```http
POST /nlp_rag/pipeline/upload
Content-Type: multipart/form-data

files: [file1.csv, file2.xlsx, file3.json]
```

#### Preview Documents
```http
POST /nlp_rag/pipeline/preview
Content-Type: application/json

{
  "files": ["chemicals.csv", "containers.json"]
}
```

#### Run Pipeline
```http
POST /nlp_rag/pipeline/run
Content-Type: application/json

{
  "entity_detection": "auto",
  "relationship_mapping": "auto",
  "data_validation": "standard",
  "output_format": "neo4j"
}
```

#### Check Status
```http
GET /nlp_rag/pipeline/status
```

### Configuration Options

#### Entity Detection Methods
- **Auto-detect**: Automatic entity identification based on data patterns
- **Column Mapping**: Manual mapping of columns to entity types
- **NLP Extraction**: Natural language processing for entity extraction
- **Rule-based**: Custom rules for entity identification

#### Relationship Mapping
- **Auto-detect**: Automatic relationship discovery
- **Foreign Key Detection**: Based on key relationships in data
- **Semantic Analysis**: Semantic relationship identification
- **Custom Mapping**: Manual relationship definition

#### Data Validation Levels
- **Basic**: Essential validation checks
- **Standard**: Comprehensive validation with quality metrics
- **Strict**: Rigorous validation with detailed error reporting
- **Custom Rules**: User-defined validation rules

#### Output Formats
- **Neo4j Graph**: Direct storage in Neo4j database
- **Cypher Scripts**: Generated Cypher queries for manual execution
- **RDF Triples**: RDF format for semantic web applications
- **JSON-LD**: JSON-LD format for linked data

## Sample Data

### CSV Example (chemicals.csv)
```csv
chemical_name,chemical_formula,molecular_weight,flash_point,boiling_point,storage_container,risk_level
Sulfuric Acid,H2SO4,98.08,None,337,Polyethylene,High
Hydrochloric Acid,HCl,36.46,None,110,Glass,High
Sodium Hydroxide,NaOH,40.00,None,1388,Polyethylene,Medium
```

### JSON Example (containers.json)
```json
[
  {
    "container_id": "CONT001",
    "container_type": "Polyethylene",
    "capacity_liters": 100,
    "chemical_compatibility": ["Sulfuric Acid", "Hydrochloric Acid"],
    "manufacturer": "ChemSafe Inc"
  }
]
```

## Pipeline Results

### Success Metrics
- **Entities Created**: Number of entities extracted and stored
- **Relationships Created**: Number of relationships mapped
- **Quality Score**: Overall data quality assessment (0-100%)
- **Processing Time**: Total pipeline execution time
- **Error Rate**: Percentage of records with validation errors

### Output Structure
```json
{
  "overall_success": true,
  "quality_score": 0.95,
  "total_entities_created": 150,
  "total_relationships_created": 300,
  "step1_upload": {
    "success": true,
    "files_processed": 3,
    "records_processed": 1000
  },
  "step2_parsing": {
    "success": true,
    "entities_extracted": 150,
    "entity_types": ["Chemical", "Container", "Procedure"]
  },
  "step3_entities": {
    "success": true,
    "entities_extracted": 150,
    "entity_types": ["Chemical", "Container", "Procedure"]
  },
  "step4_relationships": {
    "success": true,
    "relationships_mapped": 300,
    "relationship_types": ["STORED_IN", "COMPATIBLE_WITH", "REQUIRES"]
  },
  "step5_storage": {
    "success": true,
    "nodes_created": 150,
    "edges_created": 300
  }
}
```

## Error Handling

### Common Errors
- **Invalid File Format**: Unsupported file type or corrupted file
- **Schema Mismatch**: Inconsistent data structure across files
- **Validation Failures**: Data quality issues or constraint violations
- **Neo4j Connection**: Database connectivity or permission issues

### Error Recovery
- **Automatic Retry**: Failed steps are automatically retried
- **Partial Processing**: Pipeline continues with valid data
- **Error Reporting**: Detailed error messages and suggestions
- **Rollback Support**: Ability to rollback failed operations

## Performance Optimization

### Processing Speed
- **Parallel Processing**: Multiple files processed concurrently
- **Batch Operations**: Bulk operations for improved performance
- **Memory Management**: Efficient memory usage for large datasets
- **Caching**: Cached results for repeated operations

### Scalability
- **Horizontal Scaling**: Support for multiple processing nodes
- **Load Balancing**: Distribution of processing load
- **Resource Management**: Dynamic resource allocation
- **Queue Management**: Job queuing for high-volume processing

## Monitoring and Logging

### Pipeline Monitoring
- **Real-time Status**: Live pipeline progress tracking
- **Performance Metrics**: Processing time and throughput
- **Resource Usage**: CPU, memory, and disk usage
- **Error Tracking**: Comprehensive error logging and reporting

### Logging Levels
- **DEBUG**: Detailed processing information
- **INFO**: General pipeline status and progress
- **WARNING**: Non-critical issues and recommendations
- **ERROR**: Critical errors requiring attention

## Integration

### Neo4j Integration
- **Direct Connection**: Native Neo4j driver integration
- **Transaction Support**: ACID-compliant transaction handling
- **Index Management**: Automatic index creation and optimization
- **Query Optimization**: Optimized Cypher query generation

### External Systems
- **REST API**: Standard REST API for external integration
- **Webhook Support**: Real-time notifications for pipeline events
- **Export Formats**: Multiple export formats for downstream systems
- **Authentication**: Secure authentication and authorization

## Security

### Data Protection
- **File Validation**: Comprehensive file security validation
- **Access Control**: Role-based access control
- **Data Encryption**: Encryption for sensitive data
- **Audit Logging**: Complete audit trail for all operations

### Compliance
- **GDPR Compliance**: Data protection and privacy compliance
- **Industry Standards**: Compliance with industry-specific regulations
- **Security Best Practices**: Implementation of security best practices
- **Regular Audits**: Regular security audits and assessments

## Troubleshooting

### Common Issues

#### Pipeline Fails to Start
- Check file format and size limits
- Verify Neo4j connection and permissions
- Review system resource availability

#### Low Quality Scores
- Validate input data quality
- Review entity detection configuration
- Check relationship mapping rules

#### Performance Issues
- Optimize file sizes and formats
- Review system resource allocation
- Consider parallel processing options

### Support Resources
- **Documentation**: Comprehensive documentation and guides
- **Error Messages**: Detailed error messages with solutions
- **Community Support**: Community forums and discussions
- **Technical Support**: Direct technical support for enterprise users

## Future Enhancements

### Planned Features
- **Machine Learning**: ML-based entity and relationship extraction
- **Multi-language Support**: Support for multiple languages
- **Advanced Analytics**: Advanced analytics and insights
- **Real-time Processing**: Real-time data processing capabilities

### Roadmap
- **Q1 2024**: Enhanced ML capabilities
- **Q2 2024**: Multi-language support
- **Q3 2024**: Advanced analytics
- **Q4 2024**: Real-time processing

## Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up Neo4j database
4. Configure environment variables
5. Run tests: `python -m pytest tests/`

### Code Standards
- **Python**: PEP 8 style guide
- **Documentation**: Comprehensive docstrings and comments
- **Testing**: Unit and integration tests
- **Code Review**: Peer review process for all changes

### Testing
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end pipeline testing
- **Performance Tests**: Load and stress testing
- **Security Tests**: Security vulnerability testing

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions, issues, or contributions:
- **Email**: support@hazardsafe-kg.com
- **GitHub**: https://github.com/hazardsafe-kg
- **Documentation**: https://docs.hazardsafe-kg.com 