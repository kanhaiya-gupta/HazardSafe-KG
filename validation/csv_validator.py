# validation/csv_validator.py
import csv
from typing import List, Dict, Any
from .validator import BaseValidator
from .rules import ValidationRules

class CSVValidator(BaseValidator):
    """Validator for CSV files in HazardSafe-KG."""
    
    def __init__(self, rules: Dict[str, Any]):
        super().__init__(rules)
    
    def validate(self, file_path: str) -> bool:
        """
        Validate a CSV file.
        
        Args:
            file_path (str): Path to the CSV file.
        
        Returns:
            bool: True if valid, False otherwise.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Check required columns
                required_columns = self.rules.get('required_columns', [])
                if not all(col in reader.fieldnames for col in required_columns):
                    missing = [col for col in required_columns if col not in reader.fieldnames]
                    self.add_error(f"Missing required columns: {missing}")
                    return False
                
                # Validate each row
                for row_num, row in enumerate(reader, start=1):
                    self._validate_row(row, row_num)
                
                return len(self.errors) == 0
        
        except Exception as e:
            self.add_error(f"Failed to read CSV file: {str(e)}")
            return False
    
    def _validate_row(self, row: Dict[str, str], row_num: int):
        """Validate a single CSV row."""
        # Check for missing values in required fields
        for field in self.rules.get('required_columns', []):
            if not row.get(field):
                self.add_error(f"Row {row_num}: Missing value for {field}")
        
        # Validate chemical name format (example rule)
        chemical_name = row.get('Chemical_Name', '')
        if chemical_name and not ValidationRules.is_valid_chemical_name(chemical_name):
            self.add_warning(f"Row {row_num}: Invalid chemical name format: {chemical_name}")
        
        # Validate hazard class (example rule)
        hazard_class = row.get('Hazard_Class', '')
        if hazard_class and hazard_class not in self.rules.get('valid_hazard_classes', []):
            self.add_error(f"Row {row_num}: Invalid hazard class: {hazard_class}")