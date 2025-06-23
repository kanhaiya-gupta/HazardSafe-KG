# validation/compatibility.py
from typing import List, Tuple
from .validator import BaseValidator

class CompatibilityValidator(BaseValidator):
    """Validator for chemical compatibility in HazardSafe-KG."""
    
    def __init__(self, compatibility_rules: List[Tuple[str, str, str]]):
        """
        Initialize with compatibility rules.
        
        Args:
            compatibility_rules (list): List of (chemical1, chemical2, status) tuples.
            Status can be 'compatible' or 'incompatible'.
        """
        super().__init__(rules={})
        self.compatibility_rules = {(rule[0], rule[1]): rule[2] for rule in compatibility_rules}
    
    def validate(self, chemicals: List[str]) -> bool:
        """
        Validate compatibility among a list of chemicals.
        
        Args:
            chemicals (list): List of chemical names.
        
        Returns:
            bool: True if all pairs are compatible, False otherwise.
        """
        for i, chem1 in enumerate(chemicals):
            for chem2 in chemicals[i + 1:]:
                pair = tuple(sorted([chem1, chem2]))
                status = self.compatibility_rules.get(pair, 'unknown')
                if status == 'incompatible':
                    self.add_error(f"Incompatible chemicals: {chem1} and {chem2}")
                elif status == 'unknown':
                    self.add_warning(f"Unknown compatibility: {chem1} and {chem2}")
        
        return len(self.errors) == 0

# Example usage
if __name__ == "__main__":
    rules = [
        ('H2SO4', 'NaOH', 'incompatible'),
        ('H2SO4', 'HCl', 'compatible'),
        ('Toluene', 'Acetone', 'compatible')
    ]
    validator = CompatibilityValidator(rules)
    result = validator.validate(['H2SO4', 'NaOH', 'Toluene'])
    print(validator.get_report())