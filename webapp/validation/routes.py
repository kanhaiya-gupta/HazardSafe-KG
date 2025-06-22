"""
Validation routes for HazardSafe-KG platform.
"""

from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import io
import json
from typing import Dict, Any, Optional
import logging

from validation.rules import ValidationEngine

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/validation", tags=["validation"])

# Setup templates
templates = Jinja2Templates(directory="webapp/templates")

# Initialize validation engine
validation_engine = ValidationEngine()

@router.get("/", response_class=HTMLResponse)
async def validation_dashboard(request: Request):
    """Validation dashboard page."""
    return templates.TemplateResponse("validation/index.html", {"request": request})

@router.get("/stats")
async def get_validation_stats():
    """Get validation engine statistics."""
    try:
        return {
            "validation_rules": len(validation_engine.validation_rules),
            "data_types": list(validation_engine.validation_rules.keys()),
            "total_rules": sum(len(rules.get("constraints", {})) for rules in validation_engine.validation_rules.values()),
            "status": "active"
        }
    except Exception as e:
        logger.error(f"Error getting validation stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get validation statistics")

@router.post("/validate-csv")
async def validate_csv_file(
    file: UploadFile = File(...),
    data_type: str = Form(...)
):
    """Validate uploaded CSV file."""
    try:
        # Read CSV file
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        # Validate structure
        result = await validation_engine.validate_csv_structure(df, data_type)
        
        return {
            "filename": file.filename,
            "data_type": data_type,
            "validation_result": result
        }
        
    except Exception as e:
        logger.error(f"Error validating CSV file: {e}")
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@router.post("/validate-data")
async def validate_data(data: Dict[str, Any], data_type: str):
    """Validate data object."""
    try:
        # Validate safety rules
        result = await validation_engine.validate_safety_rules(data, data_type)
        
        return {
            "data_type": data_type,
            "validation_result": result
        }
        
    except Exception as e:
        logger.error(f"Error validating data: {e}")
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

@router.post("/validate-compatibility")
async def validate_compatibility(
    substance_data: Dict[str, Any],
    container_data: Dict[str, Any]
):
    """Validate substance-container compatibility."""
    try:
        result = await validation_engine.validate_compatibility(substance_data, container_data)
        
        return {
            "validation_result": result
        }
        
    except Exception as e:
        logger.error(f"Error validating compatibility: {e}")
        raise HTTPException(status_code=500, detail=f"Compatibility validation error: {str(e)}")

@router.post("/validate-formula")
async def validate_chemical_formula(formula: str):
    """Validate chemical formula."""
    try:
        result = await validation_engine.validate_chemical_formula(formula)
        
        return {
            "formula": formula,
            "validation_result": result
        }
        
    except Exception as e:
        logger.error(f"Error validating chemical formula: {e}")
        raise HTTPException(status_code=500, detail=f"Formula validation error: {str(e)}")

@router.get("/rules")
async def get_validation_rules():
    """Get all validation rules."""
    try:
        return {
            "validation_rules": validation_engine.validation_rules
        }
    except Exception as e:
        logger.error(f"Error getting validation rules: {e}")
        raise HTTPException(status_code=500, detail="Failed to get validation rules")

@router.get("/rules/{data_type}")
async def get_validation_rules_by_type(data_type: str):
    """Get validation rules for specific data type."""
    try:
        if data_type not in validation_engine.validation_rules:
            raise HTTPException(status_code=404, detail=f"Data type '{data_type}' not found")
        
        return {
            "data_type": data_type,
            "rules": validation_engine.validation_rules[data_type]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting validation rules for {data_type}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get validation rules") 