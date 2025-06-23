"""
Validation rules and safety checks for HazardSafe-KG platform.
"""

import logging
from typing import Dict, List, Any, Optional
import pandas as pd
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class ValidationEngine:
    """Engine for validating data and safety rules."""
    
    def __init__(self):
        self.validation_rules = self._load_validation_rules()
        
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules for different data types."""
        return {
            "substances": {
                "required_fields": ["name", "hazard_class"],
                "field_types": {
                    "name": "string",
                    "chemical_formula": "string",
                    "molecular_weight": "float",
                    "hazard_class": "string",
                    "flash_point": "string_or_float",
                    "boiling_point": "float",
                    "melting_point": "float",
                    "density": "float"
                },
                "hazard_classes": [
                    "flammable", "toxic", "corrosive", "explosive", 
                    "oxidizing", "environmental", "health"
                ],
                "constraints": {
                    "molecular_weight": {"min": 0, "max": 10000},
                    "boiling_point": {"min": -273, "max": 5000},
                    "melting_point": {"min": -273, "max": 5000},
                    "density": {"min": 0, "max": 100}
                }
            },
            "containers": {
                "required_fields": ["name", "material", "capacity"],
                "field_types": {
                    "name": "string",
                    "material": "string",
                    "capacity": "float",
                    "unit": "string",
                    "pressure_rating": "float",
                    "temperature_rating": "float",
                    "manufacturer": "string",
                    "model": "string"
                },
                "materials": [
                    "stainless_steel", "glass", "plastic", "aluminum", 
                    "carbon_steel", "titanium", "ceramic"
                ],
                "constraints": {
                    "capacity": {"min": 0, "max": 100000},
                    "pressure_rating": {"min": 0, "max": 10000},
                    "temperature_rating": {"min": -200, "max": 1000}
                }
            },
            "tests": {
                "required_fields": ["name", "test_type"],
                "field_types": {
                    "name": "string",
                    "test_type": "string",
                    "description": "string",
                    "standard": "string",
                    "method": "string",
                    "duration": "float",
                    "temperature": "float",
                    "pressure": "float"
                },
                "test_types": [
                    "pressure_test", "leak_test", "material_compatibility",
                    "temperature_test", "corrosion_test", "impact_test"
                ],
                "constraints": {
                    "duration": {"min": 0, "max": 10000},
                    "temperature": {"min": -200, "max": 1000},
                    "pressure": {"min": 0, "max": 10000}
                }
            },
            "assessments": {
                "required_fields": ["title", "substance_id", "risk_level"],
                "field_types": {
                    "title": "string",
                    "substance_id": "string",
                    "risk_level": "string",
                    "hazards": "string",
                    "mitigation": "string",
                    "ppe_required": "string",
                    "storage_requirements": "string",
                    "emergency_procedures": "string",
                    "assessor": "string",
                    "date": "date"
                },
                "risk_levels": ["low", "medium", "high", "critical"],
                "constraints": {}
            }
        }
    
    async def validate_csv_structure(self, df: pd.DataFrame, data_type: str) -> Dict[str, Any]:
        """Validate CSV structure and data types."""
        try:
            if data_type not in self.validation_rules:
                return {
                    "valid": False,
                    "errors": [f"Unknown data type: {data_type}"]
                }
            
            rules = self.validation_rules[data_type]
            errors = []
            warnings = []
            
            # Check required fields
            for field in rules["required_fields"]:
                if field not in df.columns:
                    errors.append(f"Missing required field: {field}")
            
            # Check field types and constraints
            for field, expected_type in rules["field_types"].items():
                if field in df.columns:
                    # Type validation
                    type_errors = self._validate_field_type(df[field], expected_type, field)
                    errors.extend(type_errors)
                    
                    # Constraint validation
                    if field in rules.get("constraints", {}):
                        constraint_errors = self._validate_constraints(
                            df[field], rules["constraints"][field], field
                        )
                        errors.extend(constraint_errors)
                    
                    # Value validation for specific fields
                    if field in rules:
                        value_errors = self._validate_field_values(
                            df[field], rules, field
                        )
                        errors.extend(value_errors)
            
            # Check for duplicate entries
            if "name" in df.columns:
                duplicates = df[df["name"].duplicated()]["name"].tolist()
                if duplicates:
                    warnings.append(f"Duplicate names found: {duplicates}")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "total_rows": len(df),
                "valid_rows": len(df) - len([e for e in errors if "row" in e])
            }
            
        except Exception as e:
            logger.error(f"Error validating CSV structure: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"]
            }
    
    def _validate_field_type(self, series: pd.Series, expected_type: str, field: str) -> List[str]:
        """Validate field data type."""
        errors = []
        
        if expected_type == "string":
            # Check if all values are strings
            non_strings = series[series.apply(lambda x: not isinstance(x, str) and pd.notna(x))]
            if len(non_strings) > 0:
                errors.append(f"Field '{field}' contains non-string values")
        
        elif expected_type == "float":
            # Check if all values can be converted to float
            try:
                pd.to_numeric(series, errors='coerce')
                invalid_floats = series[pd.to_numeric(series, errors='coerce').isna() & series.notna()]
                if len(invalid_floats) > 0:
                    errors.append(f"Field '{field}' contains non-numeric values")
            except:
                errors.append(f"Field '{field}' cannot be converted to numeric")
        
        elif expected_type == "string_or_float":
            # Check if values are either strings or floats
            invalid_values = series[
                series.apply(lambda x: not (isinstance(x, str) or isinstance(x, (int, float))) and pd.notna(x))
            ]
            if len(invalid_values) > 0:
                errors.append(f"Field '{field}' contains invalid values (must be string or number)")
        
        elif expected_type == "date":
            # Check if values can be parsed as dates
            try:
                pd.to_datetime(series, errors='coerce')
                invalid_dates = series[pd.to_datetime(series, errors='coerce').isna() & series.notna()]
                if len(invalid_dates) > 0:
                    errors.append(f"Field '{field}' contains invalid date values")
            except:
                errors.append(f"Field '{field}' cannot be converted to dates")
        
        return errors
    
    def _validate_constraints(self, series: pd.Series, constraints: Dict[str, Any], field: str) -> List[str]:
        """Validate field constraints."""
        errors = []
        
        try:
            numeric_series = pd.to_numeric(series, errors='coerce')
            
            if "min" in constraints:
                below_min = numeric_series[numeric_series < constraints["min"]]
                if len(below_min) > 0:
                    errors.append(f"Field '{field}' contains values below minimum {constraints['min']}")
            
            if "max" in constraints:
                above_max = numeric_series[numeric_series > constraints["max"]]
                if len(above_max) > 0:
                    errors.append(f"Field '{field}' contains values above maximum {constraints['max']}")
        
        except Exception as e:
            errors.append(f"Error validating constraints for field '{field}': {e}")
        
        return errors
    
    def _validate_field_values(self, series: pd.Series, rules: Dict[str, Any], field: str) -> List[str]:
        """Validate field values against allowed values."""
        errors = []
        
        if field == "hazard_class" and "hazard_classes" in rules:
            invalid_classes = series[~series.isin(rules["hazard_classes"]) & series.notna()]
            if len(invalid_classes) > 0:
                errors.append(f"Field '{field}' contains invalid hazard classes: {invalid_classes.unique().tolist()}")
        
        elif field == "material" and "materials" in rules:
            invalid_materials = series[~series.isin(rules["materials"]) & series.notna()]
            if len(invalid_materials) > 0:
                errors.append(f"Field '{field}' contains invalid materials: {invalid_materials.unique().tolist()}")
        
        elif field == "test_type" and "test_types" in rules:
            invalid_types = series[~series.isin(rules["test_types"]) & series.notna()]
            if len(invalid_types) > 0:
                errors.append(f"Field '{field}' contains invalid test types: {invalid_types.unique().tolist()}")
        
        elif field == "risk_level" and "risk_levels" in rules:
            invalid_levels = series[~series.isin(rules["risk_levels"]) & series.notna()]
            if len(invalid_levels) > 0:
                errors.append(f"Field '{field}' contains invalid risk levels: {invalid_levels.unique().tolist()}")
        
        return errors
    
    async def validate_safety_rules(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """Validate data against safety rules."""
        try:
            errors = []
            warnings = []
            
            if data_type == "substance":
                # Check for dangerous combinations
                if data.get("hazard_class") == "flammable" and data.get("flash_point", 0) < 23:
                    warnings.append("Highly flammable substance detected")
                
                if data.get("hazard_class") == "toxic" and data.get("molecular_weight", 0) < 100:
                    warnings.append("Low molecular weight toxic substance - handle with extreme care")
                
                if data.get("hazard_class") == "corrosive":
                    warnings.append("Corrosive substance - ensure proper PPE and containment")
            
            elif data_type == "container":
                # Check container compatibility
                if data.get("material") == "plastic" and data.get("pressure_rating", 0) > 100:
                    warnings.append("High pressure in plastic container - verify material compatibility")
                
                if data.get("temperature_rating", 0) < -50 or data.get("temperature_rating", 0) > 200:
                    warnings.append("Extreme temperature conditions - verify container specifications")
            
            elif data_type == "test":
                # Check test safety
                if data.get("pressure", 0) > 1000:
                    warnings.append("High pressure test - ensure proper safety measures")
                
                if data.get("temperature", 0) < -100 or data.get("temperature", 0) > 300:
                    warnings.append("Extreme temperature test - ensure proper safety measures")
            
            elif data_type == "assessment":
                # Check assessment completeness
                if data.get("risk_level") == "high" and not data.get("emergency_procedures"):
                    errors.append("High risk assessment missing emergency procedures")
                
                if data.get("risk_level") == "critical" and not data.get("ppe_required"):
                    errors.append("Critical risk assessment missing PPE requirements")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }
            
        except Exception as e:
            logger.error(f"Error validating safety rules: {e}")
            return {
                "valid": False,
                "errors": [f"Safety validation error: {str(e)}"]
            }
    
    async def validate_chemical_formula(self, formula: str) -> Dict[str, Any]:
        """Validate chemical formula format."""
        try:
            if not formula:
                return {"valid": False, "errors": ["Chemical formula cannot be empty"]}
            
            # Basic chemical formula pattern
            pattern = r'^[A-Z][a-z]?\d*([A-Z][a-z]?\d*)*$'
            
            if not re.match(pattern, formula):
                return {
                    "valid": False, 
                    "errors": ["Invalid chemical formula format"]
                }
            
            # Check for balanced parentheses (if any)
            if formula.count('(') != formula.count(')'):
                return {
                    "valid": False,
                    "errors": ["Unbalanced parentheses in chemical formula"]
                }
            
            return {"valid": True, "errors": []}
            
        except Exception as e:
            logger.error(f"Error validating chemical formula: {e}")
            return {
                "valid": False,
                "errors": [f"Formula validation error: {str(e)}"]
            }
    
    async def validate_compatibility(self, substance_data: Dict[str, Any], 
                                   container_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate substance-container compatibility."""
        try:
            errors = []
            warnings = []
            
            # Check material compatibility
            substance_hazard = substance_data.get("hazard_class", "")
            container_material = container_data.get("material", "")
            
            incompatibilities = {
                "corrosive": ["aluminum", "carbon_steel"],
                "oxidizing": ["plastic"],
                "flammable": ["plastic"]  # depending on flash point
            }
            
            if substance_hazard in incompatibilities:
                if container_material in incompatibilities[substance_hazard]:
                    errors.append(f"Incompatible: {substance_hazard} substance with {container_material} container")
            
            # Check temperature compatibility
            substance_boiling = substance_data.get("boiling_point", 0)
            container_temp_rating = container_data.get("temperature_rating", 0)
            
            if substance_boiling > container_temp_rating:
                warnings.append(f"Substance boiling point ({substance_boiling}°C) exceeds container rating ({container_temp_rating}°C)")
            
            # Check pressure compatibility
            container_pressure_rating = container_data.get("pressure_rating", 0)
            if container_pressure_rating < 1:  # atmospheric pressure
                warnings.append("Container pressure rating below atmospheric pressure")
            
            return {
                "compatible": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }
            
        except Exception as e:
            logger.error(f"Error validating compatibility: {e}")
            return {
                "compatible": False,
                "errors": [f"Compatibility validation error: {str(e)}"]
            }

# Global validation engine instance
validation_engine = ValidationEngine()

class ValidationRules:
    """Static validation rules for common validation tasks."""
    
    @staticmethod
    def is_valid_chemical_name(name: str) -> bool:
        """
        Validate chemical name format.
        
        Args:
            name (str): Chemical name to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not name or not isinstance(name, str):
            return False
        
        # Basic validation: should not be empty and should contain alphanumeric characters
        name = name.strip()
        if len(name) < 1:
            return False
        
        # Should contain at least one letter
        if not any(c.isalpha() for c in name):
            return False
        
        # Should not contain special characters except common chemical notation
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789()[]{}.,-_ ')
        if not all(c in allowed_chars for c in name):
            return False
        
        return True
    
    @staticmethod
    def is_valid_cas_number(cas_number: str) -> bool:
        """
        Validate CAS number format (XXX-XX-X).
        
        Args:
            cas_number (str): CAS number to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not cas_number or not isinstance(cas_number, str):
            return False
        
        # CAS number format: XXX-XX-X
        import re
        pattern = r'^\d{1,7}-\d{2}-\d$'
        return bool(re.match(pattern, cas_number))
    
    @staticmethod
    def is_valid_hazard_class(hazard_class: str) -> bool:
        """
        Validate hazard class.
        
        Args:
            hazard_class (str): Hazard class to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        valid_classes = [
            'flammable', 'toxic', 'corrosive', 'explosive', 
            'oxidizing', 'environmental', 'health', 'irritant',
            'sensitizer', 'carcinogen', 'mutagen', 'reproductive_toxin'
        ]
        return hazard_class.lower() in valid_classes
    
    @staticmethod
    def is_valid_molecular_weight(weight: float) -> bool:
        """
        Validate molecular weight.
        
        Args:
            weight (float): Molecular weight to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return isinstance(weight, (int, float)) and 0 < weight < 10000
    
    @staticmethod
    def is_valid_temperature(temp: float) -> bool:
        """
        Validate temperature value.
        
        Args:
            temp (float): Temperature to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return isinstance(temp, (int, float)) and -273 <= temp <= 5000
