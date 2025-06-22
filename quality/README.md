# Quality Module

The Quality Module provides comprehensive data quality assessment, metrics calculation, and report generation for the HazardSafe-KG platform.

## Overview

This module enables users to:
- Assess data quality across multiple dimensions (completeness, accuracy, consistency, timeliness, uniqueness)
- Generate detailed quality reports with visualizations
- Track quality metrics over time
- Receive actionable recommendations for data improvement
- View interactive dashboards for quality monitoring

## Features

### 🎯 Quality Metrics
- **Completeness**: Measures data completeness and missing value analysis
- **Accuracy**: Validates data accuracy against reference data or format rules
- **Consistency**: Checks data type consistency and value ranges
- **Timeliness**: Evaluates data freshness and update frequency
- **Uniqueness**: Identifies duplicate records and uniqueness patterns

### 📊 Reporting & Visualization
- **HTML Reports**: Detailed quality reports with charts and recommendations
- **Interactive Dashboards**: Real-time quality monitoring with trends
- **Export Capabilities**: JSON export for further analysis
- **Customizable Templates**: Configurable report templates

### 🔧 Configuration
- **Quality Thresholds**: Configurable thresholds for different quality levels
- **Domain-Specific Rules**: Industry-specific quality requirements
- **Validation Rules**: Customizable validation criteria
- **Outlier Detection**: Configurable outlier detection methods

## Structure

```
quality/
├── __init__.py              # Module initialization
├── metrics.py               # Quality metrics calculation
├── reports.py               # Report generation
├── utils.py                 # Utility functions
├── tests/                   # Test suite
│   ├── __init__.py
│   └── test_metrics.py
└── README.md               # This file

data/quality/
├── config/
│   └── quality_config.json  # Quality configuration
├── thresholds/
│   └── domain_thresholds.json # Domain-specific thresholds
└── templates/
    └── report_template.html # HTML report template

webapp/static/reports/quality/
├── metrics/                 # Generated metric reports
├── dashboards/             # Generated dashboards
└── templates/              # Report templates
```

## Usage

### Basic Quality Assessment

```python
from quality.metrics import QualityMetrics
from quality.reports import QualityReporter
import pandas as pd

# Load your data
data = pd.read_csv('your_data.csv')

# Initialize quality components
metrics = QualityMetrics()
reporter = QualityReporter()

# Calculate quality metrics
quality_results = metrics.calculate_overall_quality_score(data)

# Generate report
report_path = reporter.generate_quality_report(quality_results, "dataset_name")

print(f"Overall Quality Score: {quality_results['overall_score']:.1%}")
print(f"Quality Grade: {quality_results['quality_grade']}")
```

### Web Interface

1. Navigate to `/quality` in the web application
2. Upload your dataset (CSV, Excel, or JSON)
3. Configure assessment parameters
4. View quality metrics and recommendations
5. Generate and download reports

### API Endpoints

- `POST /quality/assess` - Assess data quality
- `GET /quality/metrics` - Get historical metrics
- `GET /quality/reports` - List available reports
- `GET /quality/report/{filename}` - View specific report
- `GET /quality/config` - Get quality configuration
- `POST /quality/config` - Update configuration
- `GET /quality/dashboard` - Quality dashboard page

## Configuration

### Quality Thresholds

```json
{
  "quality_thresholds": {
    "completeness": {
      "excellent": 0.95,
      "good": 0.85,
      "acceptable": 0.75,
      "poor": 0.65
    },
    "accuracy": {
      "excellent": 0.98,
      "good": 0.90,
      "acceptable": 0.80,
      "poor": 0.70
    }
  }
}
```

### Domain-Specific Thresholds

```json
{
  "engineering_data": {
    "completeness": 0.90,
    "accuracy": 0.95,
    "consistency": 0.88
  },
  "safety_data": {
    "completeness": 0.95,
    "accuracy": 0.98,
    "consistency": 0.92
  }
}
```

## Quality Metrics Explained

### Completeness
- **Overall Completeness**: Percentage of non-null values across the entire dataset
- **Column Completeness**: Completeness score for each individual column
- **Missing Pattern Analysis**: Identifies systematic missing data patterns

### Accuracy
- **Format Accuracy**: Validates data formats (email, phone, dates)
- **Reference Accuracy**: Compares against reference datasets
- **Range Validation**: Checks values against expected ranges

### Consistency
- **Type Consistency**: Ensures consistent data types within columns
- **Value Consistency**: Validates value ranges and patterns
- **Format Consistency**: Checks for consistent formatting

### Timeliness
- **Data Age**: Measures how recent the data is
- **Update Frequency**: Tracks data update patterns
- **Freshness Score**: Overall timeliness assessment

### Uniqueness
- **Record Uniqueness**: Identifies duplicate records
- **Column Uniqueness**: Measures uniqueness within columns
- **Duplicate Analysis**: Provides duplicate detection insights

## Reports and Dashboards

### Quality Reports
- **Executive Summary**: High-level quality overview
- **Detailed Metrics**: Comprehensive quality breakdown
- **Recommendations**: Actionable improvement suggestions
- **Visualizations**: Charts and graphs for easy interpretation

### Quality Dashboard
- **Trend Analysis**: Quality metrics over time
- **Performance Indicators**: Key quality KPIs
- **Historical Data**: Past quality assessments
- **Interactive Charts**: Real-time data visualization

## Integration

The Quality Module integrates seamlessly with other HazardSafe-KG components:

- **Ontology Module**: Validates ontology data quality
- **Knowledge Graph**: Assesses graph data quality
- **RAG System**: Evaluates document processing quality
- **Validation Engine**: Complements SHACL validation

## Testing

Run the test suite:

```bash
pytest quality/tests/
```

Or run specific tests:

```bash
pytest quality/tests/test_metrics.py -v
```

## Contributing

1. Follow the existing code structure
2. Add comprehensive tests for new features
3. Update documentation for any changes
4. Ensure quality metrics are well-documented

## Dependencies

- pandas
- numpy
- matplotlib (for visualizations)
- jinja2 (for report templates)
- fastapi (for web interface)

## License

Part of the HazardSafe-KG platform. See main project license. 