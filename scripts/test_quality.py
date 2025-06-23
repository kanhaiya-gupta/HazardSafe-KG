#!/usr/bin/env python3
"""
Test script for Quality Metrics
Tests data quality assessment, metrics calculation, and report generation
"""

import asyncio
import argparse
import sys
import os
import logging
import json
import pandas as pd
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from quality.metrics import QualityMetrics
from quality.reports import QualityReporter
from quality.utils import QualityUtils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QualityTester:
    def __init__(self):
        self.metrics = QualityMetrics()
        self.reporter = QualityReporter()
        self.utils = QualityUtils()
        
    def create_sample_data(self):
        """Create sample datasets for testing"""
        logger.info("Creating sample datasets...")
        
        # High quality dataset
        high_quality_data = pd.DataFrame({
            'name': ['Sulfuric Acid', 'Sodium Hydroxide', 'Methanol', 'Ethanol', 'Acetone'],
            'formula': ['H2SO4', 'NaOH', 'CH3OH', 'C2H5OH', 'C3H6O'],
            'cas_number': ['7664-93-9', '1310-73-2', '67-56-1', '64-17-5', '67-64-1'],
            'hazard_class': ['corrosive', 'corrosive', 'flammable', 'flammable', 'flammable'],
            'molecular_weight': [98.08, 40.00, 32.04, 46.07, 58.08],
            'density': [1.84, 2.13, 0.792, 0.789, 0.784],
            'melting_point': [10.31, 318.0, -97.6, -114.1, -94.7],
            'boiling_point': [337.0, 1388.0, 64.7, 78.2, 56.1]
        })
        
        # Medium quality dataset (some missing values and errors)
        medium_quality_data = pd.DataFrame({
            'name': ['Sulfuric Acid', 'Sodium Hydroxide', 'Methanol', 'Ethanol', 'Acetone'],
            'formula': ['H2SO4', 'NaOH', 'CH3OH', 'C2H5OH', 'C3H6O'],
            'cas_number': ['7664-93-9', '1310-73-2', '67-56-1', '64-17-5', '67-64-1'],
            'hazard_class': ['corrosive', 'corrosive', 'flammable', 'flammable', 'flammable'],
            'molecular_weight': [98.08, 40.00, 32.04, 46.07, 58.08],
            'density': [1.84, 2.13, 0.792, 0.789, 0.784],
            'melting_point': [10.31, 318.0, -97.6, -114.1, -94.7],
            'boiling_point': [337.0, 1388.0, 64.7, 78.2, 56.1]
        })
        
        # Introduce some quality issues
        medium_quality_data.loc[1, 'cas_number'] = np.nan  # Missing value
        medium_quality_data.loc[2, 'molecular_weight'] = -10.0  # Invalid value
        medium_quality_data.loc[3, 'hazard_class'] = 'unknown_hazard'  # Invalid category
        
        # Low quality dataset (many issues)
        low_quality_data = pd.DataFrame({
            'name': ['Sulfuric Acid', 'Sodium Hydroxide', 'Methanol', 'Ethanol', 'Acetone'],
            'formula': ['H2SO4', 'NaOH', 'CH3OH', 'C2H5OH', 'C3H6O'],
            'cas_number': ['7664-93-9', 'invalid-cas', '67-56-1', '64-17-5', '67-64-1'],
            'hazard_class': ['corrosive', 'corrosive', 'flammable', 'flammable', 'flammable'],
            'molecular_weight': [98.08, 40.00, 32.04, 46.07, 58.08],
            'density': [1.84, 2.13, 0.792, 0.789, 0.784],
            'melting_point': [10.31, 318.0, -97.6, -114.1, -94.7],
            'boiling_point': [337.0, 1388.0, 64.7, 78.2, 56.1]
        })
        
        # Introduce many quality issues
        low_quality_data.loc[0, 'name'] = ''  # Empty value
        low_quality_data.loc[1, 'cas_number'] = 'invalid-cas'  # Invalid format
        low_quality_data.loc[2, 'molecular_weight'] = -50.0  # Negative value
        low_quality_data.loc[3, 'density'] = np.nan  # Missing value
        low_quality_data.loc[4, 'hazard_class'] = 'unknown_hazard'  # Invalid category
        
        return {
            'high_quality': high_quality_data,
            'medium_quality': medium_quality_data,
            'low_quality': low_quality_data
        }
    
    async def test_completeness_metrics(self):
        """Test completeness metrics calculation"""
        logger.info("Testing Completeness Metrics...")
        
        try:
            datasets = self.create_sample_data()
            results = {}
            
            for quality_level, data in datasets.items():
                # Calculate completeness metrics
                completeness_metrics = self.metrics.calculate_completeness_metrics(data)
                
                results[quality_level] = {
                    'overall_completeness': completeness_metrics['overall_completeness'],
                    'column_completeness': completeness_metrics['column_completeness'],
                    'missing_patterns': completeness_metrics['missing_patterns']
                }
                
                logger.info(f"{quality_level} dataset completeness: {completeness_metrics['overall_completeness']:.2%}")
            
            logger.info(f"✅ Completeness metrics testing completed")
            
            return {
                "success": True,
                "completeness_results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Completeness metrics error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_accuracy_metrics(self):
        """Test accuracy metrics calculation"""
        logger.info("Testing Accuracy Metrics...")
        
        try:
            datasets = self.create_sample_data()
            results = {}
            
            for quality_level, data in datasets.items():
                # Calculate accuracy metrics
                accuracy_metrics = self.metrics.calculate_accuracy_metrics(data)
                
                results[quality_level] = {
                    'format_accuracy': accuracy_metrics['format_accuracy'],
                    'reference_accuracy': accuracy_metrics['reference_accuracy'],
                    'range_accuracy': accuracy_metrics['range_accuracy'],
                    'overall_accuracy': accuracy_metrics['overall_accuracy']
                }
                
                logger.info(f"{quality_level} dataset accuracy: {accuracy_metrics['overall_accuracy']:.2%}")
            
            logger.info(f"✅ Accuracy metrics testing completed")
            
            return {
                "success": True,
                "accuracy_results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Accuracy metrics error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_consistency_metrics(self):
        """Test consistency metrics calculation"""
        logger.info("Testing Consistency Metrics...")
        
        try:
            datasets = self.create_sample_data()
            results = {}
            
            for quality_level, data in datasets.items():
                # Calculate consistency metrics
                consistency_metrics = self.metrics.calculate_consistency_metrics(data)
                
                results[quality_level] = {
                    'type_consistency': consistency_metrics['type_consistency'],
                    'value_consistency': consistency_metrics['value_consistency'],
                    'format_consistency': consistency_metrics['format_consistency'],
                    'overall_consistency': consistency_metrics['overall_consistency']
                }
                
                logger.info(f"{quality_level} dataset consistency: {consistency_metrics['overall_consistency']:.2%}")
            
            logger.info(f"✅ Consistency metrics testing completed")
            
            return {
                "success": True,
                "consistency_results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Consistency metrics error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_timeliness_metrics(self):
        """Test timeliness metrics calculation"""
        logger.info("Testing Timeliness Metrics...")
        
        try:
            # Create sample data with timestamps
            from datetime import datetime, timedelta
            
            # Create data with different timestamps
            base_date = datetime.now()
            timestamps = [
                base_date - timedelta(days=1),   # 1 day old
                base_date - timedelta(days=7),   # 1 week old
                base_date - timedelta(days=30),  # 1 month old
                base_date - timedelta(days=90),  # 3 months old
                base_date - timedelta(days=365)  # 1 year old
            ]
            
            timeliness_data = pd.DataFrame({
                'name': ['Substance 1', 'Substance 2', 'Substance 3', 'Substance 4', 'Substance 5'],
                'formula': ['H2SO4', 'NaOH', 'CH3OH', 'C2H5OH', 'C3H6O'],
                'last_updated': timestamps
            })
            
            # Calculate timeliness metrics
            timeliness_metrics = self.metrics.calculate_timeliness_metrics(timeliness_data, 'last_updated')
            
            logger.info(f"✅ Timeliness metrics testing completed")
            logger.info(f"Data age score: {timeliness_metrics['data_age_score']:.2%}")
            logger.info(f"Update frequency score: {timeliness_metrics['update_frequency_score']:.2%}")
            logger.info(f"Overall timeliness: {timeliness_metrics['overall_timeliness']:.2%}")
            
            return {
                "success": True,
                "timeliness_metrics": timeliness_metrics
            }
            
        except Exception as e:
            logger.error(f"❌ Timeliness metrics error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_uniqueness_metrics(self):
        """Test uniqueness metrics calculation"""
        logger.info("Testing Uniqueness Metrics...")
        
        try:
            datasets = self.create_sample_data()
            results = {}
            
            for quality_level, data in datasets.items():
                # Calculate uniqueness metrics
                uniqueness_metrics = self.metrics.calculate_uniqueness_metrics(data)
                
                results[quality_level] = {
                    'record_uniqueness': uniqueness_metrics['record_uniqueness'],
                    'column_uniqueness': uniqueness_metrics['column_uniqueness'],
                    'duplicate_analysis': uniqueness_metrics['duplicate_analysis'],
                    'overall_uniqueness': uniqueness_metrics['overall_uniqueness']
                }
                
                logger.info(f"{quality_level} dataset uniqueness: {uniqueness_metrics['overall_uniqueness']:.2%}")
            
            logger.info(f"✅ Uniqueness metrics testing completed")
            
            return {
                "success": True,
                "uniqueness_results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Uniqueness metrics error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_overall_quality_score(self):
        """Test overall quality score calculation"""
        logger.info("Testing Overall Quality Score...")
        
        try:
            datasets = self.create_sample_data()
            results = {}
            
            for quality_level, data in datasets.items():
                # Calculate overall quality score
                quality_score = self.metrics.calculate_overall_quality_score(data)
                
                results[quality_level] = {
                    'overall_score': quality_score['overall_score'],
                    'quality_grade': quality_score['quality_grade'],
                    'component_scores': quality_score['component_scores'],
                    'recommendations': quality_score['recommendations']
                }
                
                logger.info(f"{quality_level} dataset overall quality: {quality_score['overall_score']:.2%} ({quality_score['quality_grade']})")
            
            logger.info(f"✅ Overall quality score testing completed")
            
            return {
                "success": True,
                "overall_quality_results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Overall quality score error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_quality_report_generation(self):
        """Test quality report generation"""
        logger.info("Testing Quality Report Generation...")
        
        try:
            # Use high quality dataset for report generation
            datasets = self.create_sample_data()
            data = datasets['high_quality']
            
            # Calculate quality metrics
            quality_results = self.metrics.calculate_overall_quality_score(data)
            
            # Generate quality report
            report_path = self.reporter.generate_quality_report(quality_results, "test_substances_dataset")
            
            logger.info(f"✅ Quality report generation completed")
            logger.info(f"Report generated: {report_path}")
            
            return {
                "success": True,
                "report_path": report_path,
                "quality_results": quality_results
            }
            
        except Exception as e:
            logger.error(f"❌ Quality report generation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_quality_dashboard(self):
        """Test quality dashboard generation"""
        logger.info("Testing Quality Dashboard Generation...")
        
        try:
            # Create multiple datasets for dashboard
            datasets = self.create_sample_data()
            dashboard_data = {}
            
            for quality_level, data in datasets.items():
                quality_results = self.metrics.calculate_overall_quality_score(data)
                dashboard_data[quality_level] = quality_results
            
            # Generate dashboard
            dashboard_path = self.reporter.generate_quality_dashboard(dashboard_data, "test_dashboard")
            
            logger.info(f"✅ Quality dashboard generation completed")
            logger.info(f"Dashboard generated: {dashboard_path}")
            
            return {
                "success": True,
                "dashboard_path": dashboard_path,
                "dashboard_data": dashboard_data
            }
            
        except Exception as e:
            logger.error(f"❌ Quality dashboard generation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_quality_utils(self):
        """Test quality utility functions"""
        logger.info("Testing Quality Utilities...")
        
        try:
            # Test data validation utilities
            test_data = pd.DataFrame({
                'name': ['Test 1', 'Test 2', 'Test 3'],
                'value': [1, 2, 3],
                'category': ['A', 'B', 'A']
            })
            
            # Test data cleaning
            cleaned_data = self.utils.clean_data(test_data)
            
            # Test outlier detection
            outliers = self.utils.detect_outliers(test_data['value'])
            
            # Test data profiling
            profile = self.utils.profile_data(test_data)
            
            logger.info(f"✅ Quality utilities testing completed")
            logger.info(f"Data cleaned: {len(cleaned_data)} rows")
            logger.info(f"Outliers detected: {len(outliers)}")
            logger.info(f"Data profile generated: {len(profile)} metrics")
            
            return {
                "success": True,
                "cleaned_data_rows": len(cleaned_data),
                "outliers_count": len(outliers),
                "profile_metrics": len(profile)
            }
            
        except Exception as e:
            logger.error(f"❌ Quality utilities error: {e}")
            return {"success": False, "error": str(e)}

async def main():
    parser = argparse.ArgumentParser(description="Test Quality Metrics")
    parser.add_argument("--metric", choices=["completeness", "accuracy", "consistency", "timeliness", "uniqueness", "overall", "report", "dashboard", "utils", "all"], 
                       help="Test specific quality metric")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    tester = QualityTester()
    
    if args.metric == "completeness":
        result = await tester.test_completeness_metrics()
    elif args.metric == "accuracy":
        result = await tester.test_accuracy_metrics()
    elif args.metric == "consistency":
        result = await tester.test_consistency_metrics()
    elif args.metric == "timeliness":
        result = await tester.test_timeliness_metrics()
    elif args.metric == "uniqueness":
        result = await tester.test_uniqueness_metrics()
    elif args.metric == "overall":
        result = await tester.test_overall_quality_score()
    elif args.metric == "report":
        result = await tester.test_quality_report_generation()
    elif args.metric == "dashboard":
        result = await tester.test_quality_dashboard()
    elif args.metric == "utils":
        result = await tester.test_quality_utils()
    else:
        # Run all tests
        logger.info("Running all quality metrics tests...")
        
        results = {}
        results["completeness"] = await tester.test_completeness_metrics()
        results["accuracy"] = await tester.test_accuracy_metrics()
        results["consistency"] = await tester.test_consistency_metrics()
        results["timeliness"] = await tester.test_timeliness_metrics()
        results["uniqueness"] = await tester.test_uniqueness_metrics()
        results["overall"] = await tester.test_overall_quality_score()
        results["report"] = await tester.test_quality_report_generation()
        results["dashboard"] = await tester.test_quality_dashboard()
        results["utils"] = await tester.test_quality_utils()
        
        # Summary
        successful_tests = sum(1 for r in results.values() if r.get("success", False))
        total_tests = len(results)
        
        logger.info(f"\n{'='*50}")
        logger.info(f"QUALITY METRICS TEST SUMMARY")
        logger.info(f"{'='*50}")
        logger.info(f"Successful tests: {successful_tests}/{total_tests}")
        
        for test_name, result in results.items():
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            logger.info(f"{test_name.capitalize()}: {status}")
            if not result.get("success", False):
                logger.error(f"  Error: {result.get('error', 'Unknown error')}")
        
        return results
    
    return result

if __name__ == "__main__":
    asyncio.run(main()) 