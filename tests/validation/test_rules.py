"""
Tests for validation rules functionality.
"""
import pytest
import tempfile
import os
from validation.rules import ValidationRules


class TestValidationRules:
    """Test cases for ValidationRules class."""
    
    def test_rules_initialization(self):
        """Test ValidationRules initialization."""
        rules = ValidationRules()
        assert rules is not None
    
    def test_load_rules_from_file(self, temp_data_dir):
        """Test loading validation rules from file."""
        rules_file = os.path.join(temp_data_dir, "validation_rules.json")
        with open(rules_file, 'w') as f:
            f.write("""
{
    "required_fields": ["name", "cas_number"],
    "field_types": {
        "name": "string",
        "cas_number": "string",
        "risk_level": "enum"
    },
    "enum_values": {
        "risk_level": ["Low", "Medium", "High"]
    }
}
            """)
        
        rules = ValidationRules()
        result = rules.load_rules_from_file(rules_file)
        assert result is True
        assert "required_fields" in rules.rules
        assert "field_types" in rules.rules
    
    def test_load_rules_from_dict(self):
        """Test loading validation rules from dictionary."""
        rules_data = {
            "required_fields": ["name", "cas_number"],
            "field_types": {
                "name": "string",
                "cas_number": "string"
            }
        }
        
        rules = ValidationRules()
        result = rules.load_rules_from_dict(rules_data)
        assert result is True
        assert rules.rules["required_fields"] == ["name", "cas_number"]
    
    def test_validate_required_fields_valid(self, sample_validation_data):
        """Test validation of required fields with valid data."""
        rules = ValidationRules()
        rules.load_rules_from_dict(sample_validation_data["validation_rules"])
        
        valid_data = sample_validation_data["valid_csv"][0]
        result = rules.validate_required_fields(valid_data)
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_required_fields_invalid(self, sample_validation_data):
        """Test validation of required fields with invalid data."""
        rules = ValidationRules()
        rules.load_rules_from_dict(sample_validation_data["validation_rules"])
        
        invalid_data = {"name": "Test", "cas_number": ""}  # Missing cas_number
        result = rules.validate_required_fields(invalid_data)
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_validate_field_types_valid(self):
        """Test validation of field types with valid data."""
        rules = ValidationRules()
        rules.load_rules_from_dict({
            "field_types": {
                "name": "string",
                "cas_number": "string",
                "risk_level": "enum"
            },
            "enum_values": {
                "risk_level": ["Low", "Medium", "High"]
            }
        })
        
        valid_data = {
            "name": "Methanol",
            "cas_number": "67-56-1",
            "risk_level": "High"
        }
        
        result = rules.validate_field_types(valid_data)
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_field_types_invalid(self):
        """Test validation of field types with invalid data."""
        rules = ValidationRules()
        rules.load_rules_from_dict({
            "field_types": {
                "name": "string",
                "cas_number": "string",
                "risk_level": "enum"
            },
            "enum_values": {
                "risk_level": ["Low", "Medium", "High"]
            }
        })
        
        invalid_data = {
            "name": 123,  # Should be string
            "cas_number": "67-56-1",
            "risk_level": "Invalid"  # Not in enum
        }
        
        result = rules.validate_field_types(invalid_data)
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_validate_cas_number_format_valid(self):
        """Test validation of CAS number format with valid data."""
        rules = ValidationRules()
        
        valid_cas_numbers = ["67-56-1", "64-17-5", "108-88-3"]
        for cas_number in valid_cas_numbers:
            result = rules.validate_cas_number_format(cas_number)
            assert result["valid"] is True
    
    def test_validate_cas_number_format_invalid(self):
        """Test validation of CAS number format with invalid data."""
        rules = ValidationRules()
        
        invalid_cas_numbers = ["invalid", "67-56", "67-56-1-2", ""]
        for cas_number in invalid_cas_numbers:
            result = rules.validate_cas_number_format(cas_number)
            assert result["valid"] is False
    
    def test_validate_risk_levels_valid(self):
        """Test validation of risk levels with valid data."""
        rules = ValidationRules()
        rules.load_rules_from_dict({
            "enum_values": {
                "risk_level": ["Low", "Medium", "High"]
            }
        })
        
        valid_risk_levels = ["Low", "Medium", "High"]
        for risk_level in valid_risk_levels:
            result = rules.validate_risk_level(risk_level)
            assert result["valid"] is True
    
    def test_validate_risk_levels_invalid(self):
        """Test validation of risk levels with invalid data."""
        rules = ValidationRules()
        rules.load_rules_from_dict({
            "enum_values": {
                "risk_level": ["Low", "Medium", "High"]
            }
        })
        
        invalid_risk_levels = ["Very High", "Low Risk", "", "unknown"]
        for risk_level in invalid_risk_levels:
            result = rules.validate_risk_level(risk_level)
            assert result["valid"] is False
    
    def test_validate_csv_data_valid(self, sample_validation_data):
        """Test validation of CSV data with valid data."""
        rules = ValidationRules()
        rules.load_rules_from_dict(sample_validation_data["validation_rules"])
        
        result = rules.validate_csv_data(sample_validation_data["valid_csv"])
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_csv_data_invalid(self, sample_validation_data):
        """Test validation of CSV data with invalid data."""
        rules = ValidationRules()
        rules.load_rules_from_dict(sample_validation_data["validation_rules"])
        
        result = rules.validate_csv_data(sample_validation_data["invalid_csv"])
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_validate_json_data_valid(self):
        """Test validation of JSON data with valid data."""
        rules = ValidationRules()
        rules.load_rules_from_dict({
            "required_fields": ["name", "cas_number"],
            "field_types": {
                "name": "string",
                "cas_number": "string"
            }
        })
        
        valid_json = {
            "substances": [
                {"name": "Methanol", "cas_number": "67-56-1"},
                {"name": "Ethanol", "cas_number": "64-17-5"}
            ]
        }
        
        result = rules.validate_json_data(valid_json)
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_json_data_invalid(self):
        """Test validation of JSON data with invalid data."""
        rules = ValidationRules()
        rules.load_rules_from_dict({
            "required_fields": ["name", "cas_number"],
            "field_types": {
                "name": "string",
                "cas_number": "string"
            }
        })
        
        invalid_json = {
            "substances": [
                {"name": "", "cas_number": "invalid"},
                {"name": "Test"}
            ]
        }
        
        result = rules.validate_json_data(invalid_json)
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_custom_validation_rule(self):
        """Test custom validation rule."""
        rules = ValidationRules()
        
        # Define custom rule
        def custom_rule(data):
            if "name" in data and len(data["name"]) < 3:
                return {"valid": False, "errors": ["Name must be at least 3 characters"]}
            return {"valid": True, "errors": []}
        
        rules.add_custom_rule("name_length", custom_rule)
        
        # Test with valid data
        valid_data = {"name": "Methanol"}
        result = rules.apply_custom_rule("name_length", valid_data)
        assert result["valid"] is True
        
        # Test with invalid data
        invalid_data = {"name": "Me"}
        result = rules.apply_custom_rule("name_length", invalid_data)
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_comprehensive_validation(self, sample_validation_data):
        """Test comprehensive validation of data."""
        rules = ValidationRules()
        rules.load_rules_from_dict(sample_validation_data["validation_rules"])
        
        # Test with valid data
        result = rules.validate_comprehensive(sample_validation_data["valid_csv"])
        assert result["valid"] is True
        assert "required_fields" in result
        assert "field_types" in result
        assert "format_validation" in result
        
        # Test with invalid data
        result = rules.validate_comprehensive(sample_validation_data["invalid_csv"])
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_export_validation_report(self, temp_data_dir, sample_validation_data):
        """Test exporting validation report."""
        rules = ValidationRules()
        rules.load_rules_from_dict(sample_validation_data["validation_rules"])
        
        validation_result = rules.validate_comprehensive(sample_validation_data["valid_csv"])
        report_file = os.path.join(temp_data_dir, "validation_report.json")
        
        result = rules.export_validation_report(validation_result, report_file)
        assert result is True
        assert os.path.exists(report_file)
    
    def test_get_validation_statistics(self, sample_validation_data):
        """Test getting validation statistics."""
        rules = ValidationRules()
        rules.load_rules_from_dict(sample_validation_data["validation_rules"])
        
        validation_result = rules.validate_comprehensive(sample_validation_data["valid_csv"])
        stats = rules.get_validation_statistics(validation_result)
        
        assert stats is not None
        assert "total_records" in stats
        assert "valid_records" in stats
        assert "invalid_records" in stats
        assert "error_types" in stats 