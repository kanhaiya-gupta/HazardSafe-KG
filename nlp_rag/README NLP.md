# NLP Module

The NLP Module provides natural language processing capabilities for entity recognition, relationship extraction, and structured information extraction from hazardous substance documents.

## Overview

This module enables users to:
- Extract chemical entities, hazards, and properties from text
- Identify relationships between entities
- Analyze text complexity and structure
- Extract safety information and technical terms
- Process documents for knowledge graph population

## Features

### 🔍 Entity Recognition
- **Chemical Entities**: Formulas, names, CAS numbers
- **Hazard Entities**: Corrosive, toxic, flammable, reactive substances
- **Property Entities**: Physical and chemical properties
- **Safety Entities**: Precautions, first aid, storage conditions

### 🔗 Relationship Extraction
- **Pattern-based**: Uses predefined patterns for common relationships
- **Dependency-based**: Leverages spaCy dependency parsing
- **Semantic-based**: Identifies semantic relationships
- **Chemical-specific**: Specialized for chemical and safety relationships

### 📊 Text Analysis
- **Complexity Analysis**: Readability scores and text statistics
- **Document Structure**: Section identification and organization
- **Key Phrase Extraction**: Important phrases and technical terms
- **Technical Term Identification**: Jargon and specialized vocabulary

## Structure

```
nlp/
├── __init__.py              # Module initialization
├── entity_extractor.py      # Entity recognition and extraction
├── relationship_extractor.py # Relationship extraction
├── text_processor.py        # Text preprocessing and analysis
├── tests/                   # Test suite
│   └── __init__.py
└── README.md               # This file

webapp/templates/nlp/
├── index.html              # NLP analysis interface
└── dashboard.html          # NLP dashboard (future)
```

## Usage

### Basic Entity Extraction

```python
from nlp.entity_extractor import EntityExtractor
from nlp.relationship_extractor import RelationshipExtractor

# Initialize extractors
entity_extractor = EntityExtractor()
relationship_extractor = RelationshipExtractor()

# Extract entities
text = "Sulfuric acid (H2SO4) is a corrosive substance that can cause severe burns."
entities = entity_extractor.extract_entities(text)

# Extract relationships
relationships = relationship_extractor.extract_relationships(text, entities)

print(f"Found {len(entities)} entities and {len(relationships)} relationships")
```

### Chemical Compound Extraction

```python
# Extract chemical compounds with properties
compounds = entity_extractor.extract_chemical_compounds(text)

for compound in compounds:
    print(f"Chemical: {compound['name']}")
    print(f"Hazards: {compound['hazards']}")
    print(f"Properties: {compound['physical_properties']}")
```

### Safety Information Extraction

```python
# Extract safety-related information
safety_info = entity_extractor.extract_safety_information(text)

print(f"Hazards: {safety_info['hazards']}")
print(f"Precautions: {safety_info['precautions']}")
print(f"First Aid: {safety_info['first_aid']}")
```

### Text Analysis

```python
from nlp.text_processor import TextProcessor

# Initialize processor
processor = TextProcessor()

# Analyze text
text_summary = processor.create_text_summary(text)

print(f"Complexity: {text_summary['complexity_analysis']}")
print(f"Key Phrases: {text_summary['key_phrases']}")
print(f"Technical Terms: {text_summary['technical_terms']}")
```

## Web Interface

### NLP Analysis Page (`/nlp`)
- **Text Input**: Direct text entry or file upload
- **Entity Extraction**: Configurable entity type extraction
- **Real-time Analysis**: Immediate results display
- **Comprehensive Analysis**: Full NLP pipeline execution

### Features
- **Entity Visualization**: Color-coded entity types
- **Relationship Display**: Interactive relationship graphs
- **Chemical Compound Analysis**: Detailed compound information
- **Safety Information**: Extracted safety data
- **Export Capabilities**: JSON export of results

## API Endpoints

- `POST /nlp/extract-entities` - Extract entities from text
- `POST /nlp/extract-relationships` - Extract relationships
- `POST /nlp/analyze-text` - Analyze text complexity and structure
- `POST /nlp/extract-chemical-compounds` - Extract chemical compounds
- `POST /nlp/extract-safety-information` - Extract safety information
- `POST /nlp/comprehensive-analysis` - Full NLP analysis
- `GET /nlp/dashboard` - NLP dashboard page
- `GET /nlp/stats` - NLP processing statistics

## Entity Types

### Chemical Entities
- **chemical_formula**: H2SO4, NaOH, etc.
- **chemical_name**: Sulfuric acid, Sodium hydroxide
- **cas_number**: CAS registry numbers
- **molecular_formula**: Chemical formulas

### Hazard Entities
- **hazard_corrosive**: Corrosive substances
- **hazard_toxic**: Toxic materials
- **hazard_flammable**: Flammable substances
- **hazard_reactive**: Reactive chemicals
- **hazard_environmental**: Environmental hazards

### Property Entities
- **property_physical_state**: Solid, liquid, gas
- **property_color**: Color descriptions
- **property_odor**: Odor characteristics
- **property_solubility**: Solubility information
- **property_density**: Density properties
- **property_temperature**: Temperature-related properties

## Relationship Types

### Chemical Relationships
- **causes**: Chemical causes effect
- **contains**: Chemical contains component
- **reacts_with**: Chemical reacts with another
- **is_a**: Chemical is a type of
- **has_property**: Chemical has property
- **requires**: Chemical requires condition

### Safety Relationships
- **hazard_relationship**: Chemical presents hazard
- **property_relationship**: Chemical has property
- **usage_relationship**: Chemical used for purpose

## Integration

The NLP Module integrates with other HazardSafe-KG components:

- **RAG System**: Enhances document processing with structured extraction
- **Knowledge Graph**: Populates graph with extracted entities and relationships
- **Ontology Module**: Validates extracted entities against ontology
- **Quality Module**: Assesses extraction quality and confidence

## Configuration

### Entity Extraction Settings
```python
# Configure entity extraction
entity_extractor = EntityExtractor(
    model_name="en_core_web_sm"  # spaCy model
)

# Custom patterns can be added
entity_extractor.chemical_patterns['custom'] = r'your_pattern'
```

### Relationship Extraction Settings
```python
# Configure relationship extraction
relationship_extractor = RelationshipExtractor(
    model_name="en_core_web_sm"
)

# Add custom relationship patterns
relationship_extractor.relationship_patterns['custom'] = [
    r'(\w+)\s+custom_pattern\s+(\w+)'
]
```

## Dependencies

- **spaCy**: Core NLP processing
- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **re**: Regular expressions
- **json**: Data serialization

## Installation

```bash
# Install spaCy model
python -m spacy download en_core_web_sm

# Install dependencies
pip install spacy pandas numpy
```

## Testing

```bash
# Run NLP tests
pytest nlp/tests/

# Test specific components
pytest nlp/tests/test_entity_extractor.py
pytest nlp/tests/test_relationship_extractor.py
```

## Performance

### Optimization Tips
- **Batch Processing**: Process multiple documents together
- **Model Selection**: Choose appropriate spaCy model size
- **Pattern Optimization**: Use efficient regex patterns
- **Caching**: Cache processed results for repeated analysis

### Expected Performance
- **Entity Extraction**: ~1000 words/second
- **Relationship Extraction**: ~500 words/second
- **Text Analysis**: ~2000 words/second
- **Memory Usage**: ~100MB for standard model

## Future Enhancements

### Planned Features
- **Multi-language Support**: Non-English document processing
- **Custom Model Training**: Domain-specific model training
- **Advanced Relationship Extraction**: Graph-based relationship mining
- **Real-time Processing**: Streaming document analysis
- **Integration APIs**: External NLP service integration

### Advanced Capabilities
- **Semantic Similarity**: Entity and relationship similarity
- **Contextual Analysis**: Context-aware entity extraction
- **Temporal Analysis**: Time-based relationship extraction
- **Cross-document Analysis**: Multi-document relationship extraction

## Contributing

1. Follow the existing code structure
2. Add comprehensive tests for new features
3. Update documentation for any changes
4. Ensure entity extraction accuracy
5. Optimize for performance

## License

Part of the HazardSafe-KG platform. See main project license. 