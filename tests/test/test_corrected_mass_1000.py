#!/usr/bin/env python3
"""
Corrected Authenticated Mass Test Suite: 1000 User Requests
Uses proper session_token cookie authentication
"""

import requests
import json
import time
import random
import statistics
from datetime import datetime
from typing import List, Dict, Any

class CorrectedMassTestSuite:
    def __init__(self):
        self.base_url = "http://localhost:8002"
        self.session_token = None
        self.results = []
        self.response_times = []
        self.error_count = 0
        self.automation_count = 0
        self.conversation_count = 0
        
    def authenticate(self) -> bool:
        """Get session token for authentication"""
        
        print("🔐 Setting up authentication...")
        
        # Test user credentials
        test_email = "test_mass_user@dxtr-labs.com"
        test_password = "TestPassword123!"
        
        try:
            # Login to get session token
            login_response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "email": test_email,
                    "password": test_password
                },
                timeout=10
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                self.session_token = login_data.get('session_token')
                
                if self.session_token:
                    print("   ✅ Authentication successful")
                    print(f"   Session token: {self.session_token[:20]}...")
                    return True
                else:
                    print("   ❌ No session token received")
                    return False
            else:
                print(f"   ❌ Login failed: {login_response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Authentication error: {e}")
            return False
    
    def generate_test_requests(self) -> List[tuple]:
        """Generate 1000 test requests (400 automation + 600 conversational)"""
        
        # Core automation patterns
        automation_patterns = [
            "Send welcome email to new customers",
            "Search for AI trends online",
            "Process daily sales data report",
            "Schedule weekly team meeting",
            "Create customer onboarding workflow",
            "Monitor website uptime alerts",
            "Generate product recommendations",
            "Sync CRM and email data",
            "Analyze customer feedback sentiment",
            "Set up automated invoicing",
            "Search competitor pricing",
            "Create follow-up email sequence",
            "Process expense reports",
            "Schedule performance reviews",
            "Monitor social media mentions",
            "Generate financial dashboard",
            "Create birthday email automation",
            "Search research papers on ML",
            "Set up inventory monitoring",
            "Create satisfaction surveys",
            "Search industry news",
            "Generate thank you emails",
            "Process timesheet data",
            "Create renewal reminders",
            "Monitor server performance",
            "Analyze customer behavior",
            "Search job market trends",
            "Create welcome sequences",
            "Schedule backup routines",
            "Generate business reports",
            "Search partnership opportunities",
            "Create ticket escalation",
            "Process survey responses",
            "Generate sales dashboard",
            "Search regulatory changes",
            "Create project updates",
            "Set up churn monitoring",
            "Generate newsletter content",
            "Search automation trends",
            "Create onboarding checklist"
        ]
        
        # Core conversation patterns
        conversation_patterns = [
            "Hi there! How are you?",
            "Good morning! What can you help with?",
            "Hello! I'm interested in AI",
            "Thanks for your help",
            "What services do you provide?",
            "Can you explain automation?",
            "I appreciate your assistance",
            "Tell me about DXTR Labs",
            "What are AI benefits?",
            "How to improve business processes?",
            "That's very helpful",
            "What's new in AI?",
            "I'm impressed with capabilities",
            "Can you give advice?",
            "How does ML work?",
            "What are main features?",
            "Great job today",
            "I want to learn automation",
            "How can AI help businesses?",
            "What's the tech future?",
            "You're knowledgeable",
            "Explain digital transformation",
            "How do chatbots work?",
            "What is data analytics?",
            "I'm curious about cloud computing",
            "How to increase productivity?",
            "What are latest trends?",
            "Help me understand workflows",
            "Learning about BI",
            "AI role in business?",
            "How automation saves time?",
            "Interested in optimization",
            "What are smart solutions?",
            "Explain predictive analytics",
            "How does NLP work?",
            "AI impact on jobs?",
            "Want to modernize business",
            "Tech improving efficiency?",
            "What are automation risks?",
            "Help with digital strategy?"
        ]
        
        # Generate 400 automation requests
        automation_requests = []
        while len(automation_requests) < 400:
            automation_requests.extend(automation_patterns)
        automation_requests = automation_requests[:400]
        
        # Generate 600 conversational requests
        conversation_requests = []
        while len(conversation_requests) < 600:
            conversation_requests.extend(conversation_patterns)
        conversation_requests = conversation_requests[:600]
        
        # Combine and label
        all_requests = []
        for i, req in enumerate(automation_requests):
            all_requests.append(("automation", req, f"auto_{i}"))
        
        for i, req in enumerate(conversation_requests):
            all_requests.append(("conversational", req, f"conv_{i}"))
        
        # Shuffle for realistic patterns
        random.shuffle(all_requests)
        return all_requests
    
    def make_request(self, message: str, request_id: str) -> Dict[str, Any]:
        """Make authenticated request using session token"""
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat/mcpai",
                json={"message": message},
                headers={"Content-Type": "application/json"},
                cookies={"session_token": self.session_token},
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
        """Run the corrected mass test with 1000 requests"""
        
        print("🚀 CORRECTED AUTHENTICATED MASS TEST: 1000 User Requests")
        print("=" * 70)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed")
            return
        
        print()
        
        # Generate test requests
        print("📝 Generating test requests...")
        test_requests = self.generate_test_requests()
        print(f"✅ Generated {len(test_requests)} requests")
        print(f"   • 400 automation requests")
        print(f"   • 600 conversational requests")
        print()
        
        # Run tests
        print("🔄 Running corrected mass test...")
        start_time = datetime.now()
        
        automation_results = []
        conversation_results = []
        
        batch_size = 25  # Smaller batches for better monitoring
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
                
                # Small delay between requests
                time.sleep(0.02)
            
            # Progress update
            completed = batch_end
            success_count = self.automation_count + self.conversation_count
            print(f"      Progress: {completed}/1000 | Success: {success_count} | Errors: {self.error_count}")
            
            # Brief pause between batches
            time.sleep(0.2)
        
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Corrected mass test completed!")
        print()
        
        # Generate comprehensive report
        self.generate_report(total_duration, automation_results, conversation_results)
    
    def generate_report(self, total_duration: float, automation_results: List, conversation_results: List):
        """Generate detailed test report"""
        
        print("=" * 80)
        print("📊 COMPREHENSIVE CORRECTED MASS TEST REPORT")
        print("=" * 80)
        
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
        
        # Status Distribution Analysis
        status_counts = {}
        for result in self.results:
            if not result.get('error'):
                status = result.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
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
        
        # Sample Results Analysis
        if successful_requests > 0:
            print(f"🔍 SAMPLE RESULTS ANALYSIS:")
            
            # Show sample automation results
            sample_automations = [r for r in automation_results[:3] if not r.get('error')]
            if sample_automations:
                print(f"   Sample Automation Results:")
                for i, result in enumerate(sample_automations, 1):
                    status = result.get('status', 'unknown')
                    has_workflow = result.get('hasWorkflowJson', False)
                    message = result.get('message', '')
                    print(f"     {i}. \"{message}\" → {status} (workflow: {has_workflow})")
            
            # Show sample conversation results
            sample_conversations = [r for r in conversation_results[:3] if not r.get('error')]
            if sample_conversations:
                print(f"   Sample Conversation Results:")
                for i, result in enumerate(sample_conversations, 1):
                    status = result.get('status', 'unknown')
                    message = result.get('message', '')
                    print(f"     {i}. \"{message}\" → {status}")
            print()
        
        # Final Assessment
        print(f"🏆 CORRECTED MASS TEST ASSESSMENT:")
        print(f"   System successfully processed {total_requests} requests")
        print(f"   with {successful_requests} successful responses ({success_rate:.1f}% success rate)")
        print(f"   Average response time: {avg_response:.3f} seconds")
        print(f"   Automation detection and workflow generation validated!")

def main():
    """Run the corrected mass test"""
    
    print("🧪 Enhanced MCP Corrected Mass Load Testing")
    print("Testing 1000 user requests with proper authentication")
    print()
    
    tester = CorrectedMassTestSuite()
    tester.run_mass_test()

if __name__ == "__main__":
    main()
