"""
Quality Routes for HazardSafe-KG Web Application

Provides API endpoints for data quality assessment and report generation.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import os
import json
from datetime import datetime
from pathlib import Path
import logging
from typing import Optional

# Import quality modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from quality.metrics import QualityMetrics
from quality.reports import QualityReporter
from quality.utils import QualityUtils

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quality", tags=["quality"])

# Setup templates
templates = Jinja2Templates(directory="webapp/templates")

# Initialize quality components
quality_metrics = QualityMetrics()
quality_reporter = QualityReporter()


@router.get("/", response_class=HTMLResponse)
async def quality_index(request: Request):
    """Quality assessment dashboard."""
    return templates.TemplateResponse("quality/index.html", {"request": request})


@router.post("/assess")
async def assess_quality(
    file: UploadFile = File(...),
    dataset_name: Optional[str] = Form(None),
    include_reference: bool = Form(False)
):
    """Assess data quality for uploaded dataset."""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        # Read the uploaded file
        if file.filename.endswith('.csv'):
            data = pd.read_csv(file.file)
        elif file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            data = pd.read_excel(file.file)
        elif file.filename.endswith('.json'):
            data = pd.read_json(file.file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Use provided dataset name or filename
        dataset_name = dataset_name or file.filename
        
        # Perform quality assessment
        quality_results = quality_metrics.calculate_overall_quality_score(
            data, 
            dataset_name=dataset_name
        )
        
        # Generate quality profile
        quality_profile = QualityUtils.create_quality_profile(data)
        
        # Generate report
        report_path = quality_reporter.generate_quality_report(
            quality_results, 
            dataset_name
        )
        
        # Generate dashboard
        dashboard_path = quality_reporter.generate_dashboard(
            quality_metrics.get_metrics_history(),
            dataset_name
        )
        
        return {
            'success': True,
            'quality_results': quality_results,
            'quality_profile': quality_profile,
            'report_path': report_path,
            'dashboard_path': dashboard_path,
            'dataset_info': {
                'name': dataset_name,
                'rows': len(data),
                'columns': len(data.columns),
                'shape': data.shape
            }
        }
        
    except Exception as e:
        logger.error(f"Quality assessment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_quality_metrics():
    """Get historical quality metrics."""
    try:
        metrics_history = quality_metrics.get_metrics_history()
        return {
            'success': True,
            'metrics_history': metrics_history
        }
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports")
async def list_reports():
    """List available quality reports."""
    try:
        reports_dir = Path("webapp/static/reports/quality")
        reports = []
        
        if reports_dir.exists():
            # List metrics reports
            metrics_dir = reports_dir / "metrics"
            if metrics_dir.exists():
                for file in metrics_dir.glob("*.html"):
                    reports.append({
                        'name': file.name,
                        'type': 'metrics',
                        'path': f'/static/reports/quality/metrics/{file.name}',
                        'created': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                    })
            
            # List dashboard reports
            dashboard_dir = reports_dir / "dashboards"
            if dashboard_dir.exists():
                for file in dashboard_dir.glob("*.html"):
                    reports.append({
                        'name': file.name,
                        'type': 'dashboard',
                        'path': f'/static/reports/quality/dashboards/{file.name}',
                        'created': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                    })
        
        return {
            'success': True,
            'reports': reports
        }
    except Exception as e:
        logger.error(f"Failed to list reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/{filename:path}")
async def view_report(filename: str):
    """View a specific quality report."""
    try:
        report_path = Path("webapp/static/reports/quality") / filename
        if report_path.exists():
            return FileResponse(report_path, media_type='text/html')
        else:
            raise HTTPException(status_code=404, detail="Report not found")
    except Exception as e:
        logger.error(f"Failed to view report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_quality_config():
    """Get quality configuration."""
    try:
        config_path = Path("data/quality/config/quality_config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            return {
                'success': True,
                'config': config
            }
        else:
            raise HTTPException(status_code=404, detail="Configuration not found")
    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config")
async def update_quality_config(config_data: dict):
    """Update quality configuration."""
    try:
        config_path = Path("data/quality/config/quality_config.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        return {
            'success': True,
            'message': 'Configuration updated successfully'
        }
    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profile")
async def generate_quality_profile(file: UploadFile = File(...)):
    """Generate quality profile for dataset."""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        # Read the uploaded file
        if file.filename.endswith('.csv'):
            data = pd.read_csv(file.file)
        elif file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            data = pd.read_excel(file.file)
        elif file.filename.endswith('.json'):
            data = pd.read_json(file.file)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Generate quality profile
        profile = QualityUtils.create_quality_profile(data)
        
        return {
            'success': True,
            'profile': profile
        }
        
    except Exception as e:
        logger.error(f"Failed to generate profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard", response_class=HTMLResponse)
async def quality_dashboard(request: Request):
    """Quality dashboard page."""
    return templates.TemplateResponse("quality/dashboard.html", {"request": request}) 