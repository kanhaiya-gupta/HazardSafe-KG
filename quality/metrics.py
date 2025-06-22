"""
Quality Metrics Module

Provides comprehensive data quality assessment metrics for HazardSafe-KG.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class QualityMetrics:
    """Data quality metrics calculator for HazardSafe-KG."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize quality metrics with configuration."""
        self.config = config or self._default_config()
        self.metrics_history = []
        
    def _default_config(self) -> Dict:
        """Default configuration for quality metrics."""
        return {
            "completeness_threshold": 0.8,
            "accuracy_threshold": 0.9,
            "consistency_threshold": 0.85,
            "timeliness_threshold": 0.95,
            "uniqueness_threshold": 0.9
        }
    
    def calculate_completeness(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate data completeness metrics."""
        metrics = {}
        
        # Overall completeness
        total_cells = data.size
        non_null_cells = data.notna().sum().sum()
        metrics['overall_completeness'] = non_null_cells / total_cells if total_cells > 0 else 0
        
        # Column-wise completeness
        column_completeness = {}
        for col in data.columns:
            non_null_count = data[col].notna().sum()
            total_count = len(data)
            column_completeness[col] = non_null_count / total_count if total_count > 0 else 0
        
        metrics['column_completeness'] = column_completeness
        metrics['avg_column_completeness'] = np.mean(list(column_completeness.values()))
        
        return metrics
    
    def calculate_accuracy(self, data: pd.DataFrame, reference_data: Optional[pd.DataFrame] = None) -> Dict[str, float]:
        """Calculate data accuracy metrics."""
        metrics = {}
        
        if reference_data is not None and data.shape == reference_data.shape:
            # Compare with reference data
            accuracy_scores = []
            for col in data.columns:
                if col in reference_data.columns:
                    matches = (data[col] == reference_data[col]).sum()
                    total = len(data)
                    accuracy_scores.append(matches / total if total > 0 else 0)
            
            metrics['overall_accuracy'] = np.mean(accuracy_scores) if accuracy_scores else 0
        else:
            # Basic format validation
            format_accuracy = self._validate_data_formats(data)
            metrics['format_accuracy'] = format_accuracy
            metrics['overall_accuracy'] = format_accuracy
        
        return metrics
    
    def calculate_consistency(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate data consistency metrics."""
        metrics = {}
        
        # Data type consistency
        type_consistency = self._check_type_consistency(data)
        metrics['type_consistency'] = type_consistency
        
        # Value range consistency
        range_consistency = self._check_value_ranges(data)
        metrics['range_consistency'] = range_consistency
        
        # Overall consistency
        metrics['overall_consistency'] = (type_consistency + range_consistency) / 2
        
        return metrics
    
    def calculate_timeliness(self, data: pd.DataFrame, timestamp_col: Optional[str] = None) -> Dict[str, float]:
        """Calculate data timeliness metrics."""
        metrics = {}
        
        if timestamp_col and timestamp_col in data.columns:
            # Check if timestamps are recent
            current_time = datetime.now()
            timestamps = pd.to_datetime(data[timestamp_col], errors='coerce')
            valid_timestamps = timestamps.dropna()
            
            if len(valid_timestamps) > 0:
                # Calculate age of data
                ages = (current_time - valid_timestamps).dt.total_seconds() / 3600  # hours
                recent_threshold = 24  # 24 hours
                recent_data = (ages <= recent_threshold).sum()
                timeliness_score = recent_data / len(valid_timestamps)
                metrics['timeliness_score'] = timeliness_score
            else:
                metrics['timeliness_score'] = 0
        else:
            # Default timeliness score
            metrics['timeliness_score'] = 0.8
        
        return metrics
    
    def calculate_uniqueness(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate data uniqueness metrics."""
        metrics = {}
        
        # Overall uniqueness
        total_rows = len(data)
        unique_rows = data.drop_duplicates().shape[0]
        metrics['overall_uniqueness'] = unique_rows / total_rows if total_rows > 0 else 0
        
        # Column-wise uniqueness
        column_uniqueness = {}
        for col in data.columns:
            unique_values = data[col].nunique()
            total_values = len(data)
            column_uniqueness[col] = unique_values / total_values if total_values > 0 else 0
        
        metrics['column_uniqueness'] = column_uniqueness
        metrics['avg_column_uniqueness'] = np.mean(list(column_uniqueness.values()))
        
        return metrics
    
    def calculate_overall_quality_score(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Calculate comprehensive quality score for the dataset."""
        quality_metrics = {}
        
        # Calculate individual metrics
        quality_metrics['completeness'] = self.calculate_completeness(data)
        quality_metrics['accuracy'] = self.calculate_accuracy(data, kwargs.get('reference_data'))
        quality_metrics['consistency'] = self.calculate_consistency(data)
        quality_metrics['timeliness'] = self.calculate_timeliness(data, kwargs.get('timestamp_col'))
        quality_metrics['uniqueness'] = self.calculate_uniqueness(data)
        
        # Calculate weighted overall score
        weights = {
            'completeness': 0.25,
            'accuracy': 0.30,
            'consistency': 0.20,
            'timeliness': 0.15,
            'uniqueness': 0.10
        }
        
        overall_score = 0
        for metric_name, weight in weights.items():
            if metric_name in quality_metrics:
                if metric_name == 'completeness':
                    score = quality_metrics[metric_name]['overall_completeness']
                elif metric_name == 'accuracy':
                    score = quality_metrics[metric_name]['overall_accuracy']
                elif metric_name == 'consistency':
                    score = quality_metrics[metric_name]['overall_consistency']
                elif metric_name == 'timeliness':
                    score = quality_metrics[metric_name]['timeliness_score']
                elif metric_name == 'uniqueness':
                    score = quality_metrics[metric_name]['overall_uniqueness']
                else:
                    score = 0
                
                overall_score += score * weight
        
        quality_metrics['overall_score'] = overall_score
        quality_metrics['quality_grade'] = self._get_quality_grade(overall_score)
        quality_metrics['timestamp'] = datetime.now().isoformat()
        
        # Store in history
        self.metrics_history.append(quality_metrics)
        
        return quality_metrics
    
    def _validate_data_formats(self, data: pd.DataFrame) -> float:
        """Validate basic data formats."""
        format_errors = 0
        total_checks = 0
        
        for col in data.columns:
            if data[col].dtype == 'object':
                # Check for common format issues
                sample_values = data[col].dropna().head(100)
                for value in sample_values:
                    total_checks += 1
                    # Basic format validation (can be extended)
                    if isinstance(value, str) and len(value.strip()) == 0:
                        format_errors += 1
        
        return 1 - (format_errors / total_checks) if total_checks > 0 else 1.0
    
    def _check_type_consistency(self, data: pd.DataFrame) -> float:
        """Check data type consistency across columns."""
        type_errors = 0
        total_checks = 0
        
        for col in data.columns:
            if data[col].dtype == 'object':
                # Check for mixed types in object columns
                sample_values = data[col].dropna().head(100)
                if len(sample_values) > 0:
                    first_type = type(sample_values.iloc[0])
                    for value in sample_values:
                        total_checks += 1
                        if type(value) != first_type:
                            type_errors += 1
        
        return 1 - (type_errors / total_checks) if total_checks > 0 else 1.0
    
    def _check_value_ranges(self, data: pd.DataFrame) -> float:
        """Check value ranges for numeric columns."""
        range_errors = 0
        total_checks = 0
        
        for col in data.columns:
            if pd.api.types.is_numeric_dtype(data[col]):
                # Check for outliers (values beyond 3 standard deviations)
                values = data[col].dropna()
                if len(values) > 0:
                    mean_val = values.mean()
                    std_val = values.std()
                    if std_val > 0:
                        outliers = values[(values < mean_val - 3*std_val) | (values > mean_val + 3*std_val)]
                        range_errors += len(outliers)
                        total_checks += len(values)
        
        return 1 - (range_errors / total_checks) if total_checks > 0 else 1.0
    
    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade."""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"
    
    def get_metrics_history(self) -> List[Dict]:
        """Get historical quality metrics."""
        return self.metrics_history
    
    def export_metrics(self, filepath: str, metrics: Dict[str, Any]) -> None:
        """Export quality metrics to JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(metrics, f, indent=2, default=str)
            logger.info(f"Quality metrics exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}") 