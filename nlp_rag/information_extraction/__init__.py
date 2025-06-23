"""
NLP Module for HazardSafe-KG

This module provides natural language processing capabilities for entity recognition,
relationship extraction, and structured information extraction from hazardous substance documents.
"""

__version__ = "1.0.0"
__author__ = "HazardSafe-KG Team"

from .entity_extractor import EntityExtractor
from .relationship_extractor import RelationshipExtractor
from .text_processor import TextProcessor

__all__ = [
    "EntityExtractor",
    "RelationshipExtractor", 
    "TextProcessor"
] 