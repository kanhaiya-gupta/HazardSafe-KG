"""
Relationship Extractor Module

Extracts relationships between entities in hazardous substance documents
using NLP techniques and pattern matching.
"""

import re
import spacy
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Relationship:
    """Represents an extracted relationship between entities."""
    source_entity: str
    target_entity: str
    relationship_type: str
    confidence: float
    source_text: str
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


class RelationshipExtractor:
    """Extracts relationships between entities in text."""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize the relationship extractor."""
        try:
            self.nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy model for relationship extraction: {model_name}")
        except OSError:
            logger.warning(f"Model {model_name} not found. Installing...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", model_name])
            self.nlp = spacy.load(model_name)
        
        # Define relationship patterns for hazardous substances
        self.relationship_patterns = {
            'causes': [
                r'(\w+)\s+causes?\\s+(\w+)',
                r'(\w+)\s+results?\s+in\s+(\w+)',
                r'(\w+)\s+leads?\s+to\s+(\w+)',
                r'(\w+)\s+produces?\s+(\w+)'
            ],
            'contains': [
                r'(\w+)\s+contains?\s+(\w+)',
                r'(\w+)\s+includes?\s+(\w+)',
                r'(\w+)\s+consists?\s+of\s+(\w+)',
                r'(\w+)\s+composed?\s+of\s+(\w+)'
            ],
            'reacts_with': [
                r'(\w+)\s+reacts?\s+with\s+(\w+)',
                r'(\w+)\s+combines?\s+with\s+(\w+)',
                r'(\w+)\s+mixes?\s+with\s+(\w+)',
                r'(\w+)\s+interacts?\s+with\s+(\w+)'
            ],
            'is_a': [
                r'(\w+)\s+is\s+a\s+(\w+)',
                r'(\w+)\s+is\s+an\s+(\w+)',
                r'(\w+)\s+belongs?\s+to\s+(\w+)',
                r'(\w+)\s+classified?\s+as\s+(\w+)'
            ],
            'has_property': [
                r'(\w+)\s+has?\s+(\w+)',
                r'(\w+)\s+exhibits?\s+(\w+)',
                r'(\w+)\s+shows?\s+(\w+)',
                r'(\w+)\s+displays?\s+(\w+)'
            ],
            'requires': [
                r'(\w+)\s+requires?\s+(\w+)',
                r'(\w+)\s+needs?\s+(\w+)',
                r'(\w+)\s+demands?\s+(\w+)',
                r'(\w+)\s+calls?\s+for\s+(\w+)'
            ]
        }
        
        # Define dependency patterns for more complex relationships
        self.dependency_patterns = {
            'subject_verb_object': ['nsubj', 'dobj'],
            'prepositional': ['prep'],
            'adjectival': ['amod'],
            'nominal': ['compound']
        }
    
    def extract_relationships(self, text: str, entities: List[Any]) -> List[Relationship]:
        """Extract relationships between entities in the text."""
        relationships = []
        
        # Extract pattern-based relationships
        pattern_relationships = self._extract_pattern_relationships(text, entities)
        relationships.extend(pattern_relationships)
        
        # Extract dependency-based relationships
        dependency_relationships = self._extract_dependency_relationships(text, entities)
        relationships.extend(dependency_relationships)
        
        # Extract semantic relationships
        semantic_relationships = self._extract_semantic_relationships(text, entities)
        relationships.extend(semantic_relationships)
        
        # Remove duplicates
        relationships = self._deduplicate_relationships(relationships)
        
        return relationships
    
    def _extract_pattern_relationships(self, text: str, entities: List[Any]) -> List[Relationship]:
        """Extract relationships using predefined patterns."""
        relationships = []
        
        for rel_type, patterns in self.relationship_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    source = match.group(1)
                    target = match.group(2)
                    
                    # Check if source and target are in our entity list
                    if self._is_entity(source, entities) and self._is_entity(target, entities):
                        relationship = Relationship(
                            source_entity=source,
                            target_entity=target,
                            relationship_type=rel_type,
                            confidence=0.8,
                            source_text=match.group(),
                            properties={'pattern_type': pattern}
                        )
                        relationships.append(relationship)
        
        return relationships
    
    def _extract_dependency_relationships(self, text: str, entities: List[Any]) -> List[Relationship]:
        """Extract relationships using spaCy dependency parsing."""
        relationships = []
        doc = self.nlp(text)
        
        # Get entity positions
        entity_positions = {}
        for entity in entities:
            entity_positions[entity.text.lower()] = (entity.start_pos, entity.end_pos)
        
        for token in doc:
            # Look for subject-verb-object relationships
            if token.dep_ == 'nsubj' and token.head.pos_ == 'VERB':
                subject = token.text
                verb = token.head.text
                
                # Find object of the verb
                for child in token.head.children:
                    if child.dep_ == 'dobj':
                        object_text = child.text
                        
                        if (self._is_entity(subject, entities) and 
                            self._is_entity(object_text, entities)):
                            
                            relationship = Relationship(
                                source_entity=subject,
                                target_entity=object_text,
                                relationship_type=f"{verb}_action",
                                confidence=0.7,
                                source_text=f"{subject} {verb} {object_text}",
                                properties={'dependency_type': 'svo', 'verb': verb}
                            )
                            relationships.append(relationship)
            
            # Look for prepositional relationships
            elif token.dep_ == 'prep':
                prep_text = token.text
                head = token.head.text
                
                # Find object of preposition
                for child in token.children:
                    if child.dep_ == 'pobj':
                        object_text = child.text
                        
                        if (self._is_entity(head, entities) and 
                            self._is_entity(object_text, entities)):
                            
                            relationship = Relationship(
                                source_entity=head,
                                target_entity=object_text,
                                relationship_type=f"{prep_text}_relation",
                                confidence=0.6,
                                source_text=f"{head} {prep_text} {object_text}",
                                properties={'dependency_type': 'prep', 'preposition': prep_text}
                            )
                            relationships.append(relationship)
        
        return relationships
    
    def _extract_semantic_relationships(self, text: str, entities: List[Any]) -> List[Relationship]:
        """Extract relationships based on semantic similarity and context."""
        relationships = []
        
        # Define semantic relationship keywords
        semantic_patterns = {
            'hazard_relationship': [
                r'(\w+)\s+is\s+hazardous\s+because\s+it\s+(\w+)',
                r'(\w+)\s+presents?\s+a\s+(\w+)\s+risk',
                r'(\w+)\s+poses?\s+a\s+(\w+)\s+threat'
            ],
            'property_relationship': [
                r'(\w+)\s+has?\s+a\s+(\w+)\s+property',
                r'(\w+)\s+characterized?\s+by\s+(\w+)',
                r'(\w+)\s+known?\s+for\s+its\s+(\w+)'
            ],
            'usage_relationship': [
                r'(\w+)\s+used?\s+for\s+(\w+)',
                r'(\w+)\s+applied?\s+in\s+(\w+)',
                r'(\w+)\s+employed?\s+for\s+(\w+)'
            ]
        }
        
        for rel_type, patterns in semantic_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    source = match.group(1)
                    target = match.group(2)
                    
                    if self._is_entity(source, entities) and self._is_entity(target, entities):
                        relationship = Relationship(
                            source_entity=source,
                            target_entity=target,
                            relationship_type=rel_type,
                            confidence=0.75,
                            source_text=match.group(),
                            properties={'semantic_type': rel_type}
                        )
                        relationships.append(relationship)
        
        return relationships
    
    def _is_entity(self, text: str, entities: List[Any]) -> bool:
        """Check if text matches any entity in the list."""
        text_lower = text.lower()
        for entity in entities:
            if hasattr(entity, 'text'):
                if text_lower == entity.text.lower():
                    return True
            else:
                # Handle case where entities might be strings
                if text_lower == entity.lower():
                    return True
        return False
    
    def _deduplicate_relationships(self, relationships: List[Relationship]) -> List[Relationship]:
        """Remove duplicate relationships."""
        seen = set()
        unique_relationships = []
        
        for rel in relationships:
            key = (rel.source_entity.lower(), rel.target_entity.lower(), rel.relationship_type)
            if key not in seen:
                seen.add(key)
                unique_relationships.append(rel)
        
        return unique_relationships
    
    def extract_chemical_relationships(self, text: str, entities: List[Any]) -> List[Dict[str, Any]]:
        """Extract chemical-specific relationships."""
        relationships = self.extract_relationships(text, entities)
        chemical_relationships = []
        
        for rel in relationships:
            # Check if relationship involves chemical entities
            if (self._is_chemical_entity(rel.source_entity, entities) or 
                self._is_chemical_entity(rel.target_entity, entities)):
                
                chemical_rel = {
                    'source': rel.source_entity,
                    'target': rel.target_entity,
                    'relationship_type': rel.relationship_type,
                    'confidence': rel.confidence,
                    'source_text': rel.source_text,
                    'properties': rel.properties
                }
                chemical_relationships.append(chemical_rel)
        
        return chemical_relationships
    
    def _is_chemical_entity(self, text: str, entities: List[Any]) -> bool:
        """Check if entity is a chemical entity."""
        for entity in entities:
            if hasattr(entity, 'text') and entity.text.lower() == text.lower():
                return entity.entity_type.startswith('chemical')
            elif hasattr(entity, 'entity_type') and entity.entity_type.startswith('chemical'):
                return True
        return False
    
    def extract_safety_relationships(self, text: str, entities: List[Any]) -> List[Dict[str, Any]]:
        """Extract safety-related relationships."""
        relationships = self.extract_relationships(text, entities)
        safety_relationships = []
        
        safety_keywords = ['hazard', 'safety', 'risk', 'danger', 'toxic', 'corrosive', 'flammable']
        
        for rel in relationships:
            # Check if relationship involves safety-related entities
            if (self._is_safety_entity(rel.source_entity, entities) or 
                self._is_safety_entity(rel.target_entity, entities) or
                any(keyword in rel.source_text.lower() for keyword in safety_keywords)):
                
                safety_rel = {
                    'source': rel.source_entity,
                    'target': rel.target_entity,
                    'relationship_type': rel.relationship_type,
                    'confidence': rel.confidence,
                    'source_text': rel.source_text,
                    'properties': rel.properties
                }
                safety_relationships.append(safety_rel)
        
        return safety_relationships
    
    def _is_safety_entity(self, text: str, entities: List[Any]) -> bool:
        """Check if entity is a safety-related entity."""
        for entity in entities:
            if hasattr(entity, 'text') and entity.text.lower() == text.lower():
                return entity.entity_type.startswith('hazard')
        return False
    
    def build_relationship_graph(self, relationships: List[Relationship]) -> Dict[str, Any]:
        """Build a graph representation of relationships."""
        graph = {
            'nodes': set(),
            'edges': [],
            'node_types': {},
            'edge_types': {}
        }
        
        for rel in relationships:
            # Add nodes
            graph['nodes'].add(rel.source_entity)
            graph['nodes'].add(rel.target_entity)
            
            # Add edge
            edge = {
                'source': rel.source_entity,
                'target': rel.target_entity,
                'type': rel.relationship_type,
                'confidence': rel.confidence,
                'properties': rel.properties
            }
            graph['edges'].append(edge)
            
            # Track edge types
            if rel.relationship_type not in graph['edge_types']:
                graph['edge_types'][rel.relationship_type] = 0
            graph['edge_types'][rel.relationship_type] += 1
        
        # Convert nodes set to list
        graph['nodes'] = list(graph['nodes'])
        
        return graph
    
    def export_relationships(self, relationships: List[Relationship], filepath: str) -> None:
        """Export relationships to JSON file."""
        try:
            data = []
            for rel in relationships:
                data.append({
                    'source_entity': rel.source_entity,
                    'target_entity': rel.target_entity,
                    'relationship_type': rel.relationship_type,
                    'confidence': rel.confidence,
                    'source_text': rel.source_text,
                    'properties': rel.properties
                })
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Relationships exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export relationships: {e}")
    
    def get_relationship_statistics(self, relationships: List[Relationship]) -> Dict[str, Any]:
        """Get statistics about extracted relationships."""
        stats = {
            'total_relationships': len(relationships),
            'relationship_types': {},
            'confidence_distribution': {
                'high': 0,    # > 0.8
                'medium': 0,  # 0.6-0.8
                'low': 0      # < 0.6
            },
            'entity_pairs': set()
        }
        
        for rel in relationships:
            # Count relationship types
            rel_type = rel.relationship_type
            stats['relationship_types'][rel_type] = stats['relationship_types'].get(rel_type, 0) + 1
            
            # Count confidence levels
            if rel.confidence > 0.8:
                stats['confidence_distribution']['high'] += 1
            elif rel.confidence > 0.6:
                stats['confidence_distribution']['medium'] += 1
            else:
                stats['confidence_distribution']['low'] += 1
            
            # Track unique entity pairs
            pair = tuple(sorted([rel.source_entity, rel.target_entity]))
            stats['entity_pairs'].add(pair)
        
        stats['unique_entity_pairs'] = len(stats['entity_pairs'])
        
        return stats 