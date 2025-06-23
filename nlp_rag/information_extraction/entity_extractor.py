"""
Entity Extractor Module

Extracts chemical entities, hazards, properties, and other relevant information
from hazardous substance documents using NLP techniques.
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
class Entity:
    """Represents an extracted entity."""
    text: str
    entity_type: str
    confidence: float
    start_pos: int
    end_pos: int
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


class EntityExtractor:
    """Extracts entities from hazardous substance documents."""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize the entity extractor."""
        try:
            self.nlp = spacy.load(model_name)
            logger.info(f"Loaded spaCy model: {model_name}")
        except OSError:
            logger.warning(f"Model {model_name} not found. Installing...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", model_name])
            self.nlp = spacy.load(model_name)
        
        # Define entity patterns for hazardous substances
        self.chemical_patterns = {
            'chemical_formula': r'\b[A-Z][a-z]?\d*[A-Z][a-z]?\d*\b',  # H2SO4, NaOH, etc.
            'chemical_name': r'\b[a-zA-Z\s]+(?:acid|base|hydroxide|chloride|sulfate|nitrate|oxide)\b',
            'cas_number': r'\b\d{1,7}-\d{2}-\d\b',  # CAS registry numbers
            'molecular_formula': r'\b[A-Z][a-z]?\d*[A-Z][a-z]?\d*\b'
        }
        
        # Define hazard and property keywords
        self.hazard_keywords = {
            'corrosive': ['corrosive', 'caustic', 'acidic', 'alkaline', 'burns'],
            'toxic': ['toxic', 'poisonous', 'harmful', 'lethal', 'deadly'],
            'flammable': ['flammable', 'combustible', 'ignitable', 'explosive'],
            'reactive': ['reactive', 'unstable', 'oxidizing', 'reducing'],
            'environmental': ['environmental hazard', 'pollutant', 'contaminant']
        }
        
        self.property_keywords = {
            'physical_state': ['solid', 'liquid', 'gas', 'powder', 'crystal'],
            'color': ['colorless', 'white', 'yellow', 'brown', 'red', 'blue'],
            'odor': ['odorless', 'pungent', 'sweet', 'bitter', 'foul'],
            'solubility': ['soluble', 'insoluble', 'miscible', 'immiscible'],
            'density': ['dense', 'light', 'heavy', 'specific gravity'],
            'temperature': ['boiling point', 'melting point', 'flash point']
        }
    
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract all entities from the given text."""
        entities = []
        
        # Use spaCy for general entity extraction
        doc = self.nlp(text)
        
        # Extract named entities
        for ent in doc.ents:
            entity = Entity(
                text=ent.text,
                entity_type=ent.label_,
                confidence=0.8,  # spaCy doesn't provide confidence scores
                start_pos=ent.start_char,
                end_pos=ent.end_char
            )
            entities.append(entity)
        
        # Extract chemical entities using patterns
        chemical_entities = self._extract_chemical_entities(text)
        entities.extend(chemical_entities)
        
        # Extract hazard entities
        hazard_entities = self._extract_hazard_entities(text)
        entities.extend(hazard_entities)
        
        # Extract property entities
        property_entities = self._extract_property_entities(text)
        entities.extend(property_entities)
        
        # Remove duplicates and sort by position
        entities = self._deduplicate_entities(entities)
        entities.sort(key=lambda x: x.start_pos)
        
        return entities
    
    def _extract_chemical_entities(self, text: str) -> List[Entity]:
        """Extract chemical entities using regex patterns."""
        entities = []
        
        for pattern_name, pattern in self.chemical_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity = Entity(
                    text=match.group(),
                    entity_type=f"chemical_{pattern_name}",
                    confidence=0.9,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    properties={'pattern_type': pattern_name}
                )
                entities.append(entity)
        
        return entities
    
    def _extract_hazard_entities(self, text: str) -> List[Entity]:
        """Extract hazard-related entities."""
        entities = []
        
        for hazard_type, keywords in self.hazard_keywords.items():
            for keyword in keywords:
                matches = re.finditer(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE)
                for match in matches:
                    entity = Entity(
                        text=match.group(),
                        entity_type=f"hazard_{hazard_type}",
                        confidence=0.85,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        properties={'hazard_category': hazard_type}
                    )
                    entities.append(entity)
        
        return entities
    
    def _extract_property_entities(self, text: str) -> List[Entity]:
        """Extract property-related entities."""
        entities = []
        
        for property_type, keywords in self.property_keywords.items():
            for keyword in keywords:
                matches = re.finditer(rf'\b{re.escape(keyword)}\b', text, re.IGNORECASE)
                for match in matches:
                    entity = Entity(
                        text=match.group(),
                        entity_type=f"property_{property_type}",
                        confidence=0.8,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        properties={'property_category': property_type}
                    )
                    entities.append(entity)
        
        return entities
    
    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """Remove duplicate entities based on text and position."""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            key = (entity.text.lower(), entity.start_pos, entity.end_pos)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def extract_chemical_compounds(self, text: str) -> List[Dict[str, Any]]:
        """Extract chemical compounds with their properties."""
        entities = self.extract_entities(text)
        compounds = []
        
        # Group entities by proximity to identify compounds
        chemical_entities = [e for e in entities if e.entity_type.startswith('chemical')]
        
        for entity in chemical_entities:
            compound = {
                'name': entity.text,
                'type': entity.entity_type,
                'confidence': entity.confidence,
                'properties': entity.properties.copy(),
                'hazards': [],
                'physical_properties': []
            }
            
            # Find associated hazards and properties
            for other_entity in entities:
                if other_entity.entity_type.startswith('hazard'):
                    # Check if hazard is mentioned near the chemical
                    if self._entities_are_related(entity, other_entity, text):
                        compound['hazards'].append({
                            'type': other_entity.entity_type,
                            'description': other_entity.text,
                            'category': other_entity.properties.get('hazard_category', '')
                        })
                
                elif other_entity.entity_type.startswith('property'):
                    if self._entities_are_related(entity, other_entity, text):
                        compound['physical_properties'].append({
                            'type': other_entity.entity_type,
                            'description': other_entity.text,
                            'category': other_entity.properties.get('property_category', '')
                        })
            
            compounds.append(compound)
        
        return compounds
    
    def _entities_are_related(self, entity1: Entity, entity2: Entity, text: str, max_distance: int = 100) -> bool:
        """Check if two entities are related based on proximity in text."""
        distance = abs(entity1.start_pos - entity2.start_pos)
        return distance <= max_distance
    
    def extract_safety_information(self, text: str) -> Dict[str, Any]:
        """Extract safety-related information from text."""
        entities = self.extract_entities(text)
        
        safety_info = {
            'hazards': [],
            'precautions': [],
            'first_aid': [],
            'storage_conditions': [],
            'disposal_methods': []
        }
        
        # Extract hazards
        hazard_entities = [e for e in entities if e.entity_type.startswith('hazard')]
        for entity in hazard_entities:
            safety_info['hazards'].append({
                'type': entity.entity_type,
                'description': entity.text,
                'category': entity.properties.get('hazard_category', '')
            })
        
        # Extract precautions (look for safety-related phrases)
        precaution_patterns = [
            r'wear\s+protective\s+equipment',
            r'use\s+in\s+well-ventilated\s+area',
            r'avoid\s+contact\s+with',
            r'keep\s+away\s+from',
            r'store\s+in\s+a\s+cool\s+place'
        ]
        
        for pattern in precaution_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                safety_info['precautions'].append(match.group())
        
        # Extract first aid information
        first_aid_patterns = [
            r'rinse\s+with\s+water',
            r'seek\s+medical\s+attention',
            r'remove\s+contaminated\s+clothing',
            r'flush\s+eyes\s+with\s+water'
        ]
        
        for pattern in first_aid_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                safety_info['first_aid'].append(match.group())
        
        return safety_info
    
    def export_entities(self, entities: List[Entity], filepath: str) -> None:
        """Export extracted entities to JSON file."""
        try:
            data = []
            for entity in entities:
                data.append({
                    'text': entity.text,
                    'entity_type': entity.entity_type,
                    'confidence': entity.confidence,
                    'start_pos': entity.start_pos,
                    'end_pos': entity.end_pos,
                    'properties': entity.properties
                })
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Entities exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export entities: {e}")
    
    def get_entity_statistics(self, entities: List[Entity]) -> Dict[str, Any]:
        """Get statistics about extracted entities."""
        stats = {
            'total_entities': len(entities),
            'entity_types': {},
            'confidence_distribution': {
                'high': 0,    # > 0.8
                'medium': 0,  # 0.6-0.8
                'low': 0      # < 0.6
            }
        }
        
        for entity in entities:
            # Count entity types
            entity_type = entity.entity_type
            stats['entity_types'][entity_type] = stats['entity_types'].get(entity_type, 0) + 1
            
            # Count confidence levels
            if entity.confidence > 0.8:
                stats['confidence_distribution']['high'] += 1
            elif entity.confidence > 0.6:
                stats['confidence_distribution']['medium'] += 1
            else:
                stats['confidence_distribution']['low'] += 1
        
        return stats 