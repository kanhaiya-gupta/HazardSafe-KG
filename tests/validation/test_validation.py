# test_validation.py
from validation.csv_validator import CSVValidator
from validation.json_validator import JSONValidator
from validation.compatibility import CompatibilityValidator
from validation.rules import ValidationRules

# Test CSV
csv_validator = CSVValidator(ValidationRules.CSV_RULES)
csv_report = csv_validator.validate('data/sample.csv')
print("CSV Validation Report:", csv_report)

# Test JSON
json_validator = JSONValidator(ValidationRules.JSON_RULES)
json_report = json_validator.validate('data/sample.json')
print("JSON Validation Report:", json_report)

# Test Compatibility
compat_rules = [
    ('H2SO4', 'NaOH', 'incompatible'),
    ('H2SO4', 'HCl', 'compatible'),
    ('Toluene', 'Acetone', 'compatible')
]
compat_validator = CompatibilityValidator(compat_rules)
compat_report = compat_validator.validate(['H2SO4', 'NaOH', 'Toluene'])
print("Compatibility Validation Report:", compat_report)