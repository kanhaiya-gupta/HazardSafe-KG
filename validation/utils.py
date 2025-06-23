# validation/utils.py
import logging
from typing import Any

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
    logger = logging.getLogger(__name__)
    if report['is_valid']:
        logger.info("Validation passed successfully.")
    else:
        logger.error("Validation failed with errors:")
        for error in report['errors']:
            logger.error(f" - {error}")
    for warning in report['warnings']:
        logger.warning(f" - {warning}")