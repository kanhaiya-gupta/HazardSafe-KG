# Data Ingestion Module - Structured Data to Knowledge Graph

## Overview

The Data Ingestion module handles the ingestion of structured data (CSV, Excel, JSON) into the HazardSafe-KG knowledge graph. This module is specifically designed for processing tabular and structured data formats, complementing the NLP & RAG system which handles unstructured documents.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Structured     │    │   Data          │    │  Knowledge      │
│  Data           │───▶│   Ingestion     │───▶│  Graph          │
│  (CSV/Excel/    │    │   Pipeline      │    │  (Neo4j)        │
│  JSON)          │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Validation     │
                       │  & Quality      │
                       │  Checks         │
                       └─────────────────┘
```

## Data Ingestion Pipeline

### 1. Data Ingestion
- **Supported Formats**: CSV, Excel (.xlsx, .xls), JSON
- **Data Types**: Substances, Containers, Tests, Assessments
- **Batch Processing**: Multiple files and data types
- **Metadata Extraction**: File properties, data statistics

### 2. Data Validation
- **Schema Validation**: Required fields, data types, constraints
- **Business Rules**: Hazard class validation, chemical compatibility
- **Data Quality**: Missing values, duplicates, format checking
- **Cross-Reference Validation**: Consistency across related data

### 3. Data Quality Check
- **Completeness**: Required field validation
- **Consistency**: Cross-field validation
- **Compatibility**: Chemical compatibility checking
- **Integrity**: Referential integrity validation

### 4. Entity Mapping
- **Direct Mapping**: CSV columns to KG entities
- **Relationship Mapping**: Foreign keys to relationships
- **Property Mapping**: Data fields to node properties
- **Type Conversion**: Data type validation and conversion

### 5. Knowledge Graph Storage
- **Neo4j Integration**: Direct database operations
- **Node Creation**: Substances, containers, tests, assessments
- **Relationship Creation**: Storage, testing, assessment relationships
- **Batch Operations**: Efficient bulk data insertion

## Module Structure

```
ingestion/
├── README.md                           # This file
├── __init__.py                         # Module initialization
├── haz_ingest.py                       # Main ingestion pipeline
└── data/                               # Sample data and templates
    ├── substances.csv                  # Sample substance data
    ├── containers.csv                  # Sample container data
    ├── tests.csv                       # Sample test data
    └── assessments.csv                 # Sample assessment data
```

## Key Components

### Hazardous Data Ingestion (`haz_ingest.py`)
Main ingestion pipeline for structured hazardous substances data.

**Features:**
- Multi-format data ingestion (CSV, Excel, JSON)
- Data validation and quality checking
- Entity extraction and mapping
- Knowledge graph population
- Batch processing capabilities

**Usage:**
```python
from ingestion.haz_ingest import HazardousDataIngestion

ingestor = HazardousDataIngestion()
await ingestor.initialize()

# Ingest CSV data
result = await ingestor.ingest_csv_data("substances.csv", "substances")
print(f"Ingested {result['ingested_count']} substances")
```

## Supported Data Types

### 1. Substances Data
Chemical substances with their properties and hazards.

**Required Fields:**
- `name`: Chemical name
- `hazard_class`: Hazard classification

**Optional Fields:**
- `chemical_formula`: Molecular formula
- `molecular_weight`: Molecular weight
- `cas_number`: CAS registry number
- `flash_point`: Flash point temperature
- `boiling_point`: Boiling point temperature
- `melting_point`: Melting point temperature
- `density`: Density value
- `description`: Additional description

**Example CSV:**
```csv
name,chemical_formula,hazard_class,molecular_weight,cas_number,description
Sulfuric Acid,H2SO4,corrosive,98.08,7664-93-9,Highly corrosive acid
Toluene,C7H8,flammable,92.14,108-88-3,Flammable solvent
Sodium Hydroxide,NaOH,corrosive,40.00,1310-73-2,Caustic base
```

### 2. Containers Data
Storage containers and their specifications.

**Required Fields:**
- `name`: Container name/identifier
- `material`: Container material
- `capacity`: Storage capacity

**Optional Fields:**
- `unit`: Capacity unit (L, mL, etc.)
- `pressure_rating`: Maximum pressure rating
- `temperature_rating`: Maximum temperature rating
- `manufacturer`: Container manufacturer
- `model`: Container model number
- `description`: Additional description

**Example CSV:**
```csv
name,material,capacity,unit,pressure_rating,temperature_rating,manufacturer
Glass Bottle 1L,glass,1,L,1.0,100,LabSupply Co
Polyethylene Tank,plastic,100,L,2.0,60,ChemStorage Inc
Stainless Steel Drum,stainless_steel,200,L,5.0,150,MetalContainers
```

### 3. Tests Data
Safety and compatibility test data.

**Required Fields:**
- `name`: Test name/identifier
- `test_type`: Type of test performed

**Optional Fields:**
- `description`: Test description
- `standard`: Testing standard used
- `method`: Testing method
- `duration`: Test duration
- `temperature`: Test temperature
- `pressure`: Test pressure
- `result`: Test results

**Example CSV:**
```csv
name,test_type,description,standard,duration,temperature,result
Corrosion Test 001,corrosion_test,Material compatibility test,ASTM G31,24,25,Pass
Pressure Test 001,pressure_test,Container pressure testing,ISO 11439,2,20,Pass
Leak Test 001,leak_test,Container leak detection,ASTM D4991,1,25,Pass
```

### 4. Assessments Data
Risk assessments and safety evaluations.

**Required Fields:**
- `title`: Assessment title
- `substance_id`: Reference to substance
- `risk_level`: Risk assessment level

**Optional Fields:**
- `hazards`: Identified hazards
- `mitigation`: Mitigation measures
- `ppe_required`: Required PPE
- `storage_requirements`: Storage requirements
- `emergency_procedures`: Emergency procedures
- `assessor`: Assessment performed by
- `assessment_date`: Date of assessment

**Example CSV:**
```csv
title,substance_id,risk_level,hazards,mitigation,ppe_required,assessor
H2SO4 Risk Assessment,H2SO4_001,high,Corrosive burns,Proper ventilation,Gloves and goggles,Dr. Smith
Toluene Safety Review,TOL_001,medium,Flammable vapors,Explosion-proof storage,Respirator,Dr. Johnson
```

## API Endpoints

### Data Ingestion
- `POST /ingestion/substances` - Ingest substance data
- `POST /ingestion/containers` - Ingest container data
- `POST /ingestion/tests` - Ingest test data
- `POST /ingestion/assessments` - Ingest assessment data
- `POST /ingestion/batch` - Batch ingest multiple data types

### Data Management
- `GET /ingestion/status` - Get ingestion pipeline status
- `GET /ingestion/statistics` - Get ingestion statistics
- `POST /ingestion/validate` - Validate data before ingestion
- `DELETE /ingestion/cleanup` - Clean up invalid data

## Usage Examples

### Example 1: Ingest Substance Data
```python
from ingestion.haz_ingest import HazardousDataIngestion

# Initialize ingestion pipeline
ingestor = HazardousDataIngestion()
await ingestor.initialize()

# Ingest CSV substance data
result = await ingestor.ingest_csv_data("substances.csv", "substances")

if result["success"]:
    print(f"Successfully ingested {result['ingested_count']} substances")
    if result["errors"]:
        print(f"Errors: {result['errors']}")
else:
    print(f"Ingestion failed: {result['message']}")
```

### Example 2: Batch Ingest Multiple Data Types
```python
# Ingest multiple data types
data_files = [
    ("substances.csv", "substances"),
    ("containers.csv", "containers"),
    ("tests.csv", "tests"),
    ("assessments.csv", "assessments")
]

for file_path, data_type in data_files:
    result = await ingestor.ingest_csv_data(file_path, data_type)
    print(f"{data_type}: {result['ingested_count']} items ingested")
```

### Example 3: Create Relationships
```python
# Create storage relationships
relationship_data = {
    "substance_id": "H2SO4_001",
    "container_id": "GLASS_001",
    "relationship_type": "STORED_IN",
    "properties": {
        "quantity": 1.0,
        "date_stored": "2024-01-15"
    }
}

result = await ingestor.create_relationships(relationship_data)
print(f"Relationship created: {result['success']}")
```

### Example 4: Get Ingestion Statistics
```python
# Get pipeline statistics
stats = await ingestor.get_ingestion_stats()
print(f"Total substances: {stats['substances']}")
print(f"Total containers: {stats['containers']}")
print(f"Total tests: {stats['tests']}")
print(f"Total assessments: {stats['assessments']}")
```

## Data Validation Rules

### Substance Validation
- **Name**: Required, non-empty string
- **Chemical Formula**: Valid chemical formula format
- **Hazard Class**: Must be from predefined list
- **CAS Number**: Valid CAS number format (XXX-XX-X)
- **Molecular Weight**: Positive number, reasonable range (0-10000)
- **Temperature Values**: Reasonable range (-273 to 5000°C)

### Container Validation
- **Name**: Required, non-empty string
- **Material**: Must be from predefined material list
- **Capacity**: Positive number, reasonable range
- **Pressure Rating**: Non-negative number
- **Temperature Rating**: Reasonable range (-200 to 1000°C)

### Test Validation
- **Name**: Required, non-empty string
- **Test Type**: Must be from predefined test types
- **Duration**: Positive number
- **Temperature**: Reasonable range
- **Pressure**: Non-negative number

### Assessment Validation
- **Title**: Required, non-empty string
- **Substance ID**: Must reference existing substance
- **Risk Level**: Must be from predefined levels (low, medium, high, critical)
- **Assessment Date**: Valid date format

## Configuration

### Ingestion Settings
```python
INGESTION_CONFIG = {
    "batch_size": 1000,
    "validation_enabled": True,
    "quality_check_enabled": True,
    "auto_relationships": True,
    "error_threshold": 0.1,  # 10% error tolerance
    "log_level": "INFO"
}
```

### Data Type Mappings
```python
DATA_TYPE_MAPPINGS = {
    "substances": {
        "node_label": "HazardousSubstance",
        "required_fields": ["name", "hazard_class"],
        "optional_fields": ["chemical_formula", "molecular_weight", "cas_number"]
    },
    "containers": {
        "node_label": "Container",
        "required_fields": ["name", "material", "capacity"],
        "optional_fields": ["pressure_rating", "temperature_rating"]
    }
}
```

## Error Handling

### Common Error Types
1. **Validation Errors**: Invalid data format or values
2. **Missing Data**: Required fields not provided
3. **Duplicate Data**: Existing entities with same identifiers
4. **Relationship Errors**: Invalid references between entities
5. **Database Errors**: Connection or transaction failures

### Error Response Format
```python
{
    "success": False,
    "error_type": "validation_error",
    "message": "Invalid chemical formula format",
    "details": {
        "field": "chemical_formula",
        "value": "H2SO4!",
        "expected_format": "Valid chemical formula"
    },
    "row_number": 5
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

### Logging Configuration
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ingestion.log'),
        logging.StreamHandler()
    ]
)
```

### Key Metrics
- **Ingestion Rate**: Records processed per second
- **Success Rate**: Percentage of successful ingestions
- **Error Rate**: Percentage of failed ingestions
- **Processing Time**: Time per batch/file
- **Data Quality**: Validation pass rate

## Data Quality Assurance

### Quality Checks
1. **Completeness**: All required fields present
2. **Accuracy**: Data values within expected ranges
3. **Consistency**: Cross-field validation
4. **Uniqueness**: No duplicate records
5. **Integrity**: Referential integrity maintained

### Quality Reports
```python
{
    "total_records": 1000,
    "valid_records": 950,
    "invalid_records": 50,
    "quality_score": 0.95,
    "issues": [
        {
            "type": "missing_field",
            "field": "cas_number",
            "count": 25
        },
        {
            "type": "invalid_format",
            "field": "chemical_formula",
            "count": 15
        }
    ]
}
```

## Troubleshooting

### Common Issues

**CSV Encoding Problems**
- Ensure UTF-8 encoding: `encoding='utf-8'`
- Handle special characters properly
- Use appropriate CSV dialect

**Data Type Conversion Errors**
- Validate data types before ingestion
- Provide default values for missing data
- Use appropriate type conversion functions

**Database Connection Issues**
- Check Neo4j connection settings
- Verify network connectivity
- Monitor database performance

**Memory Issues with Large Files**
- Use streaming for large files
- Process in smaller batches
- Implement memory monitoring

### Debugging Tips
1. **Enable Debug Logging**: Set log level to DEBUG
2. **Validate Data First**: Use validation endpoints
3. **Check File Format**: Verify CSV/Excel format
4. **Monitor Resources**: Track memory and CPU usage
5. **Test with Sample Data**: Use small datasets first

## Integration with Other Modules

### Validation Module
- Uses validation rules for data quality
- Integrates with compatibility checking
- Leverages business rule validation

### Knowledge Graph Module
- Populates Neo4j database
- Creates nodes and relationships
- Maintains graph consistency

### Quality Module
- Provides quality metrics
- Generates quality reports
- Tracks data quality over time

## Future Enhancements

### Planned Features
- **Real-time Ingestion**: Stream processing capabilities
- **Data Transformation**: ETL pipeline integration
- **Advanced Validation**: Machine learning-based validation
- **Data Lineage**: Track data provenance
- **Incremental Updates**: Delta processing

### Integration Opportunities
- **External APIs**: Chemical database integration
- **Cloud Storage**: Support for cloud data sources
- **Workflow Automation**: Integration with business processes
- **Data Catalogs**: Metadata management
- **Compliance Tools**: Regulatory compliance checking

## Contributing

When contributing to the Data Ingestion module:

1. **Follow Data Standards**: Use consistent data formats
2. **Add Validation Rules**: Include appropriate validation
3. **Update Documentation**: Document new data types
4. **Write Tests**: Test with sample data
5. **Performance Testing**: Test with large datasets

## Sample Data

The `data/` directory contains sample data files for testing:

- `substances.csv`: Sample chemical substances
- `containers.csv`: Sample storage containers
- `tests.csv`: Sample safety tests
- `assessments.csv`: Sample risk assessments

Use these files to test the ingestion pipeline and understand the expected data format.

---

For more information, see the main [HazardSafe-KG README](../README.md) or contact the development team. 