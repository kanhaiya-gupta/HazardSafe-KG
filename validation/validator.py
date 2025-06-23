# validation/validator.py

from abc import ABC, abstractmethod
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseValidator(ABC):
    """Base class for all validators in HazardSafe-KG."""
    
    def __init__(self, rules: Dict[str, Any):
        """
        Initialize validator with a set of rules.
        
        Args:
            rules (dict): Validation rules (e.g., required fields, formats).
        """
        self.rules = rules
        self.errors = []
        self.warnings = []
    
    @abstractmethod
    def validate(self, data: Any) -> bool:
        """
        Validate the input data.
        
        Args:
            data: Data to validate (e.g., list of dicts for CSV, dict for JSON).
        
        Returns:
            bool: True if valid, False otherwise.
        """
        pass
    
    def add_error(self, message: str):
        """Log and store an error message."""
        logger.error(message)
        self.errors.append(message)
    
    def add_warning(self, message: str):
        """Log and store a warning message."""
        logger.warning(message)
        self.warnings.append(message)
    
    def get_report(self) -> Dict[str, List[str]]:
        """Return validation report with errors and warnings."""
        return {
            'errors': self.errors,
            'warnings': self.warnings,
            'is_valid': len(self.errors) == 0
        }