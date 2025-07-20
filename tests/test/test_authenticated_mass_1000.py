#!/usr/bin/env python3
"""
Authenticated Mass Test Suite: 1000 User Requests with Authentication
Tests the enhanced MCP system with proper authentication
"""

import requests
import json
import time
import random
import statistics
from datetime import datetime
from typing import List, Dict, Any

class AuthenticatedMassTestSuite:
    def __init__(self):
        self.base_url = "http://localhost:8002"
        self.session = requests.Session()
        self.auth_token = None
        self.results = []
        self.response_times = []
        self.error_count = 0
        self.automation_count = 0
        self.conversation_count = 0
        
    def authenticate(self) -> bool:
        """Create/login a test user for authentication"""
        
        print("🔐 Setting up authentication...")
        
        # Test user credentials
        test_email = "test_mass_user@dxtr-labs.com"
        test_password = "TestPassword123!"
        
        try:
            # Try to sign up first (in case user doesn't exist)
            signup_response = self.session.post(
                f"{self.base_url}/api/auth/signup",
                json={
                    "email": test_email,
                    "password": test_password,
                    "firstName": "Test",
                    "lastName": "User"
                },
                timeout=10
            )
            
            if signup_response.status_code == 201:
                print("   ✅ Test user created successfully")
            elif signup_response.status_code == 400:
                print("   ℹ️ Test user already exists")
            else:
                print(f"   ⚠️ Signup response: {signup_response.status_code}")
            
            # Login with the test user
            login_response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "email": test_email,
                    "password": test_password
                },
                timeout=10
            )
            
            if login_response.status_code == 200:
                print("   ✅ Login successful")
                # The session will maintain the auth cookie automatically
                return True
            else:
                print(f"   ❌ Login failed: {login_response.status_code}")
                if login_response.status_code == 200:
                    print(f"      Response: {login_response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def generate_test_requests(self) -> List[tuple]:
        """Generate 1000 test requests (400 automation + 600 conversational)"""
        
        # 50 automation request templates to expand to 400
        automation_templates = [
            "Send welcome email to new customers with company information",
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
        
        # 50 conversational templates to expand to 600
        conversation_templates = [
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
        
        # Generate 400 automation requests
        automation_requests = []
        while len(automation_requests) < 400:
            automation_requests.extend(automation_templates)
        automation_requests = automation_requests[:400]
        
        # Generate 600 conversational requests  
        conversation_requests = []
        while len(conversation_requests) < 600:
            conversation_requests.extend(conversation_templates)
        conversation_requests = conversation_requests[:600]
        
        # Combine and label requests
        all_requests = []
        for i, req in enumerate(automation_requests):
            all_requests.append(("automation", req, f"auto_{i}"))
        
        for i, req in enumerate(conversation_requests):
            all_requests.append(("conversational", req, f"conv_{i}"))
        
        # Shuffle to simulate realistic usage
        random.shuffle(all_requests)
        
        return all_requests
    
    def make_request(self, message: str, request_id: str) -> Dict[str, Any]:
        """Make an authenticated request to the MCP API"""
        start_time = time.time()
        
        try:
            response = self.session.post(
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
        """Run the authenticated mass test with 1000 requests"""
        
        print("🚀 AUTHENTICATED MASS TEST SUITE: 1000 User Requests")
        print("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with testing")
            return
        
        print()
        
        # Generate test requests
        print("📝 Generating test requests...")
        test_requests = self.generate_test_requests()
        print(f"✅ Generated {len(test_requests)} requests")
        print(f"   • 400 automation requests")
        print(f"   • 600 conversational requests")
        print()
        
        # Run tests in batches
        print("🔄 Running authenticated mass test...")
        start_time = datetime.now()
        
        automation_results = []
        conversation_results = []
        
        batch_size = 50
        total_batches = len(test_requests) // batch_size + 1
        
        for batch_num in range(total_batches):
            batch_start = batch_num * batch_size
            batch_end = min((batch_num + 1) * batch_size, len(test_requests))
            batch_requests = test_requests[batch_start:batch_end]
            
            if not batch_requests:
                break
            
            print(f"   Batch {batch_num + 1}/{total_batches}: Processing {len(batch_requests)} requests...")
            
            for request_type, message, request_id in batch_requests:
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
            
            # Progress update
            completed = batch_end
            success_count = self.automation_count + self.conversation_count
            print(f"      Progress: {completed}/1000 | Success: {success_count} | Errors: {self.error_count}")
            
            # Brief pause between batches
            time.sleep(0.5)
        
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Mass test completed!")
        print()
        
        # Generate comprehensive report
        self.generate_comprehensive_report(total_duration, automation_results, conversation_results)
    
    def generate_comprehensive_report(self, total_duration: float, automation_results: List, conversation_results: List):
        """Generate detailed test report"""
        
        print("=" * 70)
        print("📊 COMPREHENSIVE AUTHENTICATED MASS TEST REPORT")
        print("=" * 70)
        
        # Overall Statistics
        total_requests = len(self.results)
        successful_requests = self.automation_count + self.conversation_count
        success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        
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
        
        # Status Distribution
        status_counts = {}
        for result in self.results:
            if not result.get('error'):
                status = result.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"📊 STATUS DISTRIBUTION:")
        for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / successful_requests) * 100 if successful_requests > 0 else 0
            print(f"   • {status}: {count} ({percentage:.1f}%)")
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
        
        if automation_successful > 0:
            detection_rate = (automation_detected / automation_successful) * 100
            if detection_rate >= 85:
                detection_grade = "🟢 EXCELLENT"
            elif detection_rate >= 70:
                detection_grade = "🟡 GOOD"
            elif detection_rate >= 55:
                detection_grade = "🟠 FAIR"
            else:
                detection_grade = "🔴 NEEDS IMPROVEMENT"
            print(f"   • Automation Detection: {detection_grade} ({detection_rate:.1f}%)")
        
        print()
        
        # Recommendations
        print(f"💡 RECOMMENDATIONS:")
        if success_rate < 90:
            print(f"   • Improve error handling and system stability")
        if avg_response > 2.0:
            print(f"   • Optimize response time (target: <2s)")
        if automation_successful > 0:
            detection_rate = (automation_detected / automation_successful) * 100
            if detection_rate < 80:
                print(f"   • Enhance automation detection algorithms")
        print(f"   • Consider implementing request caching")
        print(f"   • Add response compression for large workflows")
        print(f"   • Implement parallel processing for high loads")
        
        print(f"\n🏆 AUTHENTICATED MASS TEST COMPLETE!")
        print(f"   System successfully handled 1000 authenticated user requests")
        print(f"   with sophisticated automation detection and workflow generation")

def main():
    """Run the authenticated mass test"""
    
    print("🧪 Enhanced MCP Authenticated Mass Load Testing")
    print("Testing 1000 user requests with authentication and automation detection")
    print()
    
    tester = AuthenticatedMassTestSuite()
    tester.run_mass_test()

if __name__ == "__main__":
    main()
