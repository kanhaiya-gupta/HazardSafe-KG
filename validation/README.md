# Data Validation Module - Quality Assurance & Business Rules

## Overview

The Data Validation module provides comprehensive data validation, quality assurance, and business rule checking for the HazardSafe-KG platform. This module ensures data integrity, consistency, and compliance with safety standards across all data types and sources.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Input Data     │    │   Validation    │    │  Validated      │
│  (CSV/JSON/     │───▶│   Pipeline      │───▶│  Data           │
│  Documents)     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Quality        │
                       │  Reports        │
                       │  & Metrics      │
                       └─────────────────┘
```

## Validation Pipeline

### 1. Data Format Validation
- **File Format**: CSV, JSON, Excel validation
- **Encoding**: UTF-8 and other encoding checks
- **Structure**: Schema validation and field mapping
- **Metadata**: File properties and header validation

### 2. Schema Validation
- **Required Fields**: Mandatory field presence
- **Data Types**: Type checking and conversion
- **Field Constraints**: Length, range, format validation
- **Cross-Field Validation**: Inter-field dependencies

### 3. Business Rule Validation
- **Chemical Compatibility**: Substance-container compatibility
- **Hazard Classification**: Valid hazard class assignments
- **Safety Standards**: Regulatory compliance checking
- **Risk Assessment**: Risk level validation

### 4. Data Quality Assessment
- **Completeness**: Missing value analysis
- **Accuracy**: Data accuracy verification
- **Consistency**: Cross-reference validation
- **Uniqueness**: Duplicate detection

### 5. Quality Reporting
- **Validation Reports**: Detailed error reports
- **Quality Metrics**: Data quality scores
- **Compliance Reports**: Regulatory compliance status
- **Recommendations**: Improvement suggestions

## Module Structure

```
validation/
├── README.md                           # This file
├── __init__.py                         # Module initialization
├── validator.py                        # Main validation engine
├── rules.py                           # Business rules and constraints
├── csv_validator.py                   # CSV-specific validation
├── json_validator.py                  # JSON-specific validation
├── compatibility.py                   # Chemical compatibility checking
├── utils.py                           # Validation utilities
└── tests/                             # Test files
    ├── __init__.py
    ├── test_rules.py
    ├── test_validation.py
    └── conftest.py
```

## Key Components

### Main Validator (`validator.py`)
Central validation engine that orchestrates all validation processes.

**Features:**
- Multi-format data validation
- Business rule enforcement
- Quality assessment
- Comprehensive reporting

**Usage:**
```python
from validation.validator import DataValidator

validator = DataValidator()
result = await validator.validate_data("substances.csv", "substances")
print(f"Validation passed: {result['valid']}")
print(f"Quality score: {result['quality_score']}")
```

### Business Rules (`rules.py`)
Defines and enforces business rules and constraints.

**Key Rules:**
- Chemical compatibility rules
- Hazard classification rules
- Safety standard compliance
- Risk assessment validation

**Usage:**
```python
from validation.rules import BusinessRules

rules = BusinessRules()
is_compatible = rules.check_chemical_compatibility("H2SO4", "glass")
print(f"Compatible: {is_compatible}")
```

### Format Validators
Specialized validators for different data formats.

#### CSV Validator (`csv_validator.py`)
Validates CSV files with schema and business rules.

**Features:**
- Header validation
- Data type checking
- Required field validation
- Format consistency

#### JSON Validator (`json_validator.py`)
Validates JSON data structures and schemas.

**Features:**
- Schema validation
- Type checking
- Nested object validation
- Array validation

### Compatibility Checker (`compatibility.py`)
Checks chemical compatibility between substances and containers.

**Features:**
- Chemical compatibility matrix
- Material compatibility rules
- Safety threshold checking
- Risk assessment

## Supported Data Types

### 1. Substances Validation
Chemical substances with safety and property validation.

**Validation Rules:**
- **Name**: Non-empty, valid chemical name
- **Chemical Formula**: Valid molecular formula format
- **Hazard Class**: From predefined hazard classes
- **CAS Number**: Valid CAS registry format (XXX-XX-X)
- **Molecular Weight**: Positive number, reasonable range
- **Temperature Values**: Valid temperature ranges
- **Density**: Positive number, reasonable range

**Business Rules:**
- Hazard class must match chemical properties
- CAS number must be unique
- Temperature values must be physically possible
- Molecular weight must be reasonable for formula

### 2. Containers Validation
Storage containers with safety and compatibility validation.

**Validation Rules:**
- **Name**: Non-empty, unique identifier
- **Material**: From predefined material list
- **Capacity**: Positive number, reasonable range
- **Pressure Rating**: Non-negative, within limits
- **Temperature Rating**: Valid temperature range
- **Manufacturer**: Valid manufacturer information

**Business Rules:**
- Material must be compatible with intended use
- Capacity must be reasonable for material
- Pressure rating must exceed operating pressure
- Temperature rating must exceed operating temperature

### 3. Tests Validation
Safety and compatibility test data validation.

**Validation Rules:**
- **Name**: Non-empty, unique test identifier
- **Test Type**: From predefined test types
- **Standard**: Valid testing standard reference
- **Duration**: Positive number, reasonable range
- **Temperature**: Valid temperature range
- **Pressure**: Non-negative, within limits
- **Result**: Valid result format

**Business Rules:**
- Test type must match standard used
- Duration must be reasonable for test type
- Temperature must be within test equipment limits
- Results must be consistent with test parameters

### 4. Assessments Validation
Risk assessment and safety evaluation validation.

**Validation Rules:**
- **Title**: Non-empty, descriptive title
- **Substance ID**: Must reference existing substance
- **Risk Level**: From predefined risk levels
- **Assessment Date**: Valid date format
- **Assessor**: Valid assessor information

**Business Rules:**
- Risk level must match identified hazards
- Assessment must be performed by qualified assessor
- Date must be recent and valid
- Mitigation measures must address identified risks

## API Endpoints

### Data Validation
- `POST /validation/validate` - Validate data file
- `POST /validation/validate-substances` - Validate substance data
- `POST /validation/validate-containers` - Validate container data
- `POST /validation/validate-tests` - Validate test data
- `POST /validation/validate-assessments` - Validate assessment data

### Business Rules
- `POST /validation/check-compatibility` - Check chemical compatibility
- `POST /validation/check-hazards` - Validate hazard classifications
- `POST /validation/check-compliance` - Check regulatory compliance
- `GET /validation/rules` - Get available validation rules

### Quality Assessment
- `POST /validation/quality-assessment` - Assess data quality
- `GET /validation/quality-metrics` - Get quality metrics
- `POST /validation/generate-report` - Generate validation report
- `GET /validation/reports` - Get validation reports

## Usage Examples

### Example 1: Validate Substance Data
```python
from validation.validator import DataValidator

validator = DataValidator()

# Validate CSV substance data
result = await validator.validate_data("substances.csv", "substances")

if result["valid"]:
    print(f"Validation passed with quality score: {result['quality_score']}")
    print(f"Processed {result['total_records']} records")
else:
    print(f"Validation failed: {result['errors']}")
    print(f"Error count: {result['error_count']}")
```

### Example 2: Check Chemical Compatibility
```python
from validation.compatibility import CompatibilityChecker

checker = CompatibilityChecker()

# Check substance-container compatibility
compatibility = checker.check_compatibility("H2SO4", "glass")
print(f"Compatible: {compatibility['compatible']}")
print(f"Risk level: {compatibility['risk_level']}")
print(f"Recommendations: {compatibility['recommendations']}")
```

### Example 3: Business Rule Validation
```python
from validation.rules import BusinessRules

rules = BusinessRules()

# Validate hazard classification
hazard_check = rules.validate_hazard_class("H2SO4", "corrosive")
print(f"Valid classification: {hazard_check['valid']}")
print(f"Confidence: {hazard_check['confidence']}")
```

### Example 4: Quality Assessment
```python
from validation.validator import DataValidator

validator = DataValidator()

# Assess data quality
quality = await validator.assess_quality("substances.csv", "substances")
print(f"Overall quality score: {quality['overall_score']}")
print(f"Completeness: {quality['completeness']}")
print(f"Accuracy: {quality['accuracy']}")
print(f"Consistency: {quality['consistency']}")
```

## Validation Rules

### Data Format Rules
```python
FORMAT_RULES = {
    "csv": {
        "encoding": "utf-8",
        "delimiter": ",",
        "quote_char": '"',
        "required_headers": True
    },
    "json": {
        "schema_validation": True,
        "type_checking": True,
        "required_fields": True
    }
}
```

### Business Rules
```python
BUSINESS_RULES = {
    "substances": {
        "hazard_classes": ["corrosive", "flammable", "toxic", "explosive"],
        "cas_format": r"^\d{1,7}-\d{2}-\d$",
        "molecular_weight_range": (0, 10000),
        "temperature_range": (-273, 5000)
    },
    "containers": {
        "materials": ["glass", "plastic", "stainless_steel", "aluminum"],
        "capacity_range": (0.001, 1000000),
        "pressure_range": (0, 1000),
        "temperature_range": (-200, 1000)
    }
}
```

### Compatibility Rules
```python
COMPATIBILITY_MATRIX = {
    "H2SO4": {
        "compatible": ["glass", "stainless_steel"],
        "incompatible": ["aluminum", "zinc"],
        "risk_level": "high",
        "precautions": ["Use proper PPE", "Ventilation required"]
    },
    "NaOH": {
        "compatible": ["stainless_steel", "plastic"],
        "incompatible": ["aluminum", "glass"],
        "risk_level": "medium",
        "precautions": ["Avoid contact with skin", "Use gloves"]
    }
}
```

## Error Handling

### Validation Error Types
1. **Format Errors**: Invalid file format or structure
2. **Schema Errors**: Missing required fields or invalid types
3. **Business Rule Errors**: Violation of business constraints
4. **Compatibility Errors**: Incompatible combinations
5. **Quality Errors**: Data quality issues

### Error Response Format
```python
{
    "valid": False,
    "error_type": "business_rule_violation",
    "message": "Invalid hazard classification",
    "details": {
        "field": "hazard_class",
        "value": "unknown",
        "allowed_values": ["corrosive", "flammable", "toxic", "explosive"],
        "row": 5,
        "column": "hazard_class"
    },
    "severity": "error",
    "suggestions": ["Use one of the allowed hazard classes"]
}
```

## Quality Metrics

### Quality Dimensions
1. **Completeness**: Percentage of required fields present
2. **Accuracy**: Percentage of accurate data values
3. **Consistency**: Percentage of consistent data across fields
4. **Uniqueness**: Percentage of unique records
5. **Validity**: Percentage of valid data according to rules

### Quality Score Calculation
```python
QUALITY_WEIGHTS = {
    "completeness": 0.25,
    "accuracy": 0.30,
    "consistency": 0.20,
    "uniqueness": 0.15,
    "validity": 0.10
}

def calculate_quality_score(metrics):
    score = 0
    for dimension, weight in QUALITY_WEIGHTS.items():
        score += metrics[dimension] * weight
    return score
```

## Configuration

### Validation Settings
```python
VALIDATION_CONFIG = {
    "strict_mode": True,
    "auto_correct": False,
    "error_threshold": 0.1,
    "quality_threshold": 0.8,
    "max_errors": 100,
    "log_level": "INFO"
}
```

### Rule Configuration
```python
RULE_CONFIG = {
    "enable_business_rules": True,
    "enable_compatibility_check": True,
    "enable_quality_assessment": True,
    "enable_compliance_check": True,
    "custom_rules": []
}
```

## Performance Optimization

### Validation Strategies
1. **Batch Processing**: Validate data in batches
2. **Parallel Validation**: Use multiple threads for large datasets
3. **Caching**: Cache validation results
4. **Early Termination**: Stop on critical errors

### Memory Management
- Stream large files instead of loading entirely
- Use generators for data processing
- Implement cleanup procedures
- Monitor memory usage

## Monitoring and Reporting

### Validation Metrics
- **Validation Rate**: Records validated per second
- **Success Rate**: Percentage of successful validations
- **Error Rate**: Percentage of validation errors
- **Quality Score**: Average data quality score
- **Processing Time**: Time per validation batch

### Report Generation
```python
{
    "validation_summary": {
        "total_records": 1000,
        "valid_records": 950,
        "invalid_records": 50,
        "quality_score": 0.95,
        "processing_time": "2.5s"
    },
    "error_details": [
        {
            "type": "business_rule_violation",
            "count": 25,
            "examples": ["Invalid hazard class", "Missing CAS number"]
        }
    ],
    "quality_metrics": {
        "completeness": 0.98,
        "accuracy": 0.95,
        "consistency": 0.92,
        "uniqueness": 0.99,
        "validity": 0.97
    }
}
```

## Integration with Other Modules

### Ingestion Module
- Validates data before ingestion
- Provides quality feedback
- Ensures data integrity

### Knowledge Graph Module
- Validates data before KG population
- Checks referential integrity
- Ensures graph consistency

### Quality Module
- Provides validation metrics
- Generates quality reports
- Tracks validation history

### NLP & RAG Module
- Validates extracted entities
- Checks relationship consistency
- Ensures data quality

## Testing

### Test Structure
```
tests/
├── test_rules.py           # Business rules testing
├── test_validation.py      # Validation engine testing
├── test_compatibility.py   # Compatibility checking
└── conftest.py            # Test configuration
```

### Test Coverage
- Unit tests for all validation functions
- Integration tests for validation pipeline
- Performance tests for large datasets
- Error handling tests

## Troubleshooting

### Common Issues

**File Encoding Problems**
- Ensure UTF-8 encoding
- Handle special characters
- Use appropriate file readers

**Schema Validation Errors**
- Check required field definitions
- Verify data type mappings
- Validate field constraints

**Business Rule Violations**
- Review rule definitions
- Check data consistency
- Validate cross-field dependencies

**Performance Issues**
- Use batch processing
- Implement caching
- Optimize validation algorithms

### Debugging Tips
1. **Enable Debug Logging**: Set log level to DEBUG
2. **Validate Incrementally**: Test with small datasets first
3. **Check Configuration**: Verify validation settings
4. **Review Error Reports**: Analyze error patterns
5. **Test Rules Individually**: Isolate rule validation

## Future Enhancements

### Planned Features
- **Machine Learning Validation**: ML-based data quality assessment
- **Real-time Validation**: Stream processing capabilities
- **Custom Rule Engine**: User-defined validation rules
- **Advanced Reporting**: Interactive validation dashboards
- **API Integration**: External validation service integration

### Integration Opportunities
- **External Databases**: Chemical database integration
- **Regulatory APIs**: Compliance checking services
- **Quality Tools**: Integration with data quality platforms
- **Workflow Systems**: Business process integration
- **Monitoring Tools**: Real-time validation monitoring

## Contributing

When contributing to the Validation module:

1. **Follow Validation Standards**: Use consistent validation patterns
2. **Add Test Coverage**: Include comprehensive tests
3. **Update Documentation**: Document new validation rules
4. **Performance Testing**: Test with large datasets
5. **Error Handling**: Implement proper error handling

## Sample Validation Data

The module includes sample data for testing:

- `test_substances.csv`: Sample substance data for validation
- `test_containers.csv`: Sample container data for validation
- `test_tests.csv`: Sample test data for validation
- `test_assessments.csv`: Sample assessment data for validation

Use these files to test validation rules and understand expected data formats.

---

For more information, see the main [HazardSafe-KG README](../README.md) or contact the development team. 