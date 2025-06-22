"""
Quality Utilities Module

Helper functions and utilities for data quality assessment in HazardSafe-KG.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import re
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class QualityUtils:
    """Utility functions for data quality assessment."""
    
    @staticmethod
    def detect_data_types(data: pd.DataFrame) -> Dict[str, str]:
        """Detect and categorize data types for each column."""
        type_mapping = {}
        
        for col in data.columns:
            # Check for numeric columns
            if pd.api.types.is_numeric_dtype(data[col]):
                type_mapping[col] = 'numeric'
            # Check for datetime columns
            elif pd.api.types.is_datetime64_any_dtype(data[col]):
                type_mapping[col] = 'datetime'
            # Check for boolean columns
            elif pd.api.types.is_bool_dtype(data[col]):
                type_mapping[col] = 'boolean'
            # Check for categorical columns
            elif data[col].nunique() / len(data) < 0.1:  # Less than 10% unique values
                type_mapping[col] = 'categorical'
            # Check for text columns
            elif data[col].dtype == 'object':
                type_mapping[col] = 'text'
            else:
                type_mapping[col] = 'unknown'
        
        return type_mapping
    
    @staticmethod
    def identify_outliers(data: pd.DataFrame, method: str = 'iqr') -> Dict[str, List[int]]:
        """Identify outliers in numeric columns."""
        outliers = {}
        
        for col in data.columns:
            if pd.api.types.is_numeric_dtype(data[col]):
                values = data[col].dropna()
                if len(values) > 0:
                    if method == 'iqr':
                        Q1 = values.quantile(0.25)
                        Q3 = values.quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        outlier_indices = data[(data[col] < lower_bound) | (data[col] > upper_bound)].index.tolist()
                    elif method == 'zscore':
                        z_scores = np.abs((values - values.mean()) / values.std())
                        outlier_indices = data[z_scores > 3].index.tolist()
                    else:
                        outlier_indices = []
                    
                    outliers[col] = outlier_indices
        
        return outliers
    
    @staticmethod
    def check_data_patterns(data: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Check for common data patterns and anomalies."""
        patterns = {}
        
        for col in data.columns:
            col_patterns = {}
            values = data[col].dropna()
            
            if len(values) > 0:
                # Check for empty strings
                if data[col].dtype == 'object':
                    empty_strings = (data[col] == '').sum()
                    col_patterns['empty_strings'] = empty_strings
                
                # Check for whitespace-only strings
                if data[col].dtype == 'object':
                    whitespace_only = data[col].str.strip().eq('').sum()
                    col_patterns['whitespace_only'] = whitespace_only
                
                # Check for duplicate values
                duplicates = data[col].duplicated().sum()
                col_patterns['duplicates'] = duplicates
                
                # Check for case variations (for text columns)
                if data[col].dtype == 'object':
                    unique_values = values.unique()
                    case_variations = len(unique_values) - len(set(str(v).lower() for v in unique_values))
                    col_patterns['case_variations'] = case_variations
                
                # Check for leading/trailing spaces
                if data[col].dtype == 'object':
                    leading_spaces = data[col].str.startswith(' ').sum()
                    trailing_spaces = data[col].str.endswith(' ').sum()
                    col_patterns['leading_spaces'] = leading_spaces
                    col_patterns['trailing_spaces'] = trailing_spaces
            
            patterns[col] = col_patterns
        
        return patterns
    
    @staticmethod
    def validate_email_format(emails: pd.Series) -> Tuple[int, List[int]]:
        """Validate email format using regex."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        valid_count = 0
        invalid_indices = []
        
        for idx, email in enumerate(emails):
            if pd.notna(email) and isinstance(email, str):
                if re.match(email_pattern, email):
                    valid_count += 1
                else:
                    invalid_indices.append(idx)
            else:
                invalid_indices.append(idx)
        
        return valid_count, invalid_indices
    
    @staticmethod
    def validate_phone_format(phones: pd.Series) -> Tuple[int, List[int]]:
        """Validate phone number format."""
        phone_pattern = r'^[\+]?[1-9][\d]{0,15}$'
        valid_count = 0
        invalid_indices = []
        
        for idx, phone in enumerate(phones):
            if pd.notna(phone):
                # Remove common separators
                clean_phone = re.sub(r'[\s\-\(\)\.]', '', str(phone))
                if re.match(phone_pattern, clean_phone):
                    valid_count += 1
                else:
                    invalid_indices.append(idx)
            else:
                invalid_indices.append(idx)
        
        return valid_count, invalid_indices
    
    @staticmethod
    def check_date_consistency(dates: pd.Series) -> Dict[str, Any]:
        """Check date consistency and validity."""
        results = {
            'valid_dates': 0,
            'invalid_dates': 0,
            'future_dates': 0,
            'very_old_dates': 0,
            'date_range': None
        }
        
        valid_dates = []
        
        for date in dates:
            if pd.notna(date):
                try:
                    if isinstance(date, str):
                        parsed_date = pd.to_datetime(date)
                    else:
                        parsed_date = date
                    
                    valid_dates.append(parsed_date)
                    results['valid_dates'] += 1
                    
                    # Check for future dates
                    if parsed_date > datetime.now():
                        results['future_dates'] += 1
                    
                    # Check for very old dates (before 1900)
                    if parsed_date < datetime(1900, 1, 1):
                        results['very_old_dates'] += 1
                        
                except:
                    results['invalid_dates'] += 1
            else:
                results['invalid_dates'] += 1
        
        if valid_dates:
            results['date_range'] = {
                'min': min(valid_dates),
                'max': max(valid_dates)
            }
        
        return results
    
    @staticmethod
    def calculate_statistical_metrics(data: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Calculate statistical metrics for numeric columns."""
        stats = {}
        
        for col in data.columns:
            if pd.api.types.is_numeric_dtype(data[col]):
                values = data[col].dropna()
                if len(values) > 0:
                    col_stats = {
                        'count': len(values),
                        'mean': values.mean(),
                        'median': values.median(),
                        'std': values.std(),
                        'min': values.min(),
                        'max': values.max(),
                        'q25': values.quantile(0.25),
                        'q75': values.quantile(0.75),
                        'skewness': values.skew(),
                        'kurtosis': values.kurtosis()
                    }
                    stats[col] = col_stats
        
        return stats
    
    @staticmethod
    def detect_missing_patterns(data: pd.DataFrame) -> Dict[str, Any]:
        """Detect patterns in missing data."""
        missing_patterns = {
            'total_missing': data.isnull().sum().sum(),
            'missing_by_column': data.isnull().sum().to_dict(),
            'missing_percentage': (data.isnull().sum().sum() / data.size) * 100,
            'columns_with_missing': data.columns[data.isnull().any()].tolist(),
            'rows_with_missing': data[data.isnull().any(axis=1)].shape[0]
        }
        
        # Check for systematic missing patterns
        missing_matrix = data.isnull()
        missing_patterns['systematic_missing'] = {}
        
        for col1 in data.columns:
            for col2 in data.columns:
                if col1 != col2:
                    # Check if missing in col1 correlates with missing in col2
                    correlation = missing_matrix[col1].corr(missing_matrix[col2])
                    if abs(correlation) > 0.7:  # Strong correlation
                        missing_patterns['systematic_missing'][f'{col1}_vs_{col2}'] = correlation
        
        return missing_patterns
    
    @staticmethod
    def generate_quality_summary(data: pd.DataFrame) -> Dict[str, Any]:
        """Generate a comprehensive quality summary."""
        summary = {
            'dataset_info': {
                'rows': len(data),
                'columns': len(data.columns),
                'total_cells': data.size,
                'memory_usage': data.memory_usage(deep=True).sum()
            },
            'data_types': QualityUtils.detect_data_types(data),
            'missing_data': QualityUtils.detect_missing_patterns(data),
            'outliers': QualityUtils.identify_outliers(data),
            'patterns': QualityUtils.check_data_patterns(data),
            'statistics': QualityUtils.calculate_statistical_metrics(data)
        }
        
        return summary
    
    @staticmethod
    def create_quality_profile(data: pd.DataFrame, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Create a comprehensive quality profile for the dataset."""
        profile = {
            'timestamp': datetime.now().isoformat(),
            'summary': QualityUtils.generate_quality_summary(data),
            'recommendations': QualityUtils.generate_recommendations(data)
        }
        
        if output_file:
            import json
            with open(output_file, 'w') as f:
                json.dump(profile, f, indent=2, default=str)
            logger.info(f"Quality profile saved to {output_file}")
        
        return profile
    
    @staticmethod
    def generate_recommendations(data: pd.DataFrame) -> List[str]:
        """Generate data quality improvement recommendations."""
        recommendations = []
        
        # Check for missing data
        missing_percentage = (data.isnull().sum().sum() / data.size) * 100
        if missing_percentage > 10:
            recommendations.append(f"High missing data rate ({missing_percentage:.1f}%). Consider data imputation or collection.")
        
        # Check for duplicate rows
        duplicates = data.duplicated().sum()
        if duplicates > 0:
            recommendations.append(f"Found {duplicates} duplicate rows. Consider removing duplicates.")
        
        # Check for columns with high missing rates
        for col in data.columns:
            missing_rate = data[col].isnull().sum() / len(data)
            if missing_rate > 0.5:
                recommendations.append(f"Column '{col}' has {missing_rate:.1%} missing data. Consider dropping or imputing.")
        
        # Check for outliers
        outliers = QualityUtils.identify_outliers(data)
        total_outliers = sum(len(indices) for indices in outliers.values())
        if total_outliers > 0:
            recommendations.append(f"Found {total_outliers} outliers. Review for data quality issues.")
        
        # Check for data type inconsistencies
        type_mapping = QualityUtils.detect_data_types(data)
        if 'unknown' in type_mapping.values():
            recommendations.append("Some columns have unknown data types. Review and standardize data formats.")
        
        if not recommendations:
            recommendations.append("Data quality appears good. No immediate actions required.")
        
        return recommendations 