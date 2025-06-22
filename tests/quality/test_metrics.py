"""
Test Quality Metrics Module

Tests for data quality assessment functionality.
"""

import pytest
import pandas as pd
import numpy as np
from quality.metrics import QualityMetrics


class TestQualityMetrics:
    """Test cases for QualityMetrics class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.metrics = QualityMetrics()
        
        # Create sample data for testing
        self.sample_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
            'age': [25, 30, 35, None, 40],
            'email': ['alice@test.com', 'bob@test.com', 'invalid-email', 'diana@test.com', 'eve@test.com'],
            'score': [85.5, 92.0, 78.5, 88.0, 95.5]
        })
    
    def test_calculate_completeness(self):
        """Test completeness calculation."""
        completeness = self.metrics.calculate_completeness(self.sample_data)
        
        assert 'overall_completeness' in completeness
        assert 'column_completeness' in completeness
        assert 'avg_column_completeness' in completeness
        
        # Should be less than 100% due to missing age value
        assert completeness['overall_completeness'] < 1.0
        assert completeness['overall_completeness'] > 0.8
    
    def test_calculate_accuracy(self):
        """Test accuracy calculation."""
        accuracy = self.metrics.calculate_accuracy(self.sample_data)
        
        assert 'overall_accuracy' in accuracy
        assert accuracy['overall_accuracy'] >= 0
    
    def test_calculate_consistency(self):
        """Test consistency calculation."""
        consistency = self.metrics.calculate_consistency(self.sample_data)
        
        assert 'overall_consistency' in consistency
        assert consistency['overall_consistency'] >= 0
        assert consistency['overall_consistency'] <= 1
    
    def test_calculate_uniqueness(self):
        """Test uniqueness calculation."""
        uniqueness = self.metrics.calculate_uniqueness(self.sample_data)
        
        assert 'overall_uniqueness' in uniqueness
        assert uniqueness['overall_uniqueness'] >= 0
        assert uniqueness['overall_uniqueness'] <= 1
    
    def test_calculate_overall_quality_score(self):
        """Test overall quality score calculation."""
        quality_results = self.metrics.calculate_overall_quality_score(self.sample_data)
        
        assert 'overall_score' in quality_results
        assert 'quality_grade' in quality_results
        assert 'timestamp' in quality_results
        
        assert quality_results['overall_score'] >= 0
        assert quality_results['overall_score'] <= 1
        assert quality_results['quality_grade'] in ['A', 'B', 'C', 'D', 'F']
    
    def test_quality_grade_assignment(self):
        """Test quality grade assignment logic."""
        # Test grade A
        self.metrics.config['completeness_threshold'] = 0.5
        quality_results = self.metrics.calculate_overall_quality_score(self.sample_data)
        assert quality_results['quality_grade'] in ['A', 'B', 'C', 'D', 'F']
    
    def test_metrics_history(self):
        """Test metrics history tracking."""
        # Calculate metrics multiple times
        self.metrics.calculate_overall_quality_score(self.sample_data)
        self.metrics.calculate_overall_quality_score(self.sample_data)
        
        history = self.metrics.get_metrics_history()
        assert len(history) == 2
        assert all('timestamp' in metric for metric in history)
    
    def test_empty_dataframe(self):
        """Test handling of empty dataframe."""
        empty_df = pd.DataFrame()
        quality_results = self.metrics.calculate_overall_quality_score(empty_df)
        
        assert 'overall_score' in quality_results
        assert quality_results['overall_score'] == 0
    
    def test_dataframe_with_all_null(self):
        """Test handling of dataframe with all null values."""
        null_df = pd.DataFrame({
            'col1': [None, None, None],
            'col2': [None, None, None]
        })
        
        completeness = self.metrics.calculate_completeness(null_df)
        assert completeness['overall_completeness'] == 0


if __name__ == "__main__":
    pytest.main([__file__]) 