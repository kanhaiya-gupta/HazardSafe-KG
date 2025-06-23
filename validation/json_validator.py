# validation/json_validator.py
import json
from typing import Dict, Any
from .validator import BaseValidator
from .rules import ValidationRules

class JSONValidator(BaseValidator):
    """Validator for JSON files in HazardSafe-KG."""
    
    def __init__(self, rules: Dict[str, Any]):
        super().__init__(rules)
    
    def validate(self, file_path: str) -> bool:
        """
        Validate a JSON file.
        
        Args:
            file_path (str): Path to the JSON file.
        
        Returns:
            bool: True if valid, False otherwise.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                # Check if data is a list or single object
                if isinstance(data, list):
                    for idx, item in enumerate(data, start=1):
                        self._validate_item(item, idx)
                else:
                    self._validate_item(data, 1)
                
                return len(self.errors) == 0
        
        except json.JSONDecodeError as e:
            self.add_error(f"Invalid JSON format: {str(e)}")
            return False
        except Exception as e:
            self.add_error(f"Failed to read JSON file: {str(e)}")
            return False
    
    def _validate_item(self, item: Dict[str, Any], item_num: int):
        """Validate a single JSON item."""
        # Check required fields
        required_fields = self.rules.get('required_fields', [])
        for field in required_fields:
            if field not in item or item[field] is None:
                self.add_error(f"Item {item_num}: Missing or null value for {field}")
        
        # Validate chemical name format
        chemical_name = item.get('chemical', '')
        if chemical_name and not ValidationRules.is_valid_chemical_name(chemical_name):
            self.add_warning(f"Item {item_num}: Invalid chemical name format: {chemical_name}")
        
        # Validate hazard class
        hazard_class = item.get('hazard_class', '')
        if hazard_class and hazard_class not in self.rules.get('valid_hazard_classes', []):
            self.add_error(f"Item {item_num}: Invalid hazard class: {hazard_class}")