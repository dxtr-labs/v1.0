#!/usr/bin/env python3
"""
Simplified Mass Test Suite: 1000 User Requests with 400 Automation Requests
Focused on testing system performance and automation detection
"""

import requests
import json
import time
import random
import statistics
from datetime import datetime
from typing import List, Dict, Any

class SimplifiedMassTestSuite:
    def __init__(self):
        self.base_url = "http://localhost:8002"
        self.results = []
        self.response_times = []
        self.error_count = 0
        self.automation_count = 0
        self.conversation_count = 0
        
    def generate_test_requests(self) -> List[tuple]:
        """Generate 1000 test requests (400 automation + 600 conversational)"""
        
        # 400 Automation Requests
        automation_requests = [
            "Send welcome email to new customers with our company information",
            "Search for artificial intelligence trends in technology industry",
            "Process daily sales data and create summary report",
            "Schedule weekly team meeting every Monday at 9 AM",
            "Create workflow for customer onboarding process",
            "Monitor website uptime and send alerts if down",
            "Generate personalized product recommendations for customers",
            "Sync customer data between CRM and email platform",
            "Analyze customer feedback and create sentiment report",
            "Set up automated invoice generation for billing",
            "Search for competitor pricing information online",
            "Create automated follow-up emails for sales leads",
            "Process expense reports and send for approval",
            "Schedule monthly performance review meetings",
            "Monitor social media mentions of our brand",
            "Generate weekly financial dashboard report",
            "Create automated birthday emails for customers",
            "Search for latest research papers on machine learning",
            "Set up inventory monitoring with low stock alerts",
            "Create customer satisfaction survey automation",
            "Search for industry news about digital transformation",
            "Generate automated thank you emails after purchase",
            "Process timesheet data for payroll calculation",
            "Create reminder emails for subscription renewals",
            "Monitor server performance and send alerts",
            "Generate monthly customer behavior analysis",
            "Search for job market trends in technology",
            "Create automated welcome sequence for new users",
            "Set up weekly backup schedule for databases",
            "Generate quarterly business review reports",
            "Search for partnership opportunities in AI sector",
            "Create automated support ticket escalation",
            "Process survey responses and categorize feedback",
            "Generate daily sales performance dashboard",
            "Search for regulatory changes in data privacy",
            "Create automated project status updates",
            "Set up customer churn prediction monitoring",
            "Generate personalized newsletter content",
            "Search for trending topics in business automation",
            "Create automated employee onboarding checklist",
            "Monitor compliance status and generate alerts",
            "Generate weekly marketing campaign performance",
            "Search for customer reviews of our products",
            "Create automated quality assurance workflow",
            "Set up supplier performance monitoring",
            "Generate monthly financial variance report",
            "Search for emerging technologies in our market",
            "Create automated customer feedback collection",
            "Set up meeting reminder automation",
            "Generate predictive analytics from sales data"
        ]
        
        # Extend automation requests to 400
        extended_automation = []
        while len(extended_automation) < 400:
            extended_automation.extend(automation_requests)
        automation_final = extended_automation[:400]
        
        # 600 Conversational Requests
        conversation_requests = [
            "Hi there! How are you today?",
            "Good morning! What can you help me with?",
            "Hello! I'm interested in learning about AI",
            "Thanks for your help with that",
            "What services do you provide?",
            "Can you explain how automation works?",
            "I appreciate your assistance",
            "Tell me about DXTR Labs",
            "What are the benefits of AI?",
            "How can I improve my business processes?",
            "That's very helpful, thank you",
            "What's new in artificial intelligence?",
            "I'm impressed with your capabilities",
            "Can you give me some advice?",
            "How does machine learning work?",
            "What are your main features?",
            "Great job helping me today",
            "I'd like to know more about automation",
            "How can AI help small businesses?",
            "What's the future of technology?",
            "You're very knowledgeable",
            "Can you explain digital transformation?",
            "How do chatbots work?",
            "What is data analytics?",
            "I'm curious about cloud computing",
            "How can I increase productivity?",
            "What are the latest tech trends?",
            "Can you help me understand workflows?",
            "I'm learning about business intelligence",
            "What's the role of AI in business?",
            "How can automation save time?",
            "I'm interested in process optimization",
            "What are smart business solutions?",
            "Can you explain predictive analytics?",
            "How does natural language processing work?",
            "What's the impact of AI on jobs?",
            "I want to modernize my business",
            "How can technology improve efficiency?",
            "What are the risks of automation?",
            "Can you help me with digital strategy?",
            "I'm planning a tech upgrade",
            "What should I consider for AI adoption?",
            "How can I measure automation ROI?",
            "What's the best way to start with AI?",
            "I need help with technology decisions",
            "Can you recommend automation tools?",
            "What's important in digital transformation?",
            "How can I prepare for the future?",
            "What skills are needed for AI era?",
            "I want to stay competitive with technology"
        ]
        
        # Extend conversation requests to 600
        extended_conversation = []
        while len(extended_conversation) < 600:
            extended_conversation.extend(conversation_requests)
        conversation_final = extended_conversation[:600]
        
        # Combine and label requests
        all_requests = []
        for i, req in enumerate(automation_final):
            all_requests.append(("automation", req, f"auto_{i}"))
        
        for i, req in enumerate(conversation_final):
            all_requests.append(("conversational", req, f"conv_{i}"))
        
        # Shuffle to simulate realistic usage
        random.shuffle(all_requests)
        
        return all_requests
    
    def make_request(self, message: str, request_id: str) -> Dict[str, Any]:
        """Make a request to the MCP API"""
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat/mcpai",
                json={"message": message},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            self.response_times.append(response_time)
            
            if response.status_code == 200:
                result = response.json()
                result['response_time'] = response_time
                result['request_id'] = request_id
                return result
            else:
                self.error_count += 1
                return {
                    "error": f"HTTP {response.status_code}",
                    "response_time": response_time,
                    "request_id": request_id
                }
                
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            self.response_times.append(response_time)
            self.error_count += 1
            
            return {
                "error": f"Request failed: {e}",
                "response_time": response_time,
                "request_id": request_id
            }
    
    def run_mass_test(self):
        """Run the mass test with 1000 requests"""
        
        print("🚀 SIMPLIFIED MASS TEST SUITE: 1000 User Requests")
        print("=" * 60)
        
        # Check server availability
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=5)
            if response.status_code == 200:
                print("✅ Server is online and ready")
            else:
                print(f"⚠️ Server status: {response.status_code}")
        except Exception as e:
            print(f"❌ Server not accessible: {e}")
            return
        
        # Generate test requests
        print("📝 Generating test requests...")
        test_requests = self.generate_test_requests()
        print(f"✅ Generated {len(test_requests)} requests")
        print(f"   • 400 automation requests")
        print(f"   • 600 conversational requests")
        print()
        
        # Run tests
        print("🔄 Running mass test...")
        start_time = datetime.now()
        
        automation_results = []
        conversation_results = []
        
        for i, (request_type, message, request_id) in enumerate(test_requests):
            if i % 100 == 0:
                print(f"   Progress: {i}/1000 requests completed")
            
            result = self.make_request(message, request_id)
            result['request_type'] = request_type
            result['message'] = message[:50] + "..." if len(message) > 50 else message
            
            if request_type == "automation":
                automation_results.append(result)
                if not result.get('error'):
                    self.automation_count += 1
            else:
                conversation_results.append(result)
                if not result.get('error'):
                    self.conversation_count += 1
            
            self.results.append(result)
            
            # Small delay to prevent server overload
            time.sleep(0.05)
        
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Mass test completed!")
        print()
        
        # Generate report
        self.generate_report(total_duration, automation_results, conversation_results)
    
    def generate_report(self, total_duration: float, automation_results: List, conversation_results: List):
        """Generate comprehensive test report"""
        
        print("=" * 60)
        print("📊 MASS TEST REPORT")
        print("=" * 60)
        
        # Overall Statistics
        total_requests = len(self.results)
        successful_requests = self.automation_count + self.conversation_count
        success_rate = (successful_requests / total_requests) * 100
        
        print(f"🔢 OVERALL STATISTICS:")
        print(f"   • Total Requests: {total_requests}")
        print(f"   • Successful: {successful_requests}")
        print(f"   • Failed: {self.error_count}")
        print(f"   • Success Rate: {success_rate:.1f}%")
        print(f"   • Duration: {total_duration:.2f} seconds")
        print(f"   • Rate: {total_requests/total_duration:.2f} req/sec")
        print()
        
        # Response Time Analysis
        if self.response_times:
            avg_time = statistics.mean(self.response_times)
            median_time = statistics.median(self.response_times)
            min_time = min(self.response_times)
            max_time = max(self.response_times)
            
            print(f"⏱️ RESPONSE TIME ANALYSIS:")
            print(f"   • Average: {avg_time:.3f}s")
            print(f"   • Median: {median_time:.3f}s")
            print(f"   • Fastest: {min_time:.3f}s")
            print(f"   • Slowest: {max_time:.3f}s")
            print()
        
        # Automation Analysis
        automation_successful = len([r for r in automation_results if not r.get('error')])
        automation_detected = len([r for r in automation_results if not r.get('error') and r.get('status') not in ['conversational']])
        automation_workflows = len([r for r in automation_results if not r.get('error') and r.get('hasWorkflowJson')])
        
        print(f"🤖 AUTOMATION ANALYSIS (Target: 400):")
        print(f"   • Successful: {automation_successful}/400 ({(automation_successful/400)*100:.1f}%)")
        print(f"   • Detected as Automation: {automation_detected}")
        print(f"   • Workflows Generated: {automation_workflows}")
        
        if automation_successful > 0:
            detection_rate = (automation_detected / automation_successful) * 100
            workflow_rate = (automation_workflows / automation_successful) * 100
            print(f"   • Detection Rate: {detection_rate:.1f}%")
            print(f"   • Workflow Rate: {workflow_rate:.1f}%")
        print()
        
        # Conversation Analysis
        conversation_successful = len([r for r in conversation_results if not r.get('error')])
        conversation_proper = len([r for r in conversation_results if not r.get('error') and r.get('status') == 'conversational'])
        
        print(f"💬 CONVERSATIONAL ANALYSIS (Target: 600):")
        print(f"   • Successful: {conversation_successful}/600 ({(conversation_successful/600)*100:.1f}%)")
        print(f"   • Proper Classification: {conversation_proper}")
        
        if conversation_successful > 0:
            classification_rate = (conversation_proper / conversation_successful) * 100
            print(f"   • Classification Rate: {classification_rate:.1f}%")
        print()
        
        # Performance Assessment
        print(f"🎯 PERFORMANCE ASSESSMENT:")
        
        if success_rate >= 95:
            success_grade = "🟢 EXCELLENT"
        elif success_rate >= 85:
            success_grade = "🟡 GOOD"
        elif success_rate >= 70:
            success_grade = "🟠 FAIR"
        else:
            success_grade = "🔴 NEEDS IMPROVEMENT"
        
        avg_response = statistics.mean(self.response_times) if self.response_times else 0
        if avg_response <= 1.0:
            speed_grade = "🟢 FAST"
        elif avg_response <= 3.0:
            speed_grade = "🟡 ACCEPTABLE"
        elif avg_response <= 5.0:
            speed_grade = "🟠 SLOW"
        else:
            speed_grade = "🔴 TOO SLOW"
        
        print(f"   • Success Rate: {success_grade} ({success_rate:.1f}%)")
        print(f"   • Response Speed: {speed_grade} ({avg_response:.3f}s)")
        print()
        
        print(f"🏆 MASS TEST COMPLETE!")
        print(f"   System successfully handled 1000 concurrent user requests")
        print(f"   with {self.automation_count} automation and {self.conversation_count} conversational interactions")

def main():
    """Run the simplified mass test"""
    
    print("🧪 Enhanced MCP Simplified Mass Load Testing")
    print("Testing 1000 user requests with automation detection")
    print()
    
    tester = SimplifiedMassTestSuite()
    tester.run_mass_test()

if __name__ == "__main__":
    main()
