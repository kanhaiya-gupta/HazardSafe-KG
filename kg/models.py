# kg/models.py
"""
Data models and schema definitions for HazardSafe-KG knowledge graph.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

class HazardClass(Enum):
    """Hazard classification types."""
    FLAMMABLE = "flammable"
    TOXIC = "toxic"
    CORROSIVE = "corrosive"
    EXPLOSIVE = "explosive"
    OXIDIZING = "oxidizing"
    ENVIRONMENTAL = "environmental"
    HEALTH = "health"
    IRRITANT = "irritant"
    SENSITIZER = "sensitizer"
    CARCINOGEN = "carcinogen"
    MUTAGEN = "mutagen"
    REPRODUCTIVE_TOXIN = "reproductive_toxin"

class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TestType(Enum):
    """Safety test types."""
    PRESSURE_TEST = "pressure_test"
    LEAK_TEST = "leak_test"
    MATERIAL_COMPATIBILITY = "material_compatibility"
    TEMPERATURE_TEST = "temperature_test"
    CORROSION_TEST = "corrosion_test"
    IMPACT_TEST = "impact_test"

class ContainerMaterial(Enum):
    """Container material types."""
    STAINLESS_STEEL = "stainless_steel"
    GLASS = "glass"
    PLASTIC = "plastic"
    ALUMINUM = "aluminum"
    CARBON_STEEL = "carbon_steel"
    TITANIUM = "titanium"
    CERAMIC = "ceramic"

@dataclass
class HazardousSubstance:
    """Hazardous substance node model."""
    id: str
    name: str
    chemical_formula: Optional[str] = None
    molecular_weight: Optional[float] = None
    hazard_class: Optional[str] = None
    flash_point: Optional[str] = None
    boiling_point: Optional[float] = None
    melting_point: Optional[float] = None
    density: Optional[float] = None
    cas_number: Optional[str] = None
    description: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Neo4j storage."""
        return {
            "id": self.id,
            "name": self.name,
            "chemical_formula": self.chemical_formula,
            "molecular_weight": self.molecular_weight,
            "hazard_class": self.hazard_class,
            "flash_point": self.flash_point,
            "boiling_point": self.boiling_point,
            "melting_point": self.melting_point,
            "density": self.density,
            "cas_number": self.cas_number,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

@dataclass
class Container:
    """Container node model."""
    id: str
    name: str
    material: str
    capacity: float
    unit: str = "L"
    pressure_rating: Optional[float] = None
    temperature_rating: Optional[float] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    description: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Neo4j storage."""
        return {
            "id": self.id,
            "name": self.name,
            "material": self.material,
            "capacity": self.capacity,
            "unit": self.unit,
            "pressure_rating": self.pressure_rating,
            "temperature_rating": self.temperature_rating,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

@dataclass
class SafetyTest:
    """Safety test node model."""
    id: str
    name: str
    test_type: str
    description: Optional[str] = None
    standard: Optional[str] = None
    method: Optional[str] = None
    duration: Optional[float] = None
    temperature: Optional[float] = None
    pressure: Optional[float] = None
    result: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Neo4j storage."""
        return {
            "id": self.id,
            "name": self.name,
            "test_type": self.test_type,
            "description": self.description,
            "standard": self.standard,
            "method": self.method,
            "duration": self.duration,
            "temperature": self.temperature,
            "pressure": self.pressure,
            "result": self.result,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

@dataclass
class RiskAssessment:
    """Risk assessment node model."""
    id: str
    title: str
    substance_id: str
    risk_level: str
    hazards: Optional[str] = None
    mitigation: Optional[str] = None
    ppe_required: Optional[str] = None
    storage_requirements: Optional[str] = None
    emergency_procedures: Optional[str] = None
    assessor: Optional[str] = None
    assessment_date: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Neo4j storage."""
        return {
            "id": self.id,
            "title": self.title,
            "substance_id": self.substance_id,
            "risk_level": self.risk_level,
            "hazards": self.hazards,
            "mitigation": self.mitigation,
            "ppe_required": self.ppe_required,
            "storage_requirements": self.storage_requirements,
            "emergency_procedures": self.emergency_procedures,
            "assessor": self.assessor,
            "assessment_date": self.assessment_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

@dataclass
class Location:
    """Location node model."""
    id: str
    name: str
    location_type: str  # lab, warehouse, storage_room, etc.
    building: Optional[str] = None
    floor: Optional[str] = None
    room: Optional[str] = None
    description: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Neo4j storage."""
        return {
            "id": self.id,
            "name": self.name,
            "location_type": self.location_type,
            "building": self.building,
            "floor": self.floor,
            "room": self.room,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

# Relationship types
class RelationshipType:
    """Relationship type constants."""
    HAS_HAZARD_CLASS = "HAS_HAZARD_CLASS"
    STORED_IN = "STORED_IN"
    TESTED_WITH = "TESTED_WITH"
    ASSESSED_FOR = "ASSESSED_FOR"
    COMPATIBLE_WITH = "COMPATIBLE_WITH"
    INCOMPATIBLE_WITH = "INCOMPATIBLE_WITH"
    REQUIRES_PPE = "REQUIRES_PPE"
    LOCATED_AT = "LOCATED_AT"
    MANUFACTURED_BY = "MANUFACTURED_BY"
    CONTAINS = "CONTAINS"
    SIMILAR_TO = "SIMILAR_TO"
    REPLACES = "REPLACES"

# Graph schema definition
GRAPH_SCHEMA = {
    "nodes": {
        "HazardousSubstance": {
            "properties": [
                "id", "name", "chemical_formula", "molecular_weight", 
                "hazard_class", "flash_point", "boiling_point", 
                "melting_point", "density", "cas_number", "description",
                "created_at", "updated_at"
            ],
            "required": ["id", "name"],
            "indexes": ["name", "chemical_formula", "cas_number"]
        },
        "Container": {
            "properties": [
                "id", "name", "material", "capacity", "unit",
                "pressure_rating", "temperature_rating", "manufacturer",
                "model", "description", "created_at", "updated_at"
            ],
            "required": ["id", "name", "material", "capacity"],
            "indexes": ["name", "material", "manufacturer"]
        },
        "SafetyTest": {
            "properties": [
                "id", "name", "test_type", "description", "standard",
                "method", "duration", "temperature", "pressure", "result",
                "created_at", "updated_at"
            ],
            "required": ["id", "name", "test_type"],
            "indexes": ["name", "test_type"]
        },
        "RiskAssessment": {
            "properties": [
                "id", "title", "substance_id", "risk_level", "hazards",
                "mitigation", "ppe_required", "storage_requirements",
                "emergency_procedures", "assessor", "assessment_date",
                "created_at", "updated_at"
            ],
            "required": ["id", "title", "substance_id", "risk_level"],
            "indexes": ["title", "risk_level", "assessor"]
        },
        "Location": {
            "properties": [
                "id", "name", "location_type", "building", "floor",
                "room", "description", "created_at", "updated_at"
            ],
            "required": ["id", "name", "location_type"],
            "indexes": ["name", "location_type", "building"]
        }
    },
    "relationships": {
        "HAS_HAZARD_CLASS": {
            "start_node": "HazardousSubstance",
            "end_node": "HazardClass",
            "properties": ["created_at"]
        },
        "STORED_IN": {
            "start_node": "HazardousSubstance",
            "end_node": "Container",
            "properties": ["quantity", "date_stored", "created_at"]
        },
        "TESTED_WITH": {
            "start_node": "HazardousSubstance",
            "end_node": "SafetyTest",
            "properties": ["test_date", "result", "created_at"]
        },
        "ASSESSED_FOR": {
            "start_node": "HazardousSubstance",
            "end_node": "RiskAssessment",
            "properties": ["assessment_date", "created_at"]
        },
        "COMPATIBLE_WITH": {
            "start_node": "HazardousSubstance",
            "end_node": "HazardousSubstance",
            "properties": ["compatibility_level", "notes", "created_at"]
        },
        "INCOMPATIBLE_WITH": {
            "start_node": "HazardousSubstance",
            "end_node": "HazardousSubstance",
            "properties": ["incompatibility_reason", "created_at"]
        },
        "LOCATED_AT": {
            "start_node": "Container",
            "end_node": "Location",
            "properties": ["date_placed", "created_at"]
        }
    }
} 