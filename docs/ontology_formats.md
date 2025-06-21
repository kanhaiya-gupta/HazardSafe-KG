# Ontology Formats Support in HazardSafe-KG

HazardSafe-KG supports a comprehensive range of ontology file formats for maximum interoperability and flexibility in working with hazardous substance ontologies.

## Supported Formats

### 1. Turtle (.ttl)
**Description**: Readable RDF format  
**Use Case**: Human-readable ontology files, easy to edit manually  
**Example**:
```turtle
@prefix hs: <http://hazardsafe-kg.org/ontology#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

hs:HazardousSubstance a owl:Class ;
    rdfs:label "Hazardous Substance" ;
    rdfs:comment "A chemical substance that poses risks to health, safety, or the environment" .

hs:Ethanol a hs:FlammableSubstance ;
    rdfs:label "Ethanol" ;
    hs:chemicalFormula "C2H5OH" ;
    hs:molecularWeight 46.07 ;
    hs:flashPoint 13.0 .
```

### 2. OWL (.owl)
**Description**: Web Ontology Language  
**Use Case**: Standard ontology format, widely supported by ontology editors  
**Example**:
```xml
<?xml version="1.0"?>
<rdf:RDF xmlns="http://hazardsafe-kg.org/ontology#"
     xmlns:owl="http://www.w3.org/2002/07/owl#"
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">

    <owl:Class rdf:about="#HazardousSubstance">
        <rdfs:label>Hazardous Substance</rdfs:label>
        <rdfs:comment>A chemical substance that poses risks to health, safety, or the environment</rdfs:comment>
    </owl:Class>

    <owl:DatatypeProperty rdf:about="#chemicalFormula">
        <rdfs:label>Chemical Formula</rdfs:label>
        <rdfs:domain rdf:resource="#HazardousSubstance"/>
        <rdfs:range rdf:resource="http://www.w3.org/2001/XMLSchema#string"/>
    </owl:DatatypeProperty>

</rdf:RDF>
```

### 3. RDF/XML (.rdf, .xml)
**Description**: XML-based RDF format  
**Use Case**: Standard RDF format, good for programmatic processing  
**Example**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
         xmlns:hs="http://hazardsafe-kg.org/ontology#">

    <hs:SafetyRegulation rdf:about="#OSHA1910_1200">
        <rdfs:label>OSHA Hazard Communication Standard</rdfs:label>
        <hs:regulationCode>29 CFR 1910.1200</hs:regulationCode>
        <hs:effectiveDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2012-05-25</hs:effectiveDate>
    </hs:SafetyRegulation>

</rdf:RDF>
```

### 4. JSON-LD (.json, .jsonld)
**Description**: JSON for Linked Data  
**Use Case**: Web-friendly format, easy to integrate with JavaScript applications  
**Example**:
```json
{
  "@context": {
    "@vocab": "http://hazardsafe-kg.org/ontology#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#"
  },
  "@graph": [
    {
      "@id": "http://hazardsafe-kg.org/ontology#SafetyProcedure",
      "@type": "owl:Class",
      "rdfs:label": "Safety Procedure",
      "rdfs:comment": "A documented procedure for handling hazardous substances safely"
    },
    {
      "@id": "http://hazardsafe-kg.org/ontology#SpillCleanupProcedure",
      "@type": "http://hazardsafe-kg.org/ontology#EmergencyProcedure",
      "rdfs:label": "Chemical Spill Cleanup Procedure",
      "hs:procedureName": "Chemical Spill Cleanup",
      "hs:riskLevel": "High"
    }
  ]
}
```

### 5. N-Triples (.nt)
**Description**: Simple line-based RDF format  
**Use Case**: Simple, one triple per line format, good for processing  
**Example**:
```
<http://hazardsafe-kg.org/ontology#SafetyEquipment> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .
<http://hazardsafe-kg.org/ontology#SafetyEquipment> <http://www.w3.org/2000/01/rdf-schema#label> "Safety Equipment" .
<http://hazardsafe-kg.org/ontology#PPE> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .
<http://hazardsafe-kg.org/ontology#PPE> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://hazardsafe-kg.org/ontology#SafetyEquipment> .
```

### 6. Notation3 (.n3)
**Description**: Extended Turtle format  
**Use Case**: More expressive than Turtle, supports advanced features  
**Example**:
```n3
@prefix hs: <http://hazardsafe-kg.org/ontology#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

hs:FlammableSubstance a owl:Class ;
    rdfs:subClassOf hs:HazardousSubstance ;
    rdfs:label "Flammable Substance" .

hs:Ethanol a hs:FlammableSubstance ;
    rdfs:label "Ethanol" ;
    hs:flashPoint 13.0 ;
    hs:boilingPoint 78.37 .
```

### 7. TriG (.trig)
**Description**: Turtle for named graphs  
**Use Case**: Multiple graphs in one file, advanced RDF datasets  
**Example**:
```trig
@prefix hs: <http://hazardsafe-kg.org/ontology#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

<http://hazardsafe-kg.org/dataset/classes> {
    hs:HazardousSubstance a owl:Class ;
        rdfs:label "Hazardous Substance" .
}

<http://hazardsafe-kg.org/dataset/instances> {
    hs:Ethanol a hs:FlammableSubstance ;
        rdfs:label "Ethanol" ;
        hs:chemicalFormula "C2H5OH" .
}
```

### 8. SHACL (.shacl, .shapes)
**Description**: Shapes Constraint Language  
**Use Case**: Data validation and constraints  
**Example**:
```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix hs: <http://hazardsafe-kg.org/ontology#> .

hs:HazardousSubstanceShape
    a sh:NodeShape ;
    sh:targetClass hs:HazardousSubstance ;
    sh:property [
        sh:path hs:chemicalFormula ;
        sh:datatype xsd:string ;
        sh:minLength 1 ;
        sh:maxLength 50 ;
        sh:pattern "^[A-Z][a-z]?[0-9]*$" ;
        sh:message "Chemical formula must be a valid molecular formula" ;
    ] ;
    sh:property [
        sh:path hs:molecularWeight ;
        sh:datatype xsd:float ;
        sh:minInclusive 0.0 ;
        sh:maxInclusive 10000.0 ;
        sh:message "Molecular weight must be between 0 and 10000 g/mol" ;
    ] .
```

## Format Conversion

HazardSafe-KG supports converting between all supported formats:

### API Endpoint
```
POST /ontology/convert
```

### Parameters
- `input_file`: The ontology file to convert
- `output_format`: Target format (ttl, owl, rdf, xml, json, jsonld, nt, n3, trig)

### Example Usage
```bash
curl -X POST "http://localhost:8000/ontology/convert" \
  -F "input_file=@hazardsafe.owl" \
  -F "output_format=ttl"
```

## File Upload

Upload ontology files in any supported format:

### API Endpoint
```
POST /ontology/upload
```

### Parameters
- `file`: The ontology file to upload
- `format`: Optional format specification

### Example Usage
```bash
curl -X POST "http://localhost:8000/ontology/upload" \
  -F "file=@hazardsafe.jsonld"
```

## Export

Export the current ontology in any supported format:

### API Endpoint
```
GET /ontology/export?format={format}
```

### Example Usage
```bash
curl "http://localhost:8000/ontology/export?format=owl" > hazardsafe.owl
```

## Format Selection Guidelines

### Choose Turtle (.ttl) when:
- You need human-readable files
- Manual editing is required
- Simple ontologies without complex features

### Choose OWL (.owl) when:
- Working with ontology editors (Protégé, etc.)
- Need full OWL 2 features
- Interoperability with other ontology tools

### Choose RDF/XML (.rdf) when:
- Programmatic processing is needed
- Integration with XML-based systems
- Standard RDF compliance is required

### Choose JSON-LD (.jsonld) when:
- Web application integration
- JavaScript-based processing
- REST API integration

### Choose N-Triples (.nt) when:
- Simple processing is needed
- One triple per line format is preferred
- Large datasets with simple structure

### Choose Notation3 (.n3) when:
- Advanced RDF features are needed
- More expressive than Turtle required
- Complex logical expressions

### Choose TriG (.trig) when:
- Multiple named graphs in one file
- Dataset-level organization
- Advanced RDF dataset features

### Choose SHACL (.shacl) when:
- Data validation is required
- Constraint checking is needed
- Data quality enforcement

## Best Practices

1. **Consistency**: Use the same format throughout your project for consistency
2. **Tool Compatibility**: Choose formats compatible with your ontology editing tools
3. **Validation**: Use SHACL shapes for data validation
4. **Versioning**: Include version information in your ontology files
5. **Documentation**: Document your ontology structure and conventions
6. **Backup**: Keep backups in multiple formats for safety

## Integration Examples

### Python with rdflib
```python
from rdflib import Graph

# Load ontology
g = Graph()
g.parse("hazardsafe.owl", format="xml")

# Query ontology
for s, p, o in g.triples((None, None, None)):
    print(f"{s} {p} {o}")
```

### JavaScript with JSON-LD
```javascript
// Load JSON-LD ontology
const ontology = await fetch('/ontology/export?format=jsonld')
    .then(response => response.json());

// Process ontology data
ontology['@graph'].forEach(item => {
    if (item['@type'] === 'owl:Class') {
        console.log(`Class: ${item['rdfs:label']}`);
    }
});
```

### SPARQL Querying
```sparql
PREFIX hs: <http://hazardsafe-kg.org/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?substance ?label ?formula
WHERE {
    ?substance a hs:HazardousSubstance .
    ?substance rdfs:label ?label .
    ?substance hs:chemicalFormula ?formula .
}
```

This comprehensive format support ensures that HazardSafe-KG can work with ontologies from any source and integrate seamlessly with existing systems and tools. 