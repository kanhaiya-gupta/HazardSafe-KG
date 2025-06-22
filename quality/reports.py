"""
Quality Reports Module

Generates comprehensive quality reports and visualizations for HazardSafe-KG.
"""

import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class QualityReporter:
    """Generates quality reports and visualizations."""
    
    def __init__(self, output_dir: str = "webapp/static/reports/quality"):
        """Initialize reporter with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "metrics").mkdir(exist_ok=True)
        (self.output_dir / "dashboards").mkdir(exist_ok=True)
        (self.output_dir / "templates").mkdir(exist_ok=True)
    
    def generate_quality_report(self, metrics: Dict[str, Any], dataset_name: str = "dataset") -> str:
        """Generate comprehensive HTML quality report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quality_report_{dataset_name}_{timestamp}.html"
        filepath = self.output_dir / "metrics" / filename
        
        html_content = self._create_html_report(metrics, dataset_name)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"Quality report generated: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return ""
    
    def generate_dashboard(self, metrics_history: List[Dict], dataset_name: str = "dataset") -> str:
        """Generate interactive quality dashboard."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quality_dashboard_{dataset_name}_{timestamp}.html"
        filepath = self.output_dir / "dashboards" / filename
        
        html_content = self._create_dashboard_html(metrics_history, dataset_name)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"Quality dashboard generated: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to generate dashboard: {e}")
            return ""
    
    def _create_html_report(self, metrics: Dict[str, Any], dataset_name: str) -> str:
        """Create HTML content for quality report."""
        overall_score = metrics.get('overall_score', 0)
        quality_grade = metrics.get('quality_grade', 'N/A')
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quality Report - {dataset_name}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .quality-score {{
            font-size: 3rem;
            font-weight: bold;
        }}
        .grade-a {{ color: #28a745; }}
        .grade-b {{ color: #17a2b8; }}
        .grade-c {{ color: #ffc107; }}
        .grade-d {{ color: #fd7e14; }}
        .grade-f {{ color: #dc3545; }}
        .metric-card {{
            border-left: 4px solid #007bff;
            margin-bottom: 1rem;
        }}
        .progress {{
            height: 25px;
        }}
    </style>
</head>
<body>
    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-12">
                <h1 class="text-center mb-4">Data Quality Report</h1>
                <div class="card">
                    <div class="card-header">
                        <h3>Dataset: {dataset_name}</h3>
                        <p class="text-muted">Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6 text-center">
                                <div class="quality-score grade-{quality_grade.lower()}">
                                    {overall_score:.1%}
                                </div>
                                <h4>Overall Quality Score</h4>
                            </div>
                            <div class="col-md-6 text-center">
                                <div class="quality-score grade-{quality_grade.lower()}">
                                    {quality_grade}
                                </div>
                                <h4>Quality Grade</h4>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h4>Quality Metrics Breakdown</h4>
                    </div>
                    <div class="card-body">
                        {self._generate_metrics_breakdown(metrics)}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Quality Metrics Chart</h5>
                    </div>
                    <div class="card-body">
                        <canvas id="qualityChart" width="400" height="200"></canvas>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Recommendations</h5>
                    </div>
                    <div class="card-body">
                        {self._generate_recommendations(metrics)}
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        {self._generate_chart_script(metrics)}
    </script>
</body>
</html>
        """
        return html
    
    def _generate_metrics_breakdown(self, metrics: Dict[str, Any]) -> str:
        """Generate HTML for metrics breakdown."""
        breakdown_html = ""
        
        metric_names = {
            'completeness': 'Completeness',
            'accuracy': 'Accuracy', 
            'consistency': 'Consistency',
            'timeliness': 'Timeliness',
            'uniqueness': 'Uniqueness'
        }
        
        for metric_key, metric_name in metric_names.items():
            if metric_key in metrics:
                metric_data = metrics[metric_key]
                if isinstance(metric_data, dict):
                    if 'overall_completeness' in metric_data:
                        score = metric_data['overall_completeness']
                    elif 'overall_accuracy' in metric_data:
                        score = metric_data['overall_accuracy']
                    elif 'overall_consistency' in metric_data:
                        score = metric_data['overall_consistency']
                    elif 'timeliness_score' in metric_data:
                        score = metric_data['timeliness_score']
                    elif 'overall_uniqueness' in metric_data:
                        score = metric_data['overall_uniqueness']
                    else:
                        score = 0
                else:
                    score = metric_data
                
                breakdown_html += f"""
                <div class="metric-card card">
                    <div class="card-body">
                        <h6 class="card-title">{metric_name}</h6>
                        <div class="progress">
                            <div class="progress-bar" role="progressbar" 
                                 style="width: {score:.1%}" 
                                 aria-valuenow="{score:.1%}" 
                                 aria-valuemin="0" 
                                 aria-valuemax="100">
                                {score:.1%}
                            </div>
                        </div>
                    </div>
                </div>
                """
        
        return breakdown_html
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> str:
        """Generate recommendations based on quality metrics."""
        recommendations = []
        
        # Completeness recommendations
        if 'completeness' in metrics:
            completeness = metrics['completeness'].get('overall_completeness', 0)
            if completeness < 0.8:
                recommendations.append("Improve data completeness by filling missing values")
        
        # Accuracy recommendations
        if 'accuracy' in metrics:
            accuracy = metrics['accuracy'].get('overall_accuracy', 0)
            if accuracy < 0.9:
                recommendations.append("Verify data accuracy and correct erroneous values")
        
        # Consistency recommendations
        if 'consistency' in metrics:
            consistency = metrics['consistency'].get('overall_consistency', 0)
            if consistency < 0.85:
                recommendations.append("Standardize data formats and ensure consistency")
        
        # Timeliness recommendations
        if 'timeliness' in metrics:
            timeliness = metrics['timeliness'].get('timeliness_score', 0)
            if timeliness < 0.95:
                recommendations.append("Update data more frequently to improve timeliness")
        
        # Uniqueness recommendations
        if 'uniqueness' in metrics:
            uniqueness = metrics['uniqueness'].get('overall_uniqueness', 0)
            if uniqueness < 0.9:
                recommendations.append("Remove duplicate records to improve uniqueness")
        
        if not recommendations:
            recommendations.append("Data quality is excellent! No immediate actions required.")
        
        recommendations_html = "<ul class='list-group list-group-flush'>"
        for rec in recommendations:
            recommendations_html += f"<li class='list-group-item'>{rec}</li>"
        recommendations_html += "</ul>"
        
        return recommendations_html
    
    def _generate_chart_script(self, metrics: Dict[str, Any]) -> str:
        """Generate JavaScript for Chart.js visualization."""
        labels = []
        data = []
        colors = ['#007bff', '#28a745', '#ffc107', '#17a2b8', '#6f42c1']
        
        metric_mapping = {
            'completeness': 'Completeness',
            'accuracy': 'Accuracy',
            'consistency': 'Consistency', 
            'timeliness': 'Timeliness',
            'uniqueness': 'Uniqueness'
        }
        
        for i, (key, label) in enumerate(metric_mapping.items()):
            if key in metrics:
                labels.append(label)
                metric_data = metrics[key]
                if isinstance(metric_data, dict):
                    if 'overall_completeness' in metric_data:
                        score = metric_data['overall_completeness']
                    elif 'overall_accuracy' in metric_data:
                        score = metric_data['overall_accuracy']
                    elif 'overall_consistency' in metric_data:
                        score = metric_data['overall_consistency']
                    elif 'timeliness_score' in metric_data:
                        score = metric_data['timeliness_score']
                    elif 'overall_uniqueness' in metric_data:
                        score = metric_data['overall_uniqueness']
                    else:
                        score = 0
                else:
                    score = metric_data
                data.append(score * 100)
        
        return f"""
        const ctx = document.getElementById('qualityChart').getContext('2d');
        new Chart(ctx, {{
            type: 'radar',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{{
                    label: 'Quality Score (%)',
                    data: {json.dumps(data)},
                    backgroundColor: 'rgba(0, 123, 255, 0.2)',
                    borderColor: 'rgba(0, 123, 255, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(0, 123, 255, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(0, 123, 255, 1)'
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    r: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            stepSize: 20
                        }}
                    }}
                }}
            }}
        }});
        """
    
    def _create_dashboard_html(self, metrics_history: List[Dict], dataset_name: str) -> str:
        """Create HTML content for quality dashboard."""
        if not metrics_history:
            return self._create_empty_dashboard_html(dataset_name)
        
        # Prepare data for charts
        timestamps = []
        overall_scores = []
        completeness_scores = []
        accuracy_scores = []
        consistency_scores = []
        
        for metric in metrics_history:
            timestamp = metric.get('timestamp', '')
            if timestamp:
                timestamps.append(datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M'))
            
            overall_scores.append(metric.get('overall_score', 0) * 100)
            
            if 'completeness' in metric:
                completeness_scores.append(metric['completeness'].get('overall_completeness', 0) * 100)
            if 'accuracy' in metric:
                accuracy_scores.append(metric['accuracy'].get('overall_accuracy', 0) * 100)
            if 'consistency' in metric:
                consistency_scores.append(metric['consistency'].get('overall_consistency', 0) * 100)
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quality Dashboard - {dataset_name}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .dashboard-card {{
            margin-bottom: 1rem;
        }}
        .metric-value {{
            font-size: 2rem;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-12">
                <h1 class="text-center mb-4">Quality Dashboard</h1>
                <h3 class="text-center text-muted mb-4">{dataset_name}</h3>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-3">
                <div class="card dashboard-card">
                    <div class="card-body text-center">
                        <h5>Latest Score</h5>
                        <div class="metric-value text-primary">{overall_scores[-1]:.1f}%</div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card dashboard-card">
                    <div class="card-body text-center">
                        <h5>Completeness</h5>
                        <div class="metric-value text-success">{completeness_scores[-1]:.1f}%</div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card dashboard-card">
                    <div class="card-body text-center">
                        <h5>Accuracy</h5>
                        <div class="metric-value text-info">{accuracy_scores[-1]:.1f}%</div>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card dashboard-card">
                    <div class="card-body text-center">
                        <h5>Consistency</h5>
                        <div class="metric-value text-warning">{consistency_scores[-1]:.1f}%</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Quality Trends Over Time</h5>
                    </div>
                    <div class="card-body">
                        <canvas id="trendChart" width="400" height="200"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const ctx = document.getElementById('trendChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(timestamps)},
                datasets: [
                    {{
                        label: 'Overall Score',
                        data: {json.dumps(overall_scores)},
                        borderColor: 'rgba(0, 123, 255, 1)',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        tension: 0.1
                    }},
                    {{
                        label: 'Completeness',
                        data: {json.dumps(completeness_scores)},
                        borderColor: 'rgba(40, 167, 69, 1)',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        tension: 0.1
                    }},
                    {{
                        label: 'Accuracy',
                        data: {json.dumps(accuracy_scores)},
                        borderColor: 'rgba(23, 162, 184, 1)',
                        backgroundColor: 'rgba(23, 162, 184, 0.1)',
                        tension: 0.1
                    }},
                    {{
                        label: 'Consistency',
                        data: {json.dumps(consistency_scores)},
                        borderColor: 'rgba(255, 193, 7, 1)',
                        backgroundColor: 'rgba(255, 193, 7, 0.1)',
                        tension: 0.1
                    }}
                ]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
        """
        return html
    
    def _create_empty_dashboard_html(self, dataset_name: str) -> str:
        """Create empty dashboard HTML when no metrics history is available."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quality Dashboard - {dataset_name}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-12 text-center">
                <h1>Quality Dashboard</h1>
                <h3 class="text-muted">{dataset_name}</h3>
                <div class="alert alert-info mt-4">
                    <h4>No Quality Data Available</h4>
                    <p>Run quality assessment to generate dashboard data.</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
        """ 