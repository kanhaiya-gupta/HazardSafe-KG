# validation/utils.py
import logging
import re
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def normalize_string(value: str) -> str:
    """
    Normalize a string by stripping whitespace and converting to lowercase.
    
    Args:
        value (str): Input string.
    
    Returns:
        str: Normalized string.
    """
    return value.strip().lower() if value else ''

def log_validation_summary(report: dict):
    """
    Log a summary of validation results.
    
    Args:
        report (dict): Validation report with errors, warnings, and is_valid.
    """
    if report['is_valid']:
        logger.info("Validation passed successfully.")
    else:
        logger.error("Validation failed with errors:")
        for error in report['errors']:
            logger.error(f" - {error}")
    for warning in report['warnings']:
        logger.warning(f" - {warning}")

def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone (str): Phone number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not phone:
        return False
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (7-15 digits)
    return 7 <= len(digits_only) <= 15

def validate_date_format(date_str: str, format_str: str = "%Y-%m-%d") -> bool:
    """
    Validate date format.
    
    Args:
        date_str (str): Date string to validate
        format_str (str): Expected date format
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not date_str:
        return False
    
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False

def validate_numeric_range(value: Any, min_val: float, max_val: float) -> bool:
    """
    Validate if a value is within a numeric range.
    
    Args:
        value: Value to validate
        min_val (float): Minimum allowed value
        max_val (float): Maximum allowed value
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        num_value = float(value)
        return min_val <= num_value <= max_val
    except (ValueError, TypeError):
        return False

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    return filename

def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validate file extension.
    
    Args:
        filename (str): Filename to validate
        allowed_extensions (List[str]): List of allowed extensions (e.g., ['.csv', '.json'])
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not filename:
        return False
    
    # Get file extension
    if '.' not in filename:
        return False
    
    extension = filename.lower().split('.')[-1]
    return f'.{extension}' in [ext.lower() for ext in allowed_extensions]

def create_validation_report(errors: List[str], warnings: List[str], 
                           total_items: int = 0, valid_items: int = 0) -> Dict[str, Any]:
    """
    Create a standardized validation report.
    
    Args:
        errors (List[str]): List of error messages
        warnings (List[str]): List of warning messages
        total_items (int): Total number of items processed
        valid_items (int): Number of valid items
        
    Returns:
        Dict[str, Any]: Validation report
    """
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'total_items': total_items,
        'valid_items': valid_items,
        'error_count': len(errors),
        'warning_count': len(warnings),
        'success_rate': (valid_items / total_items * 100) if total_items > 0 else 0
    } 