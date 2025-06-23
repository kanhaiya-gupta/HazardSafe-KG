# HazardSafe-KG Scripting Development Guide

## Overview

This guide provides a comprehensive approach to developing and testing all HazardSafe-KG modules using Python scripts directly, without frontend integration. This approach allows for focused backend development, testing, and validation before connecting to the web interface.

## Development Philosophy

1. **Script-First Development**: Write and test all functionality using Python scripts
2. **Data-Driven Testing**: Use sample data from the `data/` folder for testing
3. **Modular Testing**: Test each module independently before integration
4. **Pipeline Validation**: Test complete pipelines end-to-end
5. **Frontend Integration**: Connect to web interface only after backend is stable

## Project Structure for Scripting

```
HazardSafe-KG/
├── data/                           # Sample data for testing
│   ├── ontology/                   # TTL ontology files
│   ├── documents/                  # PDF, CSV, JSON test files
│   ├── substances/                 # Chemical substance data
│   ├── containers/                 # Container data
│   └── tests/                      # Test data
├── scripts/                        # Development and testing scripts
│   ├── test_ontology_pipeline.py   # Ontology pipeline testing
│   ├── test_nlp_rag_pipeline.py    # NLP & RAG pipeline testing
│   ├── test_kg_operations.py       # Knowledge graph operations
│   ├── test_validation.py          # Data validation testing
│   ├── test_quality.py             # Quality metrics testing
│   └── integration_tests.py        # End-to-end integration tests
├── ontology/                       # Ontology module
├── nlp_rag/                        # NLP & RAG module
├── kg/                             # Knowledge Graph module
├── validation/                     # Validation module
└── quality/                        # Quality module
```

## Module Development Scripts

### 1. Ontology Module Scripting

#### Test Ontology Pipeline
```bash
# Test the complete ontology-to-KG pipeline
python scripts/test_ontology_pipeline.py

# Test individual steps
python scripts/test_ontology_pipeline.py --step ingestion
python scripts/test_ontology_pipeline.py --step management
python scripts/test_ontology_pipeline.py --step validation
python scripts/test_ontology_pipeline.py --step quality
python scripts/test_ontology_pipeline.py --step storage
```

#### Direct Module Testing
```python
# Test ontology manager directly
from ontology.manager import OntologyManager
from ontology.ontology_to_kg_pipeline import OntologyToKGPipeline

# Initialize components
ontology_manager = OntologyManager()
pipeline = OntologyToKGPipeline()

# Test ontology loading
success = await ontology_manager.load_ontology_files("data/ontology")
print(f"Loaded {len(ontology_manager.graph)} triples")

# Test pipeline execution
result = await pipeline.run_pipeline("data/ontology")
print(f"Pipeline completed: {result['success']}")
```

### 2. NLP & RAG Module Scripting

#### Test Document Pipeline
```bash
# Test document-to-KG pipeline
python scripts/test_nlp_rag_pipeline.py

# Test with specific document types
python scripts/test_nlp_rag_pipeline.py --type pdf
python scripts/test_nlp_rag_pipeline.py --type csv
python scripts/test_nlp_rag_pipeline.py --type json
```

#### Direct Module Testing
```python
# Test document processing
from nlp_rag.document_to_kg_pipeline import DocumentToKGPipeline
from nlp_rag.processors.document_processor import DocumentProcessor

# Initialize pipeline
pipeline = DocumentToKGPipeline()
await pipeline.initialize()

# Test single document
result = await pipeline.process_document_to_kg("data/documents/safety_sheet.pdf", "safety")
print(f"Extracted {len(result['entities'])} entities")

# Test batch processing
documents = ["doc1.pdf", "doc2.csv", "doc3.json"]
batch_result = await pipeline.process_batch_documents_to_kg(documents)
print(f"Processed {len(batch_result)} documents")
```

### 3. Knowledge Graph Module Scripting

#### Test KG Operations
```bash
# Test knowledge graph operations
python scripts/test_kg_operations.py

# Test specific operations
python scripts/test_kg_operations.py --operation create
python scripts/test_kg_operations.py --operation query
python scripts/test_kg_operations.py --operation update
python scripts/test_kg_operations.py --operation delete
```

#### Direct Module Testing
```python
# Test KG service directly
from kg.services import KnowledgeGraphService
from kg.models import Substance, Container, Test, Assessment

# Initialize KG service
kg_service = KnowledgeGraphService()

# Test substance creation
substance_data = {
    "name": "Sulfuric Acid",
    "formula": "H2SO4",
    "cas_number": "7664-93-9",
    "hazard_class": "corrosive"
}
substance = await kg_service.create_substance(substance_data)
print(f"Created substance: {substance.id}")

# Test complex queries
query = "MATCH (s:Substance)-[:HAS_HAZARD]->(h:Hazard) RETURN s.name, h.type"
results = await kg_service.execute_query(query)
print(f"Found {len(results)} hazard relationships")
```

### 4. Validation Module Scripting

#### Test Data Validation
```bash
# Test validation pipeline
python scripts/test_validation.py

# Test specific data types
python scripts/test_validation.py --type substances
python scripts/test_validation.py --type containers
python scripts/test_validation.py --type tests
```

#### Direct Module Testing
```python
# Test validation directly
from validation.validator import DataValidator
from validation.rules import BusinessRules

# Initialize validator
validator = DataValidator()
rules = BusinessRules()

# Test substance validation
substance_data = {
    "name": "H2SO4",
    "formula": "H2SO4",
    "cas_number": "7664-93-9",
    "hazard_class": "corrosive"
}
validation_result = await validator.validate_data(substance_data, "substances")
print(f"Validation passed: {validation_result['valid']}")

# Test compatibility rules
is_compatible = rules.check_chemical_compatibility("H2SO4", "glass")
print(f"Compatible: {is_compatible}")
```

### 5. Quality Module Scripting

#### Test Quality Metrics
```bash
# Test quality assessment
python scripts/test_quality.py

# Test specific metrics
python scripts/test_quality.py --metric completeness
python scripts/test_quality.py --metric accuracy
python scripts/test_quality.py --metric consistency
```

#### Direct Module Testing
```python
# Test quality metrics directly
from quality.metrics import QualityMetrics
from quality.reports import QualityReporter
import pandas as pd

# Load test data
data = pd.read_csv("data/substances/substances.csv")

# Calculate quality metrics
metrics = QualityMetrics()
quality_results = metrics.calculate_overall_quality_score(data)
print(f"Overall Quality: {quality_results['overall_score']:.1%}")

# Generate quality report
reporter = QualityReporter()
report_path = reporter.generate_quality_report(quality_results, "substances_dataset")
print(f"Report generated: {report_path}")
```

## Integration Testing Scripts

### End-to-End Pipeline Testing
```bash
# Test complete data flow
python scripts/integration_tests.py

# Test specific scenarios
python scripts/integration_tests.py --scenario ontology_to_kg
python scripts/integration_tests.py --scenario document_to_kg
python scripts/integration_tests.py --scenario validation_quality
```

### Cross-Module Integration
```python
# Test integration between modules
async def test_ontology_to_kg_integration():
    # 1. Load ontology
    ontology_manager = OntologyManager()
    await ontology_manager.load_ontology_files("data/ontology")
    
    # 2. Run pipeline
    pipeline = OntologyToKGPipeline()
    pipeline_result = await pipeline.run_pipeline("data/ontology")
    
    # 3. Validate KG data
    kg_service = KnowledgeGraphService()
    kg_data = await kg_service.get_all_substances()
    
    # 4. Assess quality
    quality_metrics = QualityMetrics()
    quality_score = quality_metrics.calculate_overall_quality_score(kg_data)
    
    print(f"Integration complete - Quality: {quality_score:.1%}")
```

## Sample Data for Testing

### Ontology Data
```bash
# Create sample TTL files
echo "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix haz: <http://hazardsafe.kg/ontology#> .

haz:HazardousSubstance a rdfs:Class ;
    rdfs:label \"Hazardous Substance\" ;
    rdfs:comment \"A chemical substance with hazardous properties\" .

haz:hasHazardClass a rdf:Property ;
    rdfs:domain haz:HazardousSubstance ;
    rdfs:range haz:HazardClass ." > data/ontology/sample.ttl
```

### Document Data
```bash
# Create sample CSV files
echo "name,formula,cas_number,hazard_class
Sulfuric Acid,H2SO4,7664-93-9,corrosive
Sodium Hydroxide,NaOH,1310-73-2,corrosive
Methanol,CH3OH,67-56-1,flammable" > data/documents/substances.csv
```

### Test Data
```bash
# Create sample test data
echo "test_name,test_type,standard,duration,temperature,result
Compatibility Test,Storage,ASTM D543,24,25,Pass
Corrosion Test,Material,ISO 9227,168,35,Fail" > data/tests/test_data.csv
```

## Development Workflow

### 1. Module Development
```bash
# 1. Create module structure
mkdir -p new_module/{config,models,processors,utils}
touch new_module/__init__.py
touch new_module/main.py

# 2. Implement core functionality
# Edit new_module/main.py with core logic

# 3. Create test script
touch scripts/test_new_module.py

# 4. Test functionality
python scripts/test_new_module.py
```

### 2. Pipeline Development
```bash
# 1. Create pipeline class
# Edit new_module/pipeline.py

# 2. Create pipeline test
touch scripts/test_new_pipeline.py

# 3. Test pipeline steps
python scripts/test_new_pipeline.py --step step1
python scripts/test_new_pipeline.py --step step2

# 4. Test complete pipeline
python scripts/test_new_pipeline.py --complete
```

### 3. Integration Development
```bash
# 1. Create integration test
touch scripts/test_integration.py

# 2. Test module interactions
python scripts/test_integration.py --modules module1,module2

# 3. Test data flow
python scripts/test_integration.py --flow data_flow_name
```

## Testing Best Practices

### 1. Unit Testing
- Test each function independently
- Use mock data for external dependencies
- Test edge cases and error conditions
- Validate input/output formats

### 2. Integration Testing
- Test module interactions
- Validate data flow between components
- Test error propagation
- Verify end-to-end functionality

### 3. Performance Testing
- Test with large datasets
- Monitor memory usage
- Measure processing time
- Identify bottlenecks

### 4. Data Validation Testing
- Test with various data formats
- Validate against business rules
- Test error handling
- Verify quality metrics

## Debugging and Troubleshooting

### Common Issues
1. **Import Errors**: Check module paths and __init__.py files
2. **Data Format Issues**: Validate input data structure
3. **Connection Errors**: Check database/API connections
4. **Memory Issues**: Monitor memory usage with large datasets

### Debugging Tools
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debugger
import pdb; pdb.set_trace()

# Profile performance
import cProfile
cProfile.run('your_function()')
```

## Script Execution Examples

### Quick Start
```bash
# Test all modules
python scripts/test_all_modules.py

# Test specific functionality
python scripts/test_ontology_pipeline.py --quick
python scripts/test_nlp_rag_pipeline.py --sample
python scripts/test_kg_operations.py --basic
```

### Development Mode
```bash
# Run with debug logging
python scripts/test_ontology_pipeline.py --debug

# Run with detailed output
python scripts/test_nlp_rag_pipeline.py --verbose

# Run with custom data
python scripts/test_validation.py --data-path custom_data/
```

### Production Testing
```bash
# Run comprehensive tests
python scripts/integration_tests.py --full

# Run performance tests
python scripts/performance_tests.py

# Run stress tests
python scripts/stress_tests.py --large-dataset
```

## Next Steps

1. **Implement Core Scripts**: Create the test scripts for each module
2. **Develop Sample Data**: Create comprehensive test datasets
3. **Build Pipelines**: Implement end-to-end processing pipelines
4. **Test Integration**: Verify module interactions
5. **Optimize Performance**: Profile and optimize critical paths
6. **Document Results**: Create detailed testing documentation
7. **Frontend Integration**: Connect to web interface after backend validation

This scripting-first approach ensures robust backend development before frontend integration, leading to more stable and maintainable code. 