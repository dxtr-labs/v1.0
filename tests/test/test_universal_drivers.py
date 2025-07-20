"""
Comprehensive Universal Driver System Test
Tests all 2000+ workflow automation capabilities
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, Any, List

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UniversalDriverSystemTester:
    """Comprehensive tester for the universal driver system"""
    
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    async def run_all_tests(self):
        """Run comprehensive tests of the universal driver system"""
        logger.info("🚀 Starting Universal Driver System Tests...")
        
        try:
            # Import the universal driver manager
            from backend.mcp.universal_driver_manager import universal_driver_manager, initialize_universal_drivers
            
            # Initialize all drivers
            logger.info("📋 Initializing universal drivers...")
            driver_registry = await initialize_universal_drivers()
            
            # Test driver loading and statistics
            await self.test_driver_statistics(universal_driver_manager)
            
            # Test top node types (most frequently used)
            await self.test_top_node_types(universal_driver_manager)
            
            # Test HTTP operations
            await self.test_http_operations(universal_driver_manager)
            
            # Test data processing
            await self.test_data_processing(universal_driver_manager)
            
            # Test LangChain AI operations
            await self.test_langchain_operations(universal_driver_manager)
            
            # Test utility operations
            await self.test_utility_operations(universal_driver_manager)
            
            # Test workflow execution scenarios
            await self.test_workflow_scenarios(universal_driver_manager)
            
            # Test error handling
            await self.test_error_handling(universal_driver_manager)
            
            # Generate final report
            self.generate_final_report()
            
        except Exception as e:
            logger.error(f"❌ Universal driver system test failed: {e}")
            self.add_test_result("Universal Driver System Test", False, str(e))
    
    async def test_driver_statistics(self, driver_manager):
        """Test driver loading and statistics"""
        test_name = "Driver Statistics and Loading"
        logger.info(f"🔧 Testing: {test_name}")
        
        try:
            stats = driver_manager.get_driver_statistics()
            
            # Check if drivers were loaded
            if stats['total_drivers'] > 0:
                logger.info(f"✅ Loaded {stats['total_drivers']} drivers")
                self.add_test_result(f"{test_name} - Driver Loading", True, f"Loaded {stats['total_drivers']} drivers")
            else:
                self.add_test_result(f"{test_name} - Driver Loading", False, "No drivers loaded")
                return
            
            # Check node type coverage
            coverage = stats['coverage']['coverage_percentage']
            if coverage > 0:
                logger.info(f"✅ Node type coverage: {coverage:.1f}%")
                self.add_test_result(f"{test_name} - Coverage", True, f"Coverage: {coverage:.1f}%")
            else:
                self.add_test_result(f"{test_name} - Coverage", False, "Zero coverage")
            
            # List available drivers
            drivers = stats['drivers']
            logger.info(f"📋 Available drivers: {', '.join(drivers)}")
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {e}")
            self.add_test_result(test_name, False, str(e))
    
    async def test_top_node_types(self, driver_manager):
        """Test the most frequently used node types"""
        test_name = "Top Node Types Execution"
        logger.info(f"🔧 Testing: {test_name}")
        
        # Top node types from analysis
        top_node_types = [
            'n8n-nodes-base.stickyNote',  # 5276 instances
            'n8n-nodes-base.set',         # 1907 instances
            'n8n-nodes-base.httpRequest', # 1696 instances
            'n8n-nodes-base.if',          # 849 instances
            'n8n-nodes-base.manualTrigger' # 688 instances
        ]
        
        for node_type in top_node_types:
            try:
                # Test basic execution
                parameters = self._get_test_parameters(node_type)
                context = {"input_data": [{"test": "data"}]}
                
                result = await driver_manager.execute_node(node_type, parameters, context)
                
                if result.get('success'):
                    logger.info(f"✅ {node_type}: Success")
                    self.add_test_result(f"{test_name} - {node_type}", True, "Execution successful")
                else:
                    logger.warning(f"⚠️ {node_type}: Failed - {result.get('error', 'Unknown error')}")
                    self.add_test_result(f"{test_name} - {node_type}", False, result.get('error', 'Unknown error'))
                    
            except Exception as e:
                logger.error(f"❌ {node_type} failed: {e}")
                self.add_test_result(f"{test_name} - {node_type}", False, str(e))
    
    async def test_http_operations(self, driver_manager):
        """Test HTTP-related operations"""
        test_name = "HTTP Operations"
        logger.info(f"🔧 Testing: {test_name}")
        
        http_tests = [
            {
                "node_type": "n8n-nodes-base.httpRequest",
                "parameters": {
                    "url": "https://api.github.com/repos/microsoft/vscode",
                    "method": "GET",
                    "headers": {"User-Agent": "DXTR-AutoFlow-Test"}
                },
                "description": "GitHub API Request"
            },
            {
                "node_type": "n8n-nodes-base.webhook",
                "parameters": {
                    "path": "/test-webhook",
                    "httpMethod": "POST"
                },
                "description": "Webhook Setup"
            },
            {
                "node_type": "n8n-nodes-base.respondToWebhook",
                "parameters": {
                    "responseCode": 200,
                    "responseData": {"status": "success"}
                },
                "description": "Webhook Response"
            }
        ]
        
        for test_case in http_tests:
            try:
                result = await driver_manager.execute_node(
                    test_case["node_type"], 
                    test_case["parameters"], 
                    {"input_data": [{}]}
                )
                
                if result.get('success'):
                    logger.info(f"✅ {test_case['description']}: Success")
                    self.add_test_result(f"{test_name} - {test_case['description']}", True, "Success")
                else:
                    logger.warning(f"⚠️ {test_case['description']}: Failed")
                    self.add_test_result(f"{test_name} - {test_case['description']}", False, result.get('error', 'Failed'))
                    
            except Exception as e:
                logger.error(f"❌ {test_case['description']} failed: {e}")
                self.add_test_result(f"{test_name} - {test_case['description']}", False, str(e))
    
    async def test_data_processing(self, driver_manager):
        """Test data processing operations"""
        test_name = "Data Processing Operations"
        logger.info(f"🔧 Testing: {test_name}")
        
        data_tests = [
            {
                "node_type": "n8n-nodes-base.set",
                "parameters": {
                    "values": {
                        "name": "Test User",
                        "timestamp": "2024-01-01T00:00:00Z",
                        "processed": True
                    }
                },
                "description": "Set Values"
            },
            {
                "node_type": "n8n-nodes-base.filter",
                "parameters": {
                    "conditions": {
                        "field": "status",
                        "operator": "equals",
                        "value": "active"
                    }
                },
                "description": "Filter Data"
            },
            {
                "node_type": "n8n-nodes-base.merge",
                "parameters": {
                    "mode": "append"
                },
                "description": "Merge Data"
            },
            {
                "node_type": "n8n-nodes-base.splitInBatches",
                "parameters": {
                    "batchSize": 5
                },
                "description": "Split in Batches"
            }
        ]
        
        # Create test data
        test_data = [
            {"id": 1, "name": "Item 1", "status": "active"},
            {"id": 2, "name": "Item 2", "status": "inactive"},
            {"id": 3, "name": "Item 3", "status": "active"}
        ]
        
        for test_case in data_tests:
            try:
                result = await driver_manager.execute_node(
                    test_case["node_type"], 
                    test_case["parameters"], 
                    {"input_data": test_data}
                )
                
                if result.get('success'):
                    logger.info(f"✅ {test_case['description']}: Success")
                    self.add_test_result(f"{test_name} - {test_case['description']}", True, "Success")
                else:
                    logger.warning(f"⚠️ {test_case['description']}: Failed")
                    self.add_test_result(f"{test_name} - {test_case['description']}", False, result.get('error', 'Failed'))
                    
            except Exception as e:
                logger.error(f"❌ {test_case['description']} failed: {e}")
                self.add_test_result(f"{test_name} - {test_case['description']}", False, str(e))
    
    async def test_langchain_operations(self, driver_manager):
        """Test LangChain AI operations"""
        test_name = "LangChain AI Operations"
        logger.info(f"🔧 Testing: {test_name}")
        
        ai_tests = [
            {
                "node_type": "@n8n/n8n-nodes-langchain.lmChatOpenAi",
                "parameters": {
                    "prompt": "What is the capital of France?",
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.7
                },
                "description": "OpenAI Chat Completion"
            },
            {
                "node_type": "@n8n/n8n-nodes-langchain.agent",
                "parameters": {
                    "prompt": "Help me analyze this data",
                    "tools": ["web_search", "calculator"],
                    "agentType": "openai-functions"
                },
                "description": "LangChain Agent"
            },
            {
                "node_type": "@n8n/n8n-nodes-langchain.embeddingsOpenAi",
                "parameters": {
                    "text": "This is a test document for embedding generation",
                    "model": "text-embedding-ada-002"
                },
                "description": "OpenAI Embeddings"
            },
            {
                "node_type": "@n8n/n8n-nodes-langchain.memoryBufferWindow",
                "parameters": {
                    "sessionId": "test-session-123",
                    "windowSize": 10,
                    "operation": "get"
                },
                "description": "Memory Buffer"
            }
        ]
        
        for test_case in ai_tests:
            try:
                result = await driver_manager.execute_node(
                    test_case["node_type"], 
                    test_case["parameters"], 
                    {"input_data": [{}]}
                )
                
                if result.get('success'):
                    logger.info(f"✅ {test_case['description']}: Success")
                    self.add_test_result(f"{test_name} - {test_case['description']}", True, "Success")
                else:
                    logger.warning(f"⚠️ {test_case['description']}: Failed")
                    self.add_test_result(f"{test_name} - {test_case['description']}", False, result.get('error', 'Failed'))
                    
            except Exception as e:
                logger.error(f"❌ {test_case['description']} failed: {e}")
                self.add_test_result(f"{test_name} - {test_case['description']}", False, str(e))
    
    async def test_utility_operations(self, driver_manager):
        """Test utility operations"""
        test_name = "Utility Operations"
        logger.info(f"🔧 Testing: {test_name}")
        
        utility_tests = [
            {
                "node_type": "n8n-nodes-base.stickyNote",
                "parameters": {
                    "content": "This is a test note for documentation",
                    "color": "yellow"
                },
                "description": "Sticky Note"
            },
            {
                "node_type": "n8n-nodes-base.manualTrigger",
                "parameters": {
                    "data": {"trigger_source": "test"}
                },
                "description": "Manual Trigger"
            },
            {
                "node_type": "n8n-nodes-base.wait",
                "parameters": {
                    "amount": 1,
                    "unit": "seconds"
                },
                "description": "Wait Operation"
            },
            {
                "node_type": "n8n-nodes-base.noOp",
                "parameters": {},
                "description": "No Operation"
            }
        ]
        
        for test_case in utility_tests:
            try:
                result = await driver_manager.execute_node(
                    test_case["node_type"], 
                    test_case["parameters"], 
                    {"input_data": [{"test": "data"}]}
                )
                
                if result.get('success'):
                    logger.info(f"✅ {test_case['description']}: Success")
                    self.add_test_result(f"{test_name} - {test_case['description']}", True, "Success")
                else:
                    logger.warning(f"⚠️ {test_case['description']}: Failed")
                    self.add_test_result(f"{test_name} - {test_case['description']}", False, result.get('error', 'Failed'))
                    
            except Exception as e:
                logger.error(f"❌ {test_case['description']} failed: {e}")
                self.add_test_result(f"{test_name} - {test_case['description']}", False, str(e))
    
    async def test_workflow_scenarios(self, driver_manager):
        """Test complete workflow scenarios"""
        test_name = "Workflow Scenarios"
        logger.info(f"🔧 Testing: {test_name}")
        
        # Scenario 1: Data Processing Pipeline
        try:
            logger.info("📋 Testing Data Processing Pipeline...")
            
            # Step 1: Manual trigger
            trigger_result = await driver_manager.execute_node(
                "n8n-nodes-base.manualTrigger",
                {"data": {"source": "test_pipeline"}},
                {}
            )
            
            # Step 2: Set values
            set_result = await driver_manager.execute_node(
                "n8n-nodes-base.set",
                {"values": {"processed_at": "2024-01-01", "status": "processing"}},
                {"input_data": trigger_result.get("data", [])}
            )
            
            # Step 3: HTTP request
            http_result = await driver_manager.execute_node(
                "n8n-nodes-base.httpRequest",
                {"url": "https://jsonplaceholder.typicode.com/posts/1", "method": "GET"},
                {"input_data": set_result.get("data", [])}
            )
            
            if all([trigger_result.get('success'), set_result.get('success'), http_result.get('success')]):
                logger.info("✅ Data Processing Pipeline: Success")
                self.add_test_result(f"{test_name} - Data Processing Pipeline", True, "3-step pipeline successful")
            else:
                self.add_test_result(f"{test_name} - Data Processing Pipeline", False, "Pipeline step failed")
                
        except Exception as e:
            logger.error(f"❌ Data Processing Pipeline failed: {e}")
            self.add_test_result(f"{test_name} - Data Processing Pipeline", False, str(e))
        
        # Scenario 2: AI-Powered Analysis
        try:
            logger.info("📋 Testing AI-Powered Analysis...")
            
            # Step 1: Data preparation
            data_prep = await driver_manager.execute_node(
                "n8n-nodes-base.set",
                {"values": {"text": "Analyze this customer feedback: Great product, love it!"}},
                {"input_data": [{}]}
            )
            
            # Step 2: AI analysis
            ai_analysis = await driver_manager.execute_node(
                "@n8n/n8n-nodes-langchain.lmChatOpenAi",
                {"prompt": "Analyze sentiment and extract insights", "model": "gpt-3.5-turbo"},
                {"input_data": data_prep.get("data", [])}
            )
            
            # Step 3: Result processing
            result_processing = await driver_manager.execute_node(
                "n8n-nodes-base.set",
                {"values": {"analysis_complete": True, "timestamp": "2024-01-01"}},
                {"input_data": [ai_analysis]}
            )
            
            if all([data_prep.get('success'), ai_analysis.get('success'), result_processing.get('success')]):
                logger.info("✅ AI-Powered Analysis: Success")
                self.add_test_result(f"{test_name} - AI-Powered Analysis", True, "AI analysis pipeline successful")
            else:
                self.add_test_result(f"{test_name} - AI-Powered Analysis", False, "AI pipeline step failed")
                
        except Exception as e:
            logger.error(f"❌ AI-Powered Analysis failed: {e}")
            self.add_test_result(f"{test_name} - AI-Powered Analysis", False, str(e))
    
    async def test_error_handling(self, driver_manager):
        """Test error handling scenarios"""
        test_name = "Error Handling"
        logger.info(f"🔧 Testing: {test_name}")
        
        error_tests = [
            {
                "description": "Unsupported Node Type",
                "node_type": "non-existent-node-type",
                "parameters": {},
                "should_fail": True
            },
            {
                "description": "Missing Required Parameters",
                "node_type": "n8n-nodes-base.httpRequest",
                "parameters": {},  # Missing required url and method
                "should_fail": True
            },
            {
                "description": "Invalid HTTP URL",
                "node_type": "n8n-nodes-base.httpRequest",
                "parameters": {"url": "invalid-url", "method": "GET"},
                "should_fail": True
            }
        ]
        
        for test_case in error_tests:
            try:
                result = await driver_manager.execute_node(
                    test_case["node_type"], 
                    test_case["parameters"], 
                    {"input_data": [{}]}
                )
                
                if test_case["should_fail"]:
                    if not result.get('success'):
                        logger.info(f"✅ {test_case['description']}: Correctly failed")
                        self.add_test_result(f"{test_name} - {test_case['description']}", True, "Correctly handled error")
                    else:
                        logger.warning(f"⚠️ {test_case['description']}: Should have failed but succeeded")
                        self.add_test_result(f"{test_name} - {test_case['description']}", False, "Should have failed")
                else:
                    if result.get('success'):
                        logger.info(f"✅ {test_case['description']}: Success")
                        self.add_test_result(f"{test_name} - {test_case['description']}", True, "Success")
                    else:
                        logger.warning(f"⚠️ {test_case['description']}: Failed")
                        self.add_test_result(f"{test_name} - {test_case['description']}", False, result.get('error', 'Failed'))
                        
            except Exception as e:
                if test_case["should_fail"]:
                    logger.info(f"✅ {test_case['description']}: Correctly threw exception")
                    self.add_test_result(f"{test_name} - {test_case['description']}", True, "Correctly threw exception")
                else:
                    logger.error(f"❌ {test_case['description']} failed: {e}")
                    self.add_test_result(f"{test_name} - {test_case['description']}", False, str(e))
    
    def _get_test_parameters(self, node_type: str) -> Dict[str, Any]:
        """Get appropriate test parameters for a node type"""
        if node_type == 'n8n-nodes-base.httpRequest':
            return {"url": "https://api.github.com/repos/microsoft/vscode", "method": "GET"}
        elif node_type == 'n8n-nodes-base.set':
            return {"values": {"test_field": "test_value", "timestamp": "2024-01-01"}}
        elif node_type == 'n8n-nodes-base.if':
            return {"conditions": {"field": "status", "operator": "equals", "value": "active"}}
        elif node_type == 'n8n-nodes-base.stickyNote':
            return {"content": "Test note", "color": "yellow"}
        elif node_type == 'n8n-nodes-base.manualTrigger':
            return {"data": {"trigger_source": "test"}}
        else:
            return {}
    
    def add_test_result(self, test_name: str, passed: bool, details: str):
        """Add a test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
        
        self.test_results.append({
            "test_name": test_name,
            "passed": passed,
            "details": details
        })
    
    def generate_final_report(self):
        """Generate comprehensive test report"""
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        logger.info("=" * 80)
        logger.info("🎯 UNIVERSAL DRIVER SYSTEM TEST REPORT")
        logger.info("=" * 80)
        logger.info(f"📊 Total Tests: {self.total_tests}")
        logger.info(f"✅ Passed: {self.passed_tests}")
        logger.info(f"❌ Failed: {self.total_tests - self.passed_tests}")
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        logger.info("=" * 80)
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            category = result["test_name"].split(" - ")[0] if " - " in result["test_name"] else "General"
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "tests": []}
            
            if result["passed"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
            categories[category]["tests"].append(result)
        
        # Print category summaries
        for category, data in categories.items():
            total_cat = data["passed"] + data["failed"]
            cat_success_rate = (data["passed"] / total_cat * 100) if total_cat > 0 else 0
            
            logger.info(f"\n📂 {category}:")
            logger.info(f"   ✅ Passed: {data['passed']}")
            logger.info(f"   ❌ Failed: {data['failed']}")
            logger.info(f"   📈 Success Rate: {cat_success_rate:.1f}%")
            
            # Show failed tests
            failed_tests = [t for t in data["tests"] if not t["passed"]]
            if failed_tests:
                logger.info(f"   🔍 Failed Tests:")
                for test in failed_tests[:3]:  # Show first 3 failures
                    logger.info(f"      - {test['test_name']}: {test['details']}")
        
        logger.info("=" * 80)
        
        if success_rate >= 90:
            logger.info("🎉 EXCELLENT: Universal driver system is working great!")
        elif success_rate >= 75:
            logger.info("👍 GOOD: Universal driver system is mostly working well")
        elif success_rate >= 50:
            logger.info("⚠️ FAIR: Universal driver system needs some improvements")
        else:
            logger.info("❌ POOR: Universal driver system needs significant work")
        
        logger.info("=" * 80)
        
        # Save detailed report
        report_data = {
            "summary": {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.total_tests - self.passed_tests,
                "success_rate": success_rate
            },
            "categories": categories,
            "all_results": self.test_results
        }
        
        with open("universal_driver_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        logger.info("📄 Detailed report saved to: universal_driver_test_report.json")

async def main():
    """Main test execution"""
    tester = UniversalDriverSystemTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
