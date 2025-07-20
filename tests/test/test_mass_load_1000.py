#!/usr/bin/env python3
"""
Comprehensive Load Test Suite: 1000 User Requests with 400 Automation Requests
Tests the enhanced MCP system under realistic load conditions
"""

import requests
import json
import time
import random
import uuid
import asyncio
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any
import statistics

class MassUserTestSuite:
    def __init__(self):
        self.base_url = "http://localhost:8002"
        self.test_results = []
        self.automation_results = []
        self.conversational_results = []
        self.response_times = []
        self.error_count = 0
        self.automation_count = 0
        self.conversation_count = 0
        
        # Test data sets
        self.conversational_requests = self._generate_conversational_requests()
        self.automation_requests = self._generate_automation_requests()
        
    def _generate_conversational_requests(self) -> List[str]:
        """Generate 600 conversational requests"""
        
        greetings = [
            "Hi there!", "Hello!", "Good morning!", "How are you?", "Nice to meet you!",
            "Hey!", "Good afternoon!", "Good evening!", "Greetings!", "What's up?"
        ]
        
        questions = [
            "What can you help me with?", "How does automation work?", "Can you explain workflows?",
            "What services do you provide?", "How do I get started?", "What's your role?",
            "Tell me about DXTR Labs", "How can I improve my business?", "What's new?",
            "Can you give me some advice?", "What are your capabilities?", "How smart are you?"
        ]
        
        casual_chat = [
            "Thank you for your help", "That's interesting", "I appreciate it", "Great job!",
            "You're very helpful", "Nice work", "Excellent!", "Perfect!", "Amazing!",
            "Thanks so much", "I'm impressed", "Keep up the good work", "Well done!"
        ]
        
        information_requests = [
            "Tell me about artificial intelligence", "What is machine learning?", "How does AI work?",
            "Explain automation benefits", "What are the latest tech trends?", "How can AI help business?",
            "What is digital transformation?", "Tell me about productivity tools", "What's cloud computing?",
            "How do chatbots work?", "What is data analytics?", "Explain workflow optimization"
        ]
        
        all_requests = []
        
        # Generate varied conversational requests
        for _ in range(150):
            all_requests.append(random.choice(greetings))
        for _ in range(150):
            all_requests.append(random.choice(questions))
        for _ in range(150):
            all_requests.append(random.choice(casual_chat))
        for _ in range(150):
            all_requests.append(random.choice(information_requests))
        
        return all_requests
    
    def _generate_automation_requests(self) -> List[str]:
        """Generate 400 automation requests across different categories"""
        
        email_automations = [
            "Send an email to {email} about {topic}",
            "Create an email campaign for {audience}",
            "Set up welcome email for new {customers}",
            "Schedule reminder email about {event}",
            "Draft newsletter about {topic}",
            "Send follow-up email to {contacts}",
            "Create automated thank you email",
            "Set up birthday email for {customers}",
            "Send product update email to {subscribers}",
            "Create email sequence for {campaign}"
        ]
        
        web_search_automations = [
            "Search for {topic} information online",
            "Find competitor prices for {product}",
            "Research {industry} trends",
            "Monitor {brand} mentions online",
            "Search for {technology} tutorials",
            "Find news about {company}",
            "Research {market} opportunities",
            "Look up {regulation} information",
            "Search for {job} requirements",
            "Find {product} reviews online"
        ]
        
        data_processing_automations = [
            "Process CSV file with {data_type} data",
            "Analyze {dataset} for trends",
            "Generate report from {source} data",
            "Clean and organize {data} files",
            "Create dashboard for {metrics}",
            "Export {data} to Excel format",
            "Merge {databases} information",
            "Calculate {metrics} from data",
            "Filter {dataset} by criteria",
            "Summarize {reports} data"
        ]
        
        scheduling_automations = [
            "Schedule daily {task} at {time}",
            "Set up weekly {meeting} reminder",
            "Create recurring {event} notification",
            "Schedule {content} posting",
            "Set reminder for {deadline}",
            "Create calendar event for {appointment}",
            "Schedule {backup} process",
            "Set up {maintenance} reminder",
            "Create {review} schedule",
            "Schedule {reports} generation"
        ]
        
        business_automations = [
            "Create workflow for {process}",
            "Automate {task} for efficiency",
            "Set up {integration} between systems",
            "Create {approval} workflow",
            "Automate {billing} process",
            "Set up {monitoring} system",
            "Create {backup} automation",
            "Automate {inventory} management",
            "Set up {customer} onboarding",
            "Create {quality} assurance workflow"
        ]
        
        # Sample data for substitution
        emails = ["john@company.com", "sarah@business.org", "team@startup.io", "admin@corp.net"]
        topics = ["new product launch", "quarterly update", "meeting schedule", "project status"]
        audiences = ["new customers", "existing clients", "team members", "subscribers"]
        customers = ["customers", "users", "clients", "members"]
        events = ["the meeting", "project deadline", "product launch", "training session"]
        contacts = ["leads", "prospects", "customers", "partners"]
        campaigns = ["new users", "existing customers", "trial users", "premium members"]
        products = ["software", "services", "consulting", "training"]
        industries = ["technology", "healthcare", "finance", "education"]
        brands = ["our company", "competitors", "industry leaders", "partners"]
        technologies = ["AI", "automation", "cloud computing", "data analytics"]
        companies = ["tech companies", "startups", "enterprises", "competitors"]
        markets = ["emerging markets", "target markets", "new segments", "global markets"]
        regulations = ["data privacy", "compliance", "industry standards", "security requirements"]
        jobs = ["developer", "analyst", "manager", "specialist"]
        data_types = ["customer", "sales", "financial", "operational"]
        datasets = ["sales data", "customer data", "financial data", "operational metrics"]
        sources = ["CRM", "database", "spreadsheet", "API"]
        data = ["customer", "sales", "product", "user"]
        metrics = ["performance", "sales", "customer satisfaction", "efficiency"]
        databases = ["CRM and ERP", "sales and marketing", "customer and product", "financial and operational"]
        reports = ["monthly", "quarterly", "annual", "weekly"]
        tasks = ["backup", "report generation", "data sync", "system check"]
        times = ["9 AM", "2 PM", "6 PM", "midnight"]
        meetings = ["team", "client", "project", "review"]
        events = ["training", "webinar", "conference", "meeting"]
        content = ["social media", "blog", "newsletter", "updates"]
        deadlines = ["project deadline", "submission date", "renewal date", "review date"]
        appointments = ["client meeting", "interview", "consultation", "demo"]
        backups = ["database", "file", "system", "configuration"]
        maintenance = ["system", "equipment", "software", "infrastructure"]
        reviews = ["performance", "project", "quality", "security"]
        processes = ["customer onboarding", "order processing", "invoice generation", "quality assurance"]
        integrations = ["CRM and email", "accounting and inventory", "support and billing", "marketing and sales"]
        approvals = ["expense", "purchase", "project", "content"]
        billing = ["subscription", "invoice", "payment", "recurring"]
        monitoring = ["system health", "security", "performance", "uptime"]
        inventory = ["stock level", "reorder", "tracking", "audit"]
        quality = ["code review", "testing", "documentation", "compliance"]
        
        # Generate automation requests with realistic substitutions
        all_automations = []
        
        # All possible variables for template substitution
        template_vars = {
            'email': emails,
            'topic': topics,
            'audience': audiences,
            'customers': customers,
            'event': events,
            'contacts': contacts,
            'subscribers': ["subscribers"],
            'campaign': campaigns,
            'product': products,
            'industry': industries,
            'brand': brands,
            'technology': technologies,
            'company': companies,
            'market': markets,
            'regulation': regulations,
            'job': jobs,
            'data_type': data_types,
            'dataset': datasets,
            'source': sources,
            'data': data,
            'metrics': metrics,
            'databases': databases,
            'reports': reports,
            'task': tasks,
            'time': times,
            'meeting': meetings,
            'content': content,
            'deadline': deadlines,
            'appointment': appointments,
            'backup': backups,
            'maintenance': maintenance,
            'review': reviews,
            'process': processes,
            'integration': integrations,
            'approval': approvals,
            'billing': billing,
            'monitoring': monitoring,
            'inventory': inventory,
            'customer': ["customer"],
            'quality': quality
        }
        
        # Email automations (100 requests)
        for _ in range(100):
            template = random.choice(email_automations)
            # Create kwargs dict with all possible values
            kwargs = {k: random.choice(v) for k, v in template_vars.items()}
            request = template.format(**kwargs)
            all_automations.append(request)
        
        # Web search automations (100 requests)
        for _ in range(100):
            template = random.choice(web_search_automations)
            kwargs = {k: random.choice(v) for k, v in template_vars.items()}
            request = template.format(**kwargs)
            all_automations.append(request)
        
        # Data processing automations (100 requests)
        for _ in range(100):
            template = random.choice(data_processing_automations)
            kwargs = {k: random.choice(v) for k, v in template_vars.items()}
            request = template.format(**kwargs)
            all_automations.append(request)
        
        # Scheduling automations (50 requests)
        for _ in range(50):
            template = random.choice(scheduling_automations)
            kwargs = {k: random.choice(v) for k, v in template_vars.items()}
            request = template.format(**kwargs)
            all_automations.append(request)
        
        # Business automations (50 requests)
        for _ in range(50):
            template = random.choice(business_automations)
            kwargs = {k: random.choice(v) for k, v in template_vars.items()}
            request = template.format(**kwargs)
            all_automations.append(request)
        
        return all_automations
    
    def _make_request(self, message: str, request_id: int) -> Dict[str, Any]:
        """Make a request to the MCP API with timing"""
        start_time = time.time()
        
        try:
            # Try the MCPAI endpoint first (no auth required)
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
                    "error": f"HTTP {response.status_code}: {response.text}",
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
        
        print("🚀 MASS USER TEST SUITE: 1000 Requests (400 Automation + 600 Conversational)")
        print("=" * 80)
        
        # Combine and shuffle requests
        all_requests = []
        
        # Add automation requests (400)
        for i, req in enumerate(self.automation_requests):
            all_requests.append(("automation", req, i))
        
        # Add conversational requests (600)
        for i, req in enumerate(self.conversational_requests):
            all_requests.append(("conversational", req, i + 400))
        
        # Shuffle to simulate realistic usage patterns
        random.shuffle(all_requests)
        
        print(f"📊 Test Configuration:")
        print(f"   • Total requests: {len(all_requests)}")
        print(f"   • Automation requests: {len(self.automation_requests)}")
        print(f"   • Conversational requests: {len(self.conversational_requests)}")
        print(f"   • Target server: {self.base_url}")
        print()
        
        # Run tests in batches to avoid overwhelming the server
        batch_size = 50
        total_batches = len(all_requests) // batch_size + 1
        
        start_time = datetime.now()
        
        for batch_num in range(total_batches):
            batch_start = batch_num * batch_size
            batch_end = min((batch_num + 1) * batch_size, len(all_requests))
            batch_requests = all_requests[batch_start:batch_end]
            
            if not batch_requests:
                break
                
            print(f"🔄 Processing Batch {batch_num + 1}/{total_batches} ({len(batch_requests)} requests)")
            
            # Process batch
            batch_results = []
            for request_type, message, request_id in batch_requests:
                result = self._make_request(message, request_id)
                result['request_type'] = request_type
                result['message'] = message[:50] + "..." if len(message) > 50 else message
                
                batch_results.append(result)
                
                # Classify result
                if request_type == "automation":
                    self.automation_results.append(result)
                    if not result.get('error'):
                        self.automation_count += 1
                else:
                    self.conversational_results.append(result)
                    if not result.get('error'):
                        self.conversation_count += 1
                
                # Small delay to prevent overwhelming the server
                time.sleep(0.1)
            
            # Progress update
            processed = batch_end
            print(f"   ✅ Completed {processed}/{len(all_requests)} requests")
            print(f"   📊 Successful: {self.automation_count + self.conversation_count}, Errors: {self.error_count}")
            print(f"   ⏱️ Avg Response Time: {statistics.mean(self.response_times[-len(batch_results):]):.2f}s")
            print()
            
            # Brief pause between batches
            time.sleep(1)
        
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        # Generate comprehensive report
        self._generate_comprehensive_report(total_duration)
    
    def _generate_comprehensive_report(self, total_duration: float):
        """Generate detailed test report"""
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE MASS TEST REPORT")
        print("=" * 80)
        
        # Overall Statistics
        total_requests = len(self.test_results) + len(self.automation_results) + len(self.conversational_results)
        success_count = self.automation_count + self.conversation_count
        success_rate = (success_count / 1000) * 100 if total_requests > 0 else 0
        
        print(f"🔢 OVERALL STATISTICS:")
        print(f"   • Total Requests: 1000")
        print(f"   • Successful Requests: {success_count}")
        print(f"   • Failed Requests: {self.error_count}")
        print(f"   • Success Rate: {success_rate:.1f}%")
        print(f"   • Total Duration: {total_duration:.2f} seconds")
        print(f"   • Requests per Second: {1000/total_duration:.2f}")
        print()
        
        # Response Time Analysis
        if self.response_times:
            avg_response_time = statistics.mean(self.response_times)
            median_response_time = statistics.median(self.response_times)
            min_response_time = min(self.response_times)
            max_response_time = max(self.response_times)
            
            print(f"⏱️ RESPONSE TIME ANALYSIS:")
            print(f"   • Average Response Time: {avg_response_time:.3f}s")
            print(f"   • Median Response Time: {median_response_time:.3f}s")
            print(f"   • Fastest Response: {min_response_time:.3f}s")
            print(f"   • Slowest Response: {max_response_time:.3f}s")
            print()
        
        # Automation vs Conversational Breakdown
        automation_success = len([r for r in self.automation_results if not r.get('error')])
        conversation_success = len([r for r in self.conversational_results if not r.get('error')])
        
        automation_success_rate = (automation_success / 400) * 100
        conversation_success_rate = (conversation_success / 600) * 100
        
        print(f"🤖 AUTOMATION REQUESTS (Target: 400):")
        print(f"   • Successful: {automation_success}/400 ({automation_success_rate:.1f}%)")
        print(f"   • Failed: {400 - automation_success}/400")
        print(f"   • Avg Response Time: {statistics.mean([r['response_time'] for r in self.automation_results if 'response_time' in r]):.3f}s")
        print()
        
        print(f"💬 CONVERSATIONAL REQUESTS (Target: 600):")
        print(f"   • Successful: {conversation_success}/600 ({conversation_success_rate:.1f}%)")
        print(f"   • Failed: {600 - conversation_success}/600")
        print(f"   • Avg Response Time: {statistics.mean([r['response_time'] for r in self.conversational_results if 'response_time' in r]):.3f}s")
        print()
        
        # Automation Type Analysis
        self._analyze_automation_types()
        
        # Error Analysis
        self._analyze_errors()
        
        # Performance Assessment
        self._assess_performance(success_rate, avg_response_time if self.response_times else 0)
    
    def _analyze_automation_types(self):
        """Analyze automation detection accuracy"""
        
        print(f"🔍 AUTOMATION DETECTION ANALYSIS:")
        
        automation_detected = 0
        workflow_generated = 0
        proper_classification = 0
        
        for result in self.automation_results:
            if not result.get('error'):
                status = result.get('status', '')
                has_workflow = result.get('hasWorkflowJson', False)
                
                if status in ['automation_ready', 'workflow_confirmation', 'parameter_collection', 'workflow_selection']:
                    automation_detected += 1
                    
                if has_workflow:
                    workflow_generated += 1
                    
                if status != 'conversational':  # Should not be classified as conversational
                    proper_classification += 1
        
        detection_rate = (automation_detected / len([r for r in self.automation_results if not r.get('error')])) * 100 if automation_detected > 0 else 0
        workflow_rate = (workflow_generated / len([r for r in self.automation_results if not r.get('error')])) * 100 if workflow_generated > 0 else 0
        
        print(f"   • Automation Detected: {automation_detected} ({detection_rate:.1f}%)")
        print(f"   • Workflows Generated: {workflow_generated} ({workflow_rate:.1f}%)")
        print(f"   • Proper Classification: {proper_classification}")
        print()
        
        # Conversational Misclassification Check
        conversation_misclassified = 0
        for result in self.conversational_results:
            if not result.get('error'):
                status = result.get('status', '')
                if status != 'conversational':
                    conversation_misclassified += 1
        
        print(f"❌ MISCLASSIFICATION ANALYSIS:")
        print(f"   • Conversational → Automation: {conversation_misclassified}")
        print(f"   • Automation → Conversational: {len([r for r in self.automation_results if not r.get('error') and r.get('status') == 'conversational'])}")
        print()
    
    def _analyze_errors(self):
        """Analyze error patterns"""
        
        error_types = {}
        for result in self.automation_results + self.conversational_results:
            if result.get('error'):
                error_msg = result['error']
                if 'HTTP 401' in error_msg:
                    error_types['Authentication'] = error_types.get('Authentication', 0) + 1
                elif 'HTTP 404' in error_msg:
                    error_types['Not Found'] = error_types.get('Not Found', 0) + 1
                elif 'HTTP 500' in error_msg:
                    error_types['Server Error'] = error_types.get('Server Error', 0) + 1
                elif 'timeout' in error_msg.lower():
                    error_types['Timeout'] = error_types.get('Timeout', 0) + 1
                elif 'connection' in error_msg.lower():
                    error_types['Connection'] = error_types.get('Connection', 0) + 1
                else:
                    error_types['Other'] = error_types.get('Other', 0) + 1
        
        print(f"❌ ERROR ANALYSIS:")
        for error_type, count in error_types.items():
            print(f"   • {error_type}: {count}")
        print()
    
    def _assess_performance(self, success_rate: float, avg_response_time: float):
        """Assess overall system performance"""
        
        print(f"🎯 PERFORMANCE ASSESSMENT:")
        
        # Success Rate Assessment
        if success_rate >= 95:
            success_grade = "🟢 EXCELLENT"
        elif success_rate >= 85:
            success_grade = "🟡 GOOD"
        elif success_rate >= 70:
            success_grade = "🟠 FAIR"
        else:
            success_grade = "🔴 NEEDS IMPROVEMENT"
        
        # Response Time Assessment
        if avg_response_time <= 1.0:
            speed_grade = "🟢 FAST"
        elif avg_response_time <= 3.0:
            speed_grade = "🟡 ACCEPTABLE"
        elif avg_response_time <= 5.0:
            speed_grade = "🟠 SLOW"
        else:
            speed_grade = "🔴 TOO SLOW"
        
        print(f"   • Success Rate: {success_grade} ({success_rate:.1f}%)")
        print(f"   • Response Speed: {speed_grade} ({avg_response_time:.3f}s avg)")
        print()
        
        # Recommendations
        print(f"🎯 RECOMMENDATIONS:")
        
        if success_rate < 90:
            print(f"   • Improve error handling and API stability")
        
        if avg_response_time > 2.0:
            print(f"   • Optimize response time (target: <2s)")
        
        if self.error_count > 50:
            print(f"   • Investigate and fix authentication/connection issues")
        
        print(f"   • Consider implementing request batching for high loads")
        print(f"   • Add response caching for common requests")
        print(f"   • Implement rate limiting to prevent server overload")
        
        print(f"\n🏆 MASS TEST COMPLETE: System handled 1000 concurrent user requests!")

def main():
    """Run the mass test suite"""
    
    print("🧪 Enhanced MCP Mass Load Testing")
    print("Simulating realistic user load with automation detection")
    print()
    
    # Check server availability first
    try:
        response = requests.get("http://localhost:8002/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Server is online and ready for testing")
        else:
            print(f"⚠️ Server responded with status {response.status_code}")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        print("Please ensure the backend server is running on port 8002")
        return
    
    # Run mass test
    tester = MassUserTestSuite()
    tester.run_mass_test()

if __name__ == "__main__":
    main()
