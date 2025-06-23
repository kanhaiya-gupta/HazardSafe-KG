#!/usr/bin/env python3
"""
Test script for Data Validation
Tests validation rules, business logic, and data quality checks
"""

import asyncio
import argparse
import sys
import os
import logging
import json
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from validation.validator import DataValidator
from validation.rules import BusinessRules
from validation.csv_validator import CSVValidator
from validation.json_validator import JSONValidator
from validation.compatibility import CompatibilityChecker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ValidationTester:
    def __init__(self):
        self.validator = DataValidator()
        self.rules = BusinessRules()
        self.csv_validator = CSVValidator()
        self.json_validator = JSONValidator()
        self.compatibility_checker = CompatibilityChecker()
        
    async def test_substance_validation(self):
        """Test substance data validation"""
        logger.info("Testing Substance Validation...")
        
        try:
            # Valid substance data
            valid_substances = [
                {
                    "name": "Sulfuric Acid",
                    "formula": "H2SO4",
                    "cas_number": "7664-93-9",
                    "hazard_class": "corrosive",
                    "molecular_weight": 98.08,
                    "density": 1.84,
                    "melting_point": 10.31,
                    "boiling_point": 337.0
                },
                {
                    "name": "Sodium Hydroxide",
                    "formula": "NaOH",
                    "cas_number": "1310-73-2",
                    "hazard_class": "corrosive",
                    "molecular_weight": 40.00,
                    "density": 2.13,
                    "melting_point": 318.0,
                    "boiling_point": 1388.0
                }
            ]
            
            # Invalid substance data
            invalid_substances = [
                {
                    "name": "",  # Empty name
                    "formula": "H2SO4",
                    "cas_number": "7664-93-9",
                    "hazard_class": "corrosive"
                },
                {
                    "name": "Invalid Acid",
                    "formula": "H2SO4",  # Valid formula
                    "cas_number": "invalid-cas",  # Invalid CAS
                    "hazard_class": "unknown_hazard"  # Invalid hazard class
                },
                {
                    "name": "Test Substance",
                    "formula": "H2SO4",
                    "cas_number": "7664-93-9",
                    "hazard_class": "corrosive",
                    "molecular_weight": -10.0,  # Negative weight
                    "melting_point": 10000.0  # Unrealistic temperature
                }
            ]
            
            validation_results = {
                "valid_substances": [],
                "invalid_substances": [],
                "total_tested": len(valid_substances) + len(invalid_substances),
                "passed": 0,
                "failed": 0
            }
            
            # Test valid substances
            for substance in valid_substances:
                result = await self.validator.validate_data(substance, "substances")
                validation_results["valid_substances"].append({
                    "data": substance,
                    "result": result
                })
                if result["valid"]:
                    validation_results["passed"] += 1
                else:
                    validation_results["failed"] += 1
                    logger.warning(f"Valid substance failed validation: {result.get('errors', [])}")
            
            # Test invalid substances
            for substance in invalid_substances:
                result = await self.validator.validate_data(substance, "substances")
                validation_results["invalid_substances"].append({
                    "data": substance,
                    "result": result
                })
                if result["valid"]:
                    validation_results["passed"] += 1
                    logger.warning(f"Invalid substance passed validation: {substance}")
                else:
                    validation_results["failed"] += 1
            
            logger.info(f"✅ Substance validation completed")
            logger.info(f"Total tested: {validation_results['total_tested']}")
            logger.info(f"Passed: {validation_results['passed']}")
            logger.info(f"Failed: {validation_results['failed']}")
            
            return {
                "success": True,
                "validation_results": validation_results
            }
            
        except Exception as e:
            logger.error(f"❌ Substance validation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_container_validation(self):
        """Test container data validation"""
        logger.info("Testing Container Validation...")
        
        try:
            # Valid container data
            valid_containers = [
                {
                    "name": "Glass Bottle 1L",
                    "material": "glass",
                    "capacity": 1.0,
                    "pressure_rating": 1.0,
                    "temperature_rating": 100.0,
                    "manufacturer": "LabSupply Co."
                },
                {
                    "name": "Steel Drum 200L",
                    "material": "stainless_steel",
                    "capacity": 200.0,
                    "pressure_rating": 5.0,
                    "temperature_rating": 200.0,
                    "manufacturer": "Industrial Containers Ltd."
                }
            ]
            
            # Invalid container data
            invalid_containers = [
                {
                    "name": "",  # Empty name
                    "material": "glass",
                    "capacity": 1.0
                },
                {
                    "name": "Test Container",
                    "material": "unknown_material",  # Invalid material
                    "capacity": -1.0,  # Negative capacity
                    "pressure_rating": -5.0  # Negative pressure
                }
            ]
            
            validation_results = {
                "valid_containers": [],
                "invalid_containers": [],
                "total_tested": len(valid_containers) + len(invalid_containers),
                "passed": 0,
                "failed": 0
            }
            
            # Test valid containers
            for container in valid_containers:
                result = await self.validator.validate_data(container, "containers")
                validation_results["valid_containers"].append({
                    "data": container,
                    "result": result
                })
                if result["valid"]:
                    validation_results["passed"] += 1
                else:
                    validation_results["failed"] += 1
            
            # Test invalid containers
            for container in invalid_containers:
                result = await self.validator.validate_data(container, "containers")
                validation_results["invalid_containers"].append({
                    "data": container,
                    "result": result
                })
                if result["valid"]:
                    validation_results["passed"] += 1
                else:
                    validation_results["failed"] += 1
            
            logger.info(f"✅ Container validation completed")
            logger.info(f"Total tested: {validation_results['total_tested']}")
            logger.info(f"Passed: {validation_results['passed']}")
            logger.info(f"Failed: {validation_results['failed']}")
            
            return {
                "success": True,
                "validation_results": validation_results
            }
            
        except Exception as e:
            logger.error(f"❌ Container validation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_test_validation(self):
        """Test test data validation"""
        logger.info("Testing Test Data Validation...")
        
        try:
            # Valid test data
            valid_tests = [
                {
                    "name": "Compatibility Test 1",
                    "test_type": "storage",
                    "standard": "ASTM D543",
                    "duration": 24,
                    "temperature": 25.0,
                    "pressure": 1.0,
                    "result": "pass"
                },
                {
                    "name": "Corrosion Test 1",
                    "test_type": "material",
                    "standard": "ISO 9227",
                    "duration": 168,
                    "temperature": 35.0,
                    "pressure": 1.0,
                    "result": "fail"
                }
            ]
            
            # Invalid test data
            invalid_tests = [
                {
                    "name": "",  # Empty name
                    "test_type": "storage",
                    "duration": 24
                },
                {
                    "name": "Invalid Test",
                    "test_type": "unknown_type",  # Invalid test type
                    "duration": -10,  # Negative duration
                    "temperature": 10000.0,  # Unrealistic temperature
                    "result": "invalid_result"  # Invalid result
                }
            ]
            
            validation_results = {
                "valid_tests": [],
                "invalid_tests": [],
                "total_tested": len(valid_tests) + len(invalid_tests),
                "passed": 0,
                "failed": 0
            }
            
            # Test valid tests
            for test in valid_tests:
                result = await self.validator.validate_data(test, "tests")
                validation_results["valid_tests"].append({
                    "data": test,
                    "result": result
                })
                if result["valid"]:
                    validation_results["passed"] += 1
                else:
                    validation_results["failed"] += 1
            
            # Test invalid tests
            for test in invalid_tests:
                result = await self.validator.validate_data(test, "tests")
                validation_results["invalid_tests"].append({
                    "data": test,
                    "result": result
                })
                if result["valid"]:
                    validation_results["passed"] += 1
                else:
                    validation_results["failed"] += 1
            
            logger.info(f"✅ Test data validation completed")
            logger.info(f"Total tested: {validation_results['total_tested']}")
            logger.info(f"Passed: {validation_results['passed']}")
            logger.info(f"Failed: {validation_results['failed']}")
            
            return {
                "success": True,
                "validation_results": validation_results
            }
            
        except Exception as e:
            logger.error(f"❌ Test data validation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_compatibility_rules(self):
        """Test chemical compatibility rules"""
        logger.info("Testing Compatibility Rules...")
        
        try:
            # Test compatibility scenarios
            compatibility_tests = [
                {
                    "substance": "H2SO4",
                    "container": "glass",
                    "expected": True,
                    "description": "Sulfuric acid in glass container"
                },
                {
                    "substance": "H2SO4",
                    "container": "aluminum",
                    "expected": False,
                    "description": "Sulfuric acid in aluminum container"
                },
                {
                    "substance": "NaOH",
                    "container": "glass",
                    "expected": True,
                    "description": "Sodium hydroxide in glass container"
                },
                {
                    "substance": "NaOH",
                    "container": "plastic",
                    "expected": False,
                    "description": "Sodium hydroxide in plastic container"
                }
            ]
            
            results = {
                "tests": [],
                "total_tested": len(compatibility_tests),
                "correct": 0,
                "incorrect": 0
            }
            
            for test in compatibility_tests:
                is_compatible = self.rules.check_chemical_compatibility(
                    test["substance"], 
                    test["container"]
                )
                
                correct = (is_compatible == test["expected"])
                results["tests"].append({
                    "test": test,
                    "result": is_compatible,
                    "correct": correct
                })
                
                if correct:
                    results["correct"] += 1
                else:
                    results["incorrect"] += 1
                    logger.warning(f"Compatibility test failed: {test['description']}")
            
            logger.info(f"✅ Compatibility rules testing completed")
            logger.info(f"Total tested: {results['total_tested']}")
            logger.info(f"Correct: {results['correct']}")
            logger.info(f"Incorrect: {results['incorrect']}")
            
            return {
                "success": True,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Compatibility rules error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_csv_validation(self):
        """Test CSV file validation"""
        logger.info("Testing CSV Validation...")
        
        try:
            # Create sample CSV data
            sample_csv_data = """name,formula,cas_number,hazard_class,molecular_weight
Sulfuric Acid,H2SO4,7664-93-9,corrosive,98.08
Sodium Hydroxide,NaOH,1310-73-2,corrosive,40.00
Methanol,CH3OH,67-56-1,flammable,32.04"""
            
            # Write to temporary file
            csv_file = "temp_test_substances.csv"
            with open(csv_file, 'w') as f:
                f.write(sample_csv_data)
            
            # Validate CSV
            result = await self.csv_validator.validate_csv_file(csv_file, "substances")
            
            # Clean up
            os.remove(csv_file)
            
            logger.info(f"✅ CSV validation completed")
            logger.info(f"Valid: {result['valid']}")
            logger.info(f"Errors: {len(result.get('errors', []))}")
            
            return {
                "success": True,
                "csv_validation": result
            }
            
        except Exception as e:
            logger.error(f"❌ CSV validation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_json_validation(self):
        """Test JSON data validation"""
        logger.info("Testing JSON Validation...")
        
        try:
            # Sample JSON data
            sample_json_data = {
                "substances": [
                    {
                        "name": "Sulfuric Acid",
                        "formula": "H2SO4",
                        "cas_number": "7664-93-9",
                        "hazard_class": "corrosive"
                    },
                    {
                        "name": "Sodium Hydroxide",
                        "formula": "NaOH",
                        "cas_number": "1310-73-2",
                        "hazard_class": "corrosive"
                    }
                ]
            }
            
            # Validate JSON
            result = await self.json_validator.validate_json_data(sample_json_data, "substances")
            
            logger.info(f"✅ JSON validation completed")
            logger.info(f"Valid: {result['valid']}")
            logger.info(f"Errors: {len(result.get('errors', []))}")
            
            return {
                "success": True,
                "json_validation": result
            }
            
        except Exception as e:
            logger.error(f"❌ JSON validation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_business_rules(self):
        """Test business rules validation"""
        logger.info("Testing Business Rules...")
        
        try:
            # Test various business rules
            business_rules_tests = [
                {
                    "rule": "hazard_class_validation",
                    "data": {"hazard_class": "corrosive"},
                    "expected": True
                },
                {
                    "rule": "cas_number_validation",
                    "data": {"cas_number": "7664-93-9"},
                    "expected": True
                },
                {
                    "rule": "cas_number_validation",
                    "data": {"cas_number": "invalid-cas"},
                    "expected": False
                },
                {
                    "rule": "temperature_validation",
                    "data": {"melting_point": 10.31, "boiling_point": 337.0},
                    "expected": True
                },
                {
                    "rule": "temperature_validation",
                    "data": {"melting_point": 1000.0, "boiling_point": 10.0},
                    "expected": False
                }
            ]
            
            results = {
                "tests": [],
                "total_tested": len(business_rules_tests),
                "passed": 0,
                "failed": 0
            }
            
            for test in business_rules_tests:
                # Apply business rule validation
                if test["rule"] == "hazard_class_validation":
                    valid = self.rules.validate_hazard_class(test["data"]["hazard_class"])
                elif test["rule"] == "cas_number_validation":
                    valid = self.rules.validate_cas_number(test["data"]["cas_number"])
                elif test["rule"] == "temperature_validation":
                    valid = self.rules.validate_temperature_range(
                        test["data"]["melting_point"],
                        test["data"]["boiling_point"]
                    )
                else:
                    valid = False
                
                correct = (valid == test["expected"])
                results["tests"].append({
                    "test": test,
                    "result": valid,
                    "correct": correct
                })
                
                if correct:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
            
            logger.info(f"✅ Business rules testing completed")
            logger.info(f"Total tested: {results['total_tested']}")
            logger.info(f"Passed: {results['passed']}")
            logger.info(f"Failed: {results['failed']}")
            
            return {
                "success": True,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Business rules error: {e}")
            return {"success": False, "error": str(e)}

async def main():
    parser = argparse.ArgumentParser(description="Test Data Validation")
    parser.add_argument("--type", choices=["substances", "containers", "tests", "compatibility", "csv", "json", "business", "all"], 
                       help="Test specific data type")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    tester = ValidationTester()
    
    if args.type == "substances":
        result = await tester.test_substance_validation()
    elif args.type == "containers":
        result = await tester.test_container_validation()
    elif args.type == "tests":
        result = await tester.test_test_validation()
    elif args.type == "compatibility":
        result = await tester.test_compatibility_rules()
    elif args.type == "csv":
        result = await tester.test_csv_validation()
    elif args.type == "json":
        result = await tester.test_json_validation()
    elif args.type == "business":
        result = await tester.test_business_rules()
    else:
        # Run all tests
        logger.info("Running all validation tests...")
        
        results = {}
        results["substances"] = await tester.test_substance_validation()
        results["containers"] = await tester.test_container_validation()
        results["tests"] = await tester.test_test_validation()
        results["compatibility"] = await tester.test_compatibility_rules()
        results["csv"] = await tester.test_csv_validation()
        results["json"] = await tester.test_json_validation()
        results["business"] = await tester.test_business_rules()
        
        # Summary
        successful_tests = sum(1 for r in results.values() if r.get("success", False))
        total_tests = len(results)
        
        logger.info(f"\n{'='*50}")
        logger.info(f"VALIDATION TEST SUMMARY")
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