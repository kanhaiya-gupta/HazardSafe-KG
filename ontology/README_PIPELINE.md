# Ontology to Knowledge Graph Pipeline

## Overview

The Ontology to Knowledge Graph Pipeline is a comprehensive 5-step process that transforms TTL ontology files into a structured Neo4j knowledge graph. This pipeline ensures data integrity, validation, and quality throughout the transformation process.

## Pipeline Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Step 1:        │    │  Step 2:        │    │  Step 3:        │    │  Step 4:        │    │  Step 5:        │
│  Ontology       │───▶│  Ontology       │───▶│  SHACL          │───▶│  Data Quality   │───▶│  Knowledge      │
│  File           │    │  Management     │    │  Validation     │    │  Check          │    │  Graph          │
│  Ingestion      │    │                 │    │                 │    │                 │    │  Storage        │
│                 │    │                 │    │                 │    │                 │    │                 │
│ TTL Files       │    │ RDF Graph       │    │ Validated       │    │ High-Quality    │    │ Neo4j           │
│ → RDF Graph     │    │ → Schema +      │    │ Triples         │    │ Data            │    │ Knowledge       │
│                 │    │   SHACL         │    │                 │    │                 │    │ Graph           │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Step-by-Step Process

### Step 1: Ontology File Ingestion
**Input:** TTL, OWL, RDF/XML, JSON-LD files  
**Output:** Parsed RDF graph with triples

**Process:**
- Load ontology files from specified directory
- Parse multiple formats (TTL, OWL, RDF/XML, JSON-LD)
- Create unified RDF graph representation
- Extract metadata and file statistics

**Key Features:**
- Multi-format support
- Batch processing
- Error handling and logging
- File validation

**Example:**
```python
# Load ontology files
success = await ontology_manager.load_ontology_files("data/ontology")
rdf_graph = ontology_manager.graph
print(f"Loaded {len(rdf_graph)} triples")
```

### Step 2: Ontology Management
**Input:** RDF graph from Step 1  
**Output:** Ontology schema + SHACL constraints

**Process:**
- Extract ontology classes and properties
- Identify SHACL shapes and constraints
- Build schema representation
- Validate ontology structure

**Key Features:**
- Schema extraction
- SHACL constraint identification
- Namespace management
- Ontology validation

**Example:**
```python
# Extract schema
schema = await pipeline._extract_ontology_schema()
classes = schema["classes"]
properties = schema["properties"]
shacl_constraints = await pipeline._extract_shacl_constraints()
```

### Step 3: SHACL Validation
**Input:** Extracted entities/relations + SHACL constraints  
**Output:** Ontology-validated RDF triples

**Process:**
- Extract entities and relationships from RDF
- Apply SHACL validation rules
- Validate data against constraints
- Generate validation reports

**Key Features:**
- SHACL shape validation
- Entity validation
- Relationship validation
- Constraint checking

**Example:**
```python
# Validate entities
entities = await pipeline._extract_entities_from_rdf()
for entity in entities:
    validation_result = await pipeline._validate_entity_with_shacl(entity)
    if validation_result["valid"]:
        validated_data.append(entity)
```

### Step 4: Data Quality Check
**Input:** Validated triples from Step 3  
**Output:** High-quality data with quality metrics

**Process:**
- Assess data completeness
- Check data accuracy
- Validate consistency
- Perform compatibility checks

**Key Features:**
- Quality metrics calculation
- Completeness assessment
- Accuracy verification
- Compatibility validation

**Example:**
```python
# Assess quality
quality_metrics = await pipeline._assess_data_quality()
completeness = quality_metrics["completeness"]
accuracy = quality_metrics["accuracy"]
consistency = quality_metrics["consistency"]
quality_score = (completeness * 0.3 + accuracy * 0.4 + consistency * 0.3)
```

### Step 5: Knowledge Graph Storage
**Input:** High-quality data from Step 4  
**Output:** Knowledge graph in Neo4j database

**Process:**
- Convert RDF triples to Neo4j format
- Create nodes and relationships
- Apply data transformations
- Store in Neo4j database

**Key Features:**
- RDF to Neo4j conversion
- Node creation
- Relationship creation
- Batch operations

**Example:**
```python
# Convert and store
kg_data = await pipeline._convert_rdf_to_kg_format()
for entity in kg_data["entities"]:
    if entity["type"] == "HazardousSubstance":
        await kg_service.create_substance(entity["data"])
```

## Implementation

### Core Components

#### 1. OntologyToKGPipeline Class
Main pipeline orchestrator that manages the entire process.

```python
class OntologyToKGPipeline:
    def __init__(self):
        self.ontology_manager = OntologyManager()
        self.kg_service = KnowledgeGraphService()
        self.validator = DataValidator()
        self.rdf_graph = Graph()
        self.shacl_graph = Graph()
        self.validated_triples = []
```

#### 2. Pipeline Execution
```python
async def run_pipeline(self, ontology_directory: str = "data/ontology"):
    # Step 1: Ingestion
    ingestion_result = await self._step1_ontology_ingestion(ontology_directory)
    
    # Step 2: Management
    management_result = await self._step2_ontology_management()
    
    # Step 3: Validation
    validation_result = await self._step3_shacl_validation()
    
    # Step 4: Quality
    quality_result = await self._step4_data_quality_check()
    
    # Step 5: Storage
    storage_result = await self._step5_kg_storage()
    
    return pipeline_results
```

### API Endpoints

#### Run Complete Pipeline
```http
POST /ontology/pipeline/run
Content-Type: application/json

{
    "ontology_directory": "data/ontology"
}
```

#### Validate Only (Steps 1-3)
```http
POST /ontology/pipeline/validate
Content-Type: application/json

{
    "ontology_directory": "data/ontology"
}
```

#### Check Pipeline Status
```http
GET /ontology/pipeline/status
```

### Web Interface

Access the pipeline through the web interface at `/ontology/pipeline` which provides:

- **Pipeline Overview:** Visual representation of the 5 steps
- **Pipeline Controls:** Run, validate, and status check buttons
- **Real-time Status:** Current pipeline status and metrics
- **Step Details:** Detailed information for each step
- **Results Visualization:** Pipeline execution results

## Data Flow

### Input Data Format
The pipeline expects ontology files in the `data/ontology` directory:

```
data/ontology/
├── hazardous_substances.ttl    # Main ontology file
├── shapes/                     # SHACL shapes
│   └── validation_shapes.ttl
├── classes/                    # Class definitions
│   └── substance_classes.ttl
└── README.md                   # Documentation
```

### Sample TTL Ontology
```turtle
@prefix hs: <http://hazardsafe-kg.org/ontology#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Class definition
hs:HazardousSubstance a rdfs:Class ;
    rdfs:label "Hazardous Substance" ;
    rdfs:comment "A substance that poses a risk to health, safety, or the environment" .

# Property definition
hs:chemicalFormula a rdfs:DatatypeProperty ;
    rdfs:label "Chemical Formula" ;
    rdfs:domain hs:HazardousSubstance ;
    rdfs:range xsd:string .

# Instance
hs:SulfuricAcid a hs:HazardousSubstance ;
    hs:name "Sulfuric Acid" ;
    hs:chemicalFormula "H2SO4" ;
    hs:hazardClass "corrosive" .
```

### Output Data Format
The pipeline creates Neo4j nodes and relationships:

```cypher
// Substance node
CREATE (s:HazardousSubstance {
    id: "uuid",
    name: "Sulfuric Acid",
    chemical_formula: "H2SO4",
    hazard_class: "corrosive",
    created_at: "2024-01-15T10:30:00Z"
})

// Container node
CREATE (c:Container {
    id: "uuid",
    name: "Glass Bottle 1L",
    material: "glass",
    capacity: 1.0,
    created_at: "2024-01-15T10:30:00Z"
})

// Storage relationship
CREATE (s)-[:STORED_IN {
    quantity: 1.0,
    date_stored: "2024-01-15T10:30:00Z"
}]->(c)
```

## Validation Rules

### SHACL Constraints
The pipeline supports SHACL validation with constraints like:

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .

hs:HazardousSubstanceShape a sh:NodeShape ;
    sh:targetClass hs:HazardousSubstance ;
    sh:property [
        sh:path hs:name ;
        sh:minCount 1 ;
        sh:datatype xsd:string
    ] ;
    sh:property [
        sh:path hs:hazardClass ;
        sh:in ("corrosive", "flammable", "toxic", "explosive") ;
        sh:minCount 1
    ] .
```

### Business Rules
- Chemical compatibility validation
- Hazard class verification
- Required field validation
- Data type checking

## Quality Metrics

### Quality Dimensions
1. **Completeness:** Percentage of required fields present
2. **Accuracy:** Percentage of accurate data values
3. **Consistency:** Percentage of consistent data across fields
4. **Uniqueness:** Percentage of unique records
5. **Validity:** Percentage of valid data according to rules

### Quality Score Calculation
```python
quality_score = (
    completeness * 0.3 +
    accuracy * 0.4 +
    consistency * 0.3
)
```

## Error Handling

### Common Error Types
1. **File Format Errors:** Invalid ontology file format
2. **Schema Errors:** Missing required classes or properties
3. **Validation Errors:** SHACL constraint violations
4. **Quality Errors:** Data quality below threshold
5. **Storage Errors:** Neo4j connection or transaction failures

### Error Response Format
```json
{
    "success": false,
    "error_type": "validation_error",
    "message": "SHACL validation failed",
    "details": {
        "step": "step3_validation",
        "errors": ["Missing required property 'hazard_class'"]
    }
}
```

## Performance Optimization

### Batch Processing
- Process data in configurable batch sizes
- Use database transactions for consistency
- Implement parallel processing for large datasets

### Memory Management
- Stream large files instead of loading entirely
- Use generators for data processing
- Implement cleanup procedures

### Database Optimization
- Use bulk insert operations
- Create appropriate indexes
- Optimize query patterns

## Monitoring and Logging

### Pipeline Metrics
- **Execution Time:** Time per step and total
- **Success Rate:** Percentage of successful executions
- **Error Rate:** Percentage of failed executions
- **Data Quality:** Quality scores over time
- **Storage Metrics:** Entities and relationships created

### Logging Configuration
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
```

## Usage Examples

### Basic Pipeline Execution
```python
from ontology.ontology_to_kg_pipeline import run_ontology_to_kg_pipeline

# Run complete pipeline
results = await run_ontology_to_kg_pipeline("data/ontology")

if results["overall_success"]:
    print(f"Pipeline completed successfully!")
    print(f"Created {results['total_entities_created']} entities")
    print(f"Created {results['total_relationships_created']} relationships")
    print(f"Quality score: {results['quality_score']}")
else:
    print(f"Pipeline failed: {results['errors']}")
```

### Step-by-Step Execution
```python
from ontology.ontology_to_kg_pipeline import OntologyToKGPipeline

pipeline = OntologyToKGPipeline()
await pipeline.initialize()

# Run individual steps
ingestion_result = await pipeline._step1_ontology_ingestion("data/ontology")
management_result = await pipeline._step2_ontology_management()
validation_result = await pipeline._step3_shacl_validation()
quality_result = await pipeline._step4_data_quality_check()
storage_result = await pipeline._step5_kg_storage()

await pipeline.close()
```

### Web Interface Usage
1. Navigate to `/ontology/pipeline`
2. Set ontology directory path
3. Click "Run Pipeline" for complete execution
4. Click "Validate Only" for steps 1-3
5. Click "Check Status" for system readiness
6. Monitor real-time progress and results

## Troubleshooting

### Common Issues

**File Not Found Errors**
- Ensure ontology files exist in specified directory
- Check file permissions
- Verify file format support

**Validation Errors**
- Review SHACL constraints
- Check ontology structure
- Validate data against business rules

**Database Connection Issues**
- Verify Neo4j connection settings
- Check network connectivity
- Monitor database performance

**Memory Issues**
- Use smaller batch sizes
- Process files individually
- Monitor memory usage

### Debugging Tips
1. **Enable Debug Logging:** Set log level to DEBUG
2. **Check Step Results:** Review individual step outputs
3. **Validate Input Data:** Ensure ontology files are valid
4. **Monitor Resources:** Track memory and CPU usage
5. **Test Incrementally:** Run steps individually

## Integration

### With Other Modules
- **Ingestion Module:** Provides structured data input
- **Validation Module:** Leverages validation rules
- **Quality Module:** Uses quality assessment tools
- **Knowledge Graph Module:** Populates Neo4j database

### External Systems
- **Chemical Databases:** Integration with external chemical data
- **Regulatory Systems:** Compliance checking
- **Safety Systems:** Risk assessment integration
- **Monitoring Tools:** Real-time pipeline monitoring

## Future Enhancements

### Planned Features
- **Real-time Processing:** Stream processing capabilities
- **Advanced Validation:** Machine learning-based validation
- **Data Lineage:** Track data provenance
- **Incremental Updates:** Delta processing
- **Multi-format Output:** Support for other graph databases

### Integration Opportunities
- **External APIs:** Chemical database integration
- **Cloud Storage:** Support for cloud data sources
- **Workflow Automation:** Integration with business processes
- **Data Catalogs:** Metadata management
- **Compliance Tools:** Regulatory compliance checking

## Contributing

When contributing to the Ontology-to-KG Pipeline:

1. **Follow Pipeline Standards:** Use consistent validation patterns
2. **Add Test Coverage:** Include comprehensive tests
3. **Update Documentation:** Document new features
4. **Performance Testing:** Test with large datasets
5. **Error Handling:** Implement proper error handling

---

For more information, see the main [HazardSafe-KG README](../README.md) or contact the development team. 