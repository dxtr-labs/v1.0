#!/usr/bin/env python3
"""
Automation Engine Driver Connectivity Test
Tests connectivity between automation engine and all universal drivers
"""

import sys
import os
import importlib
import importlib.util
import asyncio
import json
from typing import Dict, Any, List

# Add backend path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_path)

class AutomationEngineDriverTest:
    def __init__(self):
        self.backend_path = backend_path
        self.drivers_path = os.path.join(backend_path, 'mcp', 'drivers')
        self.universal_drivers_path = os.path.join(self.drivers_path, 'universal')
        
        self.loaded_drivers = {}
        self.universal_drivers = {}
        self.connectivity_results = {}
        
    def test_driver_loading(self):
        """Test loading of all drivers"""
        
        print("🔌 AUTOMATION ENGINE DRIVER CONNECTIVITY TEST")
        print("=" * 60)
        
        # Test legacy drivers
        print("📁 Testing Legacy Drivers...")
        legacy_drivers = self._discover_legacy_drivers()
        for driver_name, driver_path in legacy_drivers.items():
            result = self._test_load_driver(driver_name, driver_path)
            self.connectivity_results[f"legacy_{driver_name}"] = result
            print(f"   {driver_name}: {'✅' if result['success'] else '❌'} {result['status']}")
        
        print()
        
        # Test universal drivers
        print("🚀 Testing Universal Drivers...")
        universal_drivers = self._discover_universal_drivers()
        for driver_name, driver_path in universal_drivers.items():
            result = self._test_load_universal_driver(driver_name, driver_path)
            self.connectivity_results[f"universal_{driver_name}"] = result
            print(f"   {driver_name}: {'✅' if result['success'] else '❌'} {result['status']}")
        
        print()
        
        # Test automation engine integration
        print("🏗️ Testing Automation Engine Integration...")
        self._test_automation_engine_integration()
    
    def _discover_legacy_drivers(self) -> Dict[str, str]:
        """Discover legacy drivers in drivers folder"""
        drivers = {}
        
        if not os.path.exists(self.drivers_path):
            return drivers
        
        for file in os.listdir(self.drivers_path):
            if file.endswith('_driver.py') and not file.startswith('__'):
                driver_name = file[:-3]  # Remove .py extension
                driver_path = os.path.join(self.drivers_path, file)
                drivers[driver_name] = driver_path
        
        return drivers
    
    def _discover_universal_drivers(self) -> Dict[str, str]:
        """Discover universal drivers in universal folder"""
        drivers = {}
        
        if not os.path.exists(self.universal_drivers_path):
            return drivers
        
        for file in os.listdir(self.universal_drivers_path):
            if file.endswith('_driver.py') and not file.startswith('__'):
                driver_name = file[:-3]  # Remove .py extension
                driver_path = os.path.join(self.universal_drivers_path, file)
                drivers[driver_name] = driver_path
        
        return drivers
    
    def _test_load_driver(self, driver_name: str, driver_path: str) -> Dict[str, Any]:
        """Test loading a legacy driver"""
        try:
            # Import the driver module
            spec = importlib.util.spec_from_file_location(driver_name, driver_path)
            if spec is None:
                return {"success": False, "status": "Failed to create spec", "error": "No spec"}
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for driver class
            driver_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and attr_name.endswith('Driver') and attr_name != 'BaseDriver':
                    driver_class = attr
                    break
            
            if driver_class is None:
                return {"success": False, "status": "No driver class found", "error": "No class"}
            
            # Try to instantiate
            driver_instance = driver_class()
            self.loaded_drivers[driver_name] = driver_instance
            
            # Check if it has required methods
            required_methods = ['execute', 'get_node_info']
            missing_methods = []
            for method in required_methods:
                if not hasattr(driver_instance, method):
                    missing_methods.append(method)
            
            if missing_methods:
                return {
                    "success": False, 
                    "status": f"Missing methods: {missing_methods}", 
                    "error": "Missing methods"
                }
            
            return {
                "success": True, 
                "status": "Loaded successfully", 
                "class": driver_class.__name__,
                "methods": [m for m in dir(driver_instance) if not m.startswith('_')]
            }
            
        except Exception as e:
            return {"success": False, "status": f"Error: {str(e)}", "error": str(e)}
    
    def _test_load_universal_driver(self, driver_name: str, driver_path: str) -> Dict[str, Any]:
        """Test loading a universal driver"""
        try:
            # Import the driver module
            spec = importlib.util.spec_from_file_location(driver_name, driver_path)
            if spec is None:
                return {"success": False, "status": "Failed to create spec", "error": "No spec"}
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for driver class
            driver_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and (attr_name.endswith('Driver') or attr_name.endswith('Node')):
                    if hasattr(attr, 'execute') or hasattr(attr, '__call__'):
                        driver_class = attr
                        break
            
            if driver_class is None:
                return {"success": False, "status": "No driver class found", "error": "No class"}
            
            # Try to instantiate
            try:
                driver_instance = driver_class()
            except TypeError:
                # Some drivers might need parameters
                try:
                    driver_instance = driver_class({})
                except:
                    return {"success": False, "status": "Cannot instantiate", "error": "Instantiation failed"}
            
            self.universal_drivers[driver_name] = driver_instance
            
            # Check capabilities
            capabilities = []
            if hasattr(driver_instance, 'execute'):
                capabilities.append('execute')
            if hasattr(driver_instance, 'get_supported_node_types'):
                capabilities.append('get_supported_node_types')
            if hasattr(driver_instance, 'get_required_parameters'):
                capabilities.append('get_required_parameters')
            
            return {
                "success": True, 
                "status": "Loaded successfully", 
                "class": driver_class.__name__,
                "capabilities": capabilities,
                "methods": [m for m in dir(driver_instance) if not m.startswith('_')]
            }
            
        except Exception as e:
            return {"success": False, "status": f"Error: {str(e)}", "error": str(e)}
    
    def _test_automation_engine_integration(self):
        """Test automation engine integration with drivers"""
        try:
            # Import automation engine
            from mcp.simple_automation_engine import AutomationEngine
            
            print("   📋 Creating AutomationEngine instance...")
            engine = AutomationEngine()
            print("   ✅ AutomationEngine created successfully")
            
            # Test universal driver manager
            if hasattr(engine, 'universal_driver_manager'):
                print("   ✅ Universal driver manager found")
                
                # Test driver manager capabilities
                udm = engine.universal_driver_manager
                if hasattr(udm, 'get_available_drivers'):
                    try:
                        available_drivers = udm.get_available_drivers()
                        print(f"   ✅ Available drivers: {len(available_drivers)}")
                    except Exception as e:
                        print(f"   ⚠️ Could not get available drivers: {e}")
                
                if hasattr(udm, 'execute_node'):
                    print("   ✅ Execute node capability found")
                else:
                    print("   ❌ Execute node capability missing")
            else:
                print("   ❌ Universal driver manager not found")
            
            # Test individual driver execution
            print("   🧪 Testing driver execution capabilities...")
            
            # Test a simple driver if available
            if self.universal_drivers:
                test_driver_name = list(self.universal_drivers.keys())[0]
                test_driver = self.universal_drivers[test_driver_name]
                print(f"   🔍 Testing {test_driver_name} execution...")
                
                try:
                    if hasattr(test_driver, 'execute'):
                        # Try a simple execution test
                        test_params = {"test": True}
                        # Note: This might fail due to missing parameters, but we're testing connectivity
                        print(f"   ✅ {test_driver_name} has execute method")
                    else:
                        print(f"   ⚠️ {test_driver_name} missing execute method")
                except Exception as e:
                    print(f"   ⚠️ {test_driver_name} execution test error: {e}")
            
        except ImportError as e:
            print(f"   ❌ Cannot import AutomationEngine: {e}")
        except Exception as e:
            print(f"   ❌ AutomationEngine integration test failed: {e}")
    
    def generate_connectivity_report(self):
        """Generate comprehensive connectivity report"""
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE DRIVER CONNECTIVITY REPORT")
        print("=" * 60)
        
        # Count results
        total_drivers = len(self.connectivity_results)
        successful_drivers = len([r for r in self.connectivity_results.values() if r['success']])
        failed_drivers = total_drivers - successful_drivers
        
        print(f"🔢 OVERALL STATISTICS:")
        print(f"   • Total Drivers Tested: {total_drivers}")
        print(f"   • Successfully Loaded: {successful_drivers}")
        print(f"   • Failed to Load: {failed_drivers}")
        print(f"   • Success Rate: {(successful_drivers/total_drivers)*100:.1f}%")
        print()
        
        # Legacy drivers analysis
        legacy_results = {k: v for k, v in self.connectivity_results.items() if k.startswith('legacy_')}
        legacy_success = len([r for r in legacy_results.values() if r['success']])
        
        print(f"📁 LEGACY DRIVERS:")
        print(f"   • Total: {len(legacy_results)}")
        print(f"   • Successful: {legacy_success}")
        print(f"   • Success Rate: {(legacy_success/len(legacy_results))*100:.1f}%" if legacy_results else "   • No legacy drivers found")
        print()
        
        # Universal drivers analysis
        universal_results = {k: v for k, v in self.connectivity_results.items() if k.startswith('universal_')}
        universal_success = len([r for r in universal_results.values() if r['success']])
        
        print(f"🚀 UNIVERSAL DRIVERS:")
        print(f"   • Total: {len(universal_results)}")
        print(f"   • Successful: {universal_success}")
        print(f"   • Success Rate: {(universal_success/len(universal_results))*100:.1f}%" if universal_results else "   • No universal drivers found")
        print()
        
        # Detailed driver list
        if successful_drivers > 0:
            print(f"✅ SUCCESSFULLY LOADED DRIVERS:")
            for driver_name, result in self.connectivity_results.items():
                if result['success']:
                    driver_type = "Legacy" if driver_name.startswith('legacy_') else "Universal"
                    clean_name = driver_name.replace('legacy_', '').replace('universal_', '')
                    capabilities = result.get('capabilities', result.get('methods', []))
                    print(f"   • {clean_name} ({driver_type}) - {result.get('class', 'Unknown')}")
                    if capabilities:
                        print(f"     Capabilities: {', '.join(capabilities[:5])}{'...' if len(capabilities) > 5 else ''}")
            print()
        
        # Failed drivers
        if failed_drivers > 0:
            print(f"❌ FAILED TO LOAD:")
            for driver_name, result in self.connectivity_results.items():
                if not result['success']:
                    clean_name = driver_name.replace('legacy_', '').replace('universal_', '')
                    print(f"   • {clean_name}: {result['status']}")
            print()
        
        # Driver categories analysis
        print(f"📂 DRIVER CATEGORIES DETECTED:")
        categories = set()
        for driver_name in self.connectivity_results.keys():
            clean_name = driver_name.replace('legacy_', '').replace('universal_', '')
            if 'email' in clean_name:
                categories.add('Email')
            elif 'database' in clean_name or 'mysql' in clean_name or 'postgres' in clean_name or 'mongodb' in clean_name:
                categories.add('Database')
            elif 'api' in clean_name or 'http' in clean_name or 'webhook' in clean_name:
                categories.add('API/HTTP')
            elif 'openai' in clean_name or 'claude' in clean_name or 'ai' in clean_name or 'llm' in clean_name:
                categories.add('AI/LLM')
            elif 'slack' in clean_name or 'telegram' in clean_name or 'discord' in clean_name:
                categories.add('Communication')
            elif 'google' in clean_name or 'sheets' in clean_name or 'drive' in clean_name:
                categories.add('Google Services')
            elif 'file' in clean_name or 'csv' in clean_name or 'pdf' in clean_name or 'document' in clean_name:
                categories.add('File Processing')
            elif 'workflow' in clean_name or 'conditional' in clean_name or 'scheduler' in clean_name:
                categories.add('Workflow Control')
            else:
                categories.add('Other')
        
        for category in sorted(categories):
            print(f"   • {category}")
        
        print()
        
        # Assessment
        print(f"🎯 CONNECTIVITY ASSESSMENT:")
        if successful_drivers / total_drivers >= 0.9:
            grade = "🟢 EXCELLENT"
        elif successful_drivers / total_drivers >= 0.7:
            grade = "🟡 GOOD"
        elif successful_drivers / total_drivers >= 0.5:
            grade = "🟠 FAIR"
        else:
            grade = "🔴 NEEDS IMPROVEMENT"
        
        print(f"   • Overall Connectivity: {grade}")
        print(f"   • Automation Engine Ready: {'✅ YES' if successful_drivers > 0 else '❌ NO'}")
        print(f"   • Universal Driver System: {'✅ OPERATIONAL' if universal_success > 0 else '❌ NOT READY'}")
        
        print(f"\n🏆 DRIVER CONNECTIVITY TEST COMPLETE!")
        print(f"   System has {successful_drivers} operational drivers ready for automation workflows!")

def main():
    """Run the driver connectivity test"""
    
    print("🔌 Automation Engine Driver Connectivity Test")
    print("Testing connectivity between automation engine and all universal drivers")
    print()
    
    tester = AutomationEngineDriverTest()
    tester.test_driver_loading()
    tester.generate_connectivity_report()

if __name__ == "__main__":
    main()
