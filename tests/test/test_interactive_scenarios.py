#!/usr/bin/env python3
"""
Interactive Workflow Loader Test Scenarios
Demonstrates 10+ real user scenarios with the workflow loading system
"""

import requests
import json
import time
import urllib.parse
from typing import Dict, Any

class InteractiveWorkflowTester:
    def __init__(self, base_url: str = "http://localhost:3001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/automation/load-workflow"
        
    def print_header(self, title: str):
        print("\n" + "="*60)
        print(f"🎯 {title}")
        print("="*60)
    
    def print_step(self, step: str, details: str = ""):
        print(f"\n📝 {step}")
        if details:
            print(f"   {details}")
    
    def scenario_1_email_automation(self):
        """Scenario 1: User wants to create an email automation workflow"""
        self.print_header("SCENARIO 1: Email Marketing Automation")
        
        workflow = {
            "id": "email_automation_001",
            "name": "Daily Newsletter Automation",
            "description": "Automated email marketing campaign for daily newsletter",
            "filename": "email_automation.json",
            "nodes": [
                {
                    "id": "trigger_node",
                    "type": "schedule",
                    "name": "Daily Trigger",
                    "parameters": {
                        "schedule": "0 9 * * *",  # 9 AM daily
                        "timezone": "UTC"
                    }
                },
                {
                    "id": "content_generator",
                    "type": "ai",
                    "name": "Generate Newsletter Content",
                    "parameters": {
                        "prompt": "Generate daily newsletter content about tech trends",
                        "model": "gpt-4-turbo",
                        "max_tokens": 500
                    }
                },
                {
                    "id": "email_sender",
                    "type": "email",
                    "name": "Send Newsletter",
                    "parameters": {
                        "to": "subscribers@company.com",
                        "subject": "Daily Tech Newsletter",
                        "template": "newsletter_template"
                    }
                }
            ]
        }
        
        self.print_step("User Request", "I want to automate sending daily newsletters with AI-generated content")
        self.print_step("System Action", "Creating email automation workflow...")
        
        response = requests.post(self.api_url, json={"workflow": workflow})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Workflow created with ID: {data['workflowId']}")
            print(f"🔗 Agent URL: {data['redirectUrl']}")
            return data['workflowId']
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")
            return None
    
    def scenario_2_social_media_posting(self):
        """Scenario 2: User wants to automate social media posting"""
        self.print_header("SCENARIO 2: Social Media Cross-Posting")
        
        workflow = {
            "id": "social_media_automation_002",
            "name": "Multi-Platform Social Media Poster",
            "description": "Automatically post content to Twitter, LinkedIn, and Facebook",
            "filename": "social_media_automation.json",
            "nodes": [
                {
                    "id": "webhook_trigger",
                    "type": "webhook",
                    "name": "Content Webhook",
                    "parameters": {
                        "method": "POST",
                        "path": "/social-content",
                        "authentication": "api_key"
                    }
                },
                {
                    "id": "content_processor",
                    "type": "transform",
                    "name": "Process Content",
                    "parameters": {
                        "operations": [
                            {"type": "extract", "field": "content"},
                            {"type": "validate", "max_length": 280}
                        ]
                    }
                },
                {
                    "id": "twitter_post",
                    "type": "http",
                    "name": "Post to Twitter",
                    "parameters": {
                        "url": "https://api.twitter.com/2/tweets",
                        "method": "POST",
                        "auth": "oauth"
                    }
                },
                {
                    "id": "linkedin_post",
                    "type": "http",
                    "name": "Post to LinkedIn",
                    "parameters": {
                        "url": "https://api.linkedin.com/v2/shares",
                        "method": "POST",
                        "auth": "oauth"
                    }
                }
            ]
        }
        
        self.print_step("User Request", "I need to post the same content to Twitter and LinkedIn simultaneously")
        self.print_step("System Action", "Creating multi-platform social media workflow...")
        
        response = requests.post(self.api_url, json={"workflow": workflow})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Social media workflow created: {data['workflowId']}")
            return data['workflowId']
        else:
            print(f"❌ FAILED: {response.status_code}")
            return None
    
    def scenario_3_data_backup(self):
        """Scenario 3: User wants to automate database backups"""
        self.print_header("SCENARIO 3: Automated Database Backup")
        
        workflow = {
            "id": "backup_automation_003",
            "name": "Daily Database Backup to Cloud",
            "description": "Automated backup of PostgreSQL database to AWS S3",
            "filename": "database_backup.json",
            "nodes": [
                {
                    "id": "backup_trigger",
                    "type": "schedule",
                    "name": "Nightly Backup Schedule",
                    "parameters": {
                        "schedule": "0 2 * * *",  # 2 AM daily
                        "timezone": "America/New_York"
                    }
                },
                {
                    "id": "db_dump",
                    "type": "database",
                    "name": "Create Database Dump",
                    "parameters": {
                        "connection": "postgresql://localhost:5432/mydb",
                        "operation": "dump",
                        "format": "sql"
                    }
                },
                {
                    "id": "compress_file",
                    "type": "file",
                    "name": "Compress Backup",
                    "parameters": {
                        "operation": "compress",
                        "format": "gzip"
                    }
                },
                {
                    "id": "upload_s3",
                    "type": "aws",
                    "name": "Upload to S3",
                    "parameters": {
                        "service": "s3",
                        "bucket": "mycompany-backups",
                        "path": "/database-backups/"
                    }
                },
                {
                    "id": "notification",
                    "type": "email",
                    "name": "Success Notification",
                    "parameters": {
                        "to": "admin@company.com",
                        "subject": "Backup Completed Successfully"
                    }
                }
            ]
        }
        
        self.print_step("User Request", "I need nightly database backups uploaded to AWS S3 with email notifications")
        self.print_step("System Action", "Creating database backup automation...")
        
        response = requests.post(self.api_url, json={"workflow": workflow})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Backup workflow created: {data['workflowId']}")
            return data['workflowId']
        else:
            print(f"❌ FAILED: {response.status_code}")
            return None
    
    def scenario_4_customer_support(self):
        """Scenario 4: Customer support ticket automation"""
        self.print_header("SCENARIO 4: Customer Support Automation")
        
        workflow = {
            "id": "support_automation_004",
            "name": "Intelligent Customer Support Router",
            "description": "Auto-categorize and route customer support tickets",
            "filename": "customer_support.json",
            "nodes": [
                {
                    "id": "email_receiver",
                    "type": "email",
                    "name": "Receive Support Email",
                    "parameters": {
                        "inbox": "support@company.com",
                        "filter": "unread"
                    }
                },
                {
                    "id": "ai_categorizer",
                    "type": "ai",
                    "name": "Categorize Ticket",
                    "parameters": {
                        "prompt": "Categorize this support ticket: technical, billing, general",
                        "model": "gpt-4",
                        "output_format": "json"
                    }
                },
                {
                    "id": "priority_assessment",
                    "type": "ai",
                    "name": "Assess Priority",
                    "parameters": {
                        "prompt": "Rate this ticket priority: low, medium, high, urgent",
                        "model": "gpt-4"
                    }
                },
                {
                    "id": "route_ticket",
                    "type": "conditional",
                    "name": "Route to Team",
                    "parameters": {
                        "conditions": [
                            {"if": "category == 'technical'", "then": "tech-team@company.com"},
                            {"if": "category == 'billing'", "then": "billing@company.com"},
                            {"else": "general@company.com"}
                        ]
                    }
                },
                {
                    "id": "auto_response",
                    "type": "email",
                    "name": "Send Auto Response",
                    "parameters": {
                        "template": "support_acknowledgment",
                        "include_ticket_number": True
                    }
                }
            ]
        }
        
        self.print_step("User Request", "I want to automatically categorize and route customer support emails")
        self.print_step("System Action", "Creating intelligent support ticket router...")
        
        response = requests.post(self.api_url, json={"workflow": workflow})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Support automation created: {data['workflowId']}")
            return data['workflowId']
        else:
            print(f"❌ FAILED: {response.status_code}")
            return None
    
    def scenario_5_ecommerce_order(self):
        """Scenario 5: E-commerce order processing"""
        self.print_header("SCENARIO 5: E-commerce Order Processing")
        
        workflow = {
            "id": "ecommerce_order_005",
            "name": "Complete Order Processing Pipeline",
            "description": "Handle new orders from payment to fulfillment",
            "filename": "ecommerce_order.json",
            "nodes": [
                {
                    "id": "order_webhook",
                    "type": "webhook",
                    "name": "New Order Webhook",
                    "parameters": {
                        "endpoint": "/api/orders/new",
                        "method": "POST",
                        "validate_signature": True
                    }
                },
                {
                    "id": "payment_verification",
                    "type": "http",
                    "name": "Verify Payment",
                    "parameters": {
                        "url": "https://api.stripe.com/v1/charges/{{order.charge_id}}",
                        "method": "GET",
                        "headers": {"Authorization": "Bearer {{stripe_key}}"}
                    }
                },
                {
                    "id": "inventory_check",
                    "type": "database",
                    "name": "Check Inventory",
                    "parameters": {
                        "query": "SELECT quantity FROM inventory WHERE product_id = {{order.product_id}}",
                        "connection": "inventory_db"
                    }
                },
                {
                    "id": "update_inventory",
                    "type": "database",
                    "name": "Update Stock",
                    "parameters": {
                        "query": "UPDATE inventory SET quantity = quantity - {{order.quantity}} WHERE product_id = {{order.product_id}}"
                    }
                },
                {
                    "id": "shipping_label",
                    "type": "http",
                    "name": "Create Shipping Label",
                    "parameters": {
                        "url": "https://api.shippo.com/shipments/",
                        "method": "POST",
                        "data": "{{shipping_details}}"
                    }
                },
                {
                    "id": "customer_notification",
                    "type": "email",
                    "name": "Order Confirmation",
                    "parameters": {
                        "to": "{{order.customer_email}}",
                        "template": "order_confirmation",
                        "include_tracking": True
                    }
                }
            ]
        }
        
        self.print_step("User Request", "I need to automate the entire order processing from payment to shipping")
        self.print_step("System Action", "Creating complete e-commerce pipeline...")
        
        response = requests.post(self.api_url, json={"workflow": workflow})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: E-commerce workflow created: {data['workflowId']}")
            return data['workflowId']
        else:
            print(f"❌ FAILED: {response.status_code}")
            return None
    
    def scenario_6_content_moderation(self):
        """Scenario 6: Content moderation for social platform"""
        self.print_header("SCENARIO 6: AI-Powered Content Moderation")
        
        workflow = {
            "id": "content_moderation_006",
            "name": "Automated Content Moderation System",
            "description": "AI-powered content filtering and moderation",
            "filename": "content_moderation.json",
            "nodes": [
                {
                    "id": "content_upload",
                    "type": "webhook",
                    "name": "Content Upload Trigger",
                    "parameters": {
                        "endpoint": "/api/content/upload",
                        "types": ["image", "text", "video"]
                    }
                },
                {
                    "id": "text_analysis",
                    "type": "ai",
                    "name": "Analyze Text Content",
                    "parameters": {
                        "model": "moderation-model",
                        "checks": ["toxicity", "spam", "hate_speech"],
                        "threshold": 0.8
                    }
                },
                {
                    "id": "image_analysis",
                    "type": "ai",
                    "name": "Analyze Images",
                    "parameters": {
                        "service": "aws_rekognition",
                        "detect": ["explicit_content", "violence", "drugs"]
                    }
                },
                {
                    "id": "decision_engine",
                    "type": "conditional",
                    "name": "Moderation Decision",
                    "parameters": {
                        "rules": [
                            {"if": "toxicity > 0.8", "action": "reject"},
                            {"if": "explicit_content == true", "action": "flag"},
                            {"else": "approve"}
                        ]
                    }
                },
                {
                    "id": "notification",
                    "type": "http",
                    "name": "Notify User",
                    "parameters": {
                        "url": "/api/notifications/send",
                        "template": "moderation_result"
                    }
                }
            ]
        }
        
        self.print_step("User Request", "I need to automatically moderate user-generated content using AI")
        self.print_step("System Action", "Creating AI content moderation system...")
        
        response = requests.post(self.api_url, json={"workflow": workflow})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Content moderation workflow created: {data['workflowId']}")
            return data['workflowId']
        else:
            print(f"❌ FAILED: {response.status_code}")
            return None
    
    def scenario_7_lead_qualification(self):
        """Scenario 7: Sales lead qualification and scoring"""
        self.print_header("SCENARIO 7: Automated Lead Qualification")
        
        workflow = {
            "id": "lead_qualification_007",
            "name": "AI Lead Scoring and Qualification",
            "description": "Automatically score and qualify sales leads",
            "filename": "lead_qualification.json",
            "nodes": [
                {
                    "id": "form_submission",
                    "type": "webhook",
                    "name": "Lead Form Submission",
                    "parameters": {
                        "source": "website_forms",
                        "required_fields": ["email", "company", "role"]
                    }
                },
                {
                    "id": "company_enrichment",
                    "type": "http",
                    "name": "Enrich Company Data",
                    "parameters": {
                        "service": "clearbit",
                        "url": "https://company.clearbit.com/v2/companies/find",
                        "lookup_field": "domain"
                    }
                },
                {
                    "id": "ai_scoring",
                    "type": "ai",
                    "name": "AI Lead Scoring",
                    "parameters": {
                        "model": "lead-scoring-model",
                        "factors": ["company_size", "industry", "role", "budget"],
                        "output": "score_0_100"
                    }
                },
                {
                    "id": "qualification_check",
                    "type": "conditional",
                    "name": "Qualify Lead",
                    "parameters": {
                        "conditions": [
                            {"if": "score >= 80", "status": "hot_lead"},
                            {"if": "score >= 60", "status": "warm_lead"},
                            {"if": "score >= 40", "status": "cold_lead"},
                            {"else": "unqualified"}
                        ]
                    }
                },
                {
                    "id": "crm_update",
                    "type": "http",
                    "name": "Update CRM",
                    "parameters": {
                        "system": "salesforce",
                        "operation": "create_lead",
                        "fields": "{{lead_data}}"
                    }
                },
                {
                    "id": "sales_notification",
                    "type": "email",
                    "name": "Notify Sales Team",
                    "parameters": {
                        "condition": "score >= 60",
                        "to": "sales@company.com",
                        "template": "new_qualified_lead"
                    }
                }
            ]
        }
        
        self.print_step("User Request", "I want to automatically score leads and notify sales for high-quality prospects")
        self.print_step("System Action", "Creating AI lead qualification system...")
        
        response = requests.post(self.api_url, json={"workflow": workflow})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Lead qualification workflow created: {data['workflowId']}")
            return data['workflowId']
        else:
            print(f"❌ FAILED: {response.status_code}")
            return None
    
    def scenario_8_expense_approval(self):
        """Scenario 8: Expense report approval workflow"""
        self.print_header("SCENARIO 8: Automated Expense Approval")
        
        workflow = {
            "id": "expense_approval_008",
            "name": "Smart Expense Report Approval",
            "description": "Automated expense report processing and approval routing",
            "filename": "expense_approval.json",
            "nodes": [
                {
                    "id": "expense_submission",
                    "type": "webhook",
                    "name": "Expense Report Submitted",
                    "parameters": {
                        "source": "expense_app",
                        "validate_receipts": True
                    }
                },
                {
                    "id": "receipt_ocr",
                    "type": "ai",
                    "name": "Extract Receipt Data",
                    "parameters": {
                        "service": "aws_textract",
                        "extract": ["amount", "date", "vendor", "category"]
                    }
                },
                {
                    "id": "policy_check",
                    "type": "conditional",
                    "name": "Check Company Policy",
                    "parameters": {
                        "rules": [
                            {"if": "amount > 500", "approval_required": "manager"},
                            {"if": "amount > 1000", "approval_required": "director"},
                            {"if": "category == 'travel'", "check_travel_policy": True}
                        ]
                    }
                },
                {
                    "id": "auto_approve",
                    "type": "conditional",
                    "name": "Auto Approve Small Expenses",
                    "parameters": {
                        "condition": "amount <= 100 AND category IN ('meals', 'transport')",
                        "action": "auto_approve"
                    }
                },
                {
                    "id": "approval_request",
                    "type": "email",
                    "name": "Request Approval",
                    "parameters": {
                        "condition": "approval_required",
                        "to": "{{manager_email}}",
                        "template": "expense_approval_request"
                    }
                },
                {
                    "id": "accounting_integration",
                    "type": "http",
                    "name": "Update Accounting System",
                    "parameters": {
                        "system": "quickbooks",
                        "operation": "create_expense"
                    }
                }
            ]
        }
        
        self.print_step("User Request", "I need to automate expense report approvals with different rules based on amount")
        self.print_step("System Action", "Creating smart expense approval workflow...")
        
        response = requests.post(self.api_url, json={"workflow": workflow})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Expense approval workflow created: {data['workflowId']}")
            return data['workflowId']
        else:
            print(f"❌ FAILED: {response.status_code}")
            return None
    
    def scenario_9_security_monitoring(self):
        """Scenario 9: Security incident response automation"""
        self.print_header("SCENARIO 9: Security Incident Response")
        
        workflow = {
            "id": "security_monitoring_009",
            "name": "Automated Security Incident Response",
            "description": "Detect, analyze, and respond to security incidents",
            "filename": "security_monitoring.json",
            "nodes": [
                {
                    "id": "security_alert",
                    "type": "webhook",
                    "name": "Security Alert Trigger",
                    "parameters": {
                        "sources": ["firewall", "ids", "antivirus", "log_analysis"],
                        "severity_levels": ["medium", "high", "critical"]
                    }
                },
                {
                    "id": "threat_analysis",
                    "type": "ai",
                    "name": "Analyze Threat",
                    "parameters": {
                        "model": "security-analysis-model",
                        "analyze": ["attack_type", "severity", "potential_impact"],
                        "enrichment": "threat_intelligence"
                    }
                },
                {
                    "id": "ip_reputation",
                    "type": "http",
                    "name": "Check IP Reputation",
                    "parameters": {
                        "service": "virustotal",
                        "endpoint": "/api/v3/ip_addresses/{{source_ip}}"
                    }
                },
                {
                    "id": "incident_classification",
                    "type": "conditional",
                    "name": "Classify Incident",
                    "parameters": {
                        "rules": [
                            {"if": "severity == 'critical'", "response": "immediate_block"},
                            {"if": "threat_score > 8", "response": "isolate_system"},
                            {"if": "attack_type == 'brute_force'", "response": "rate_limit"}
                        ]
                    }
                },
                {
                    "id": "automated_response",
                    "type": "http",
                    "name": "Execute Response",
                    "parameters": {
                        "firewall_api": "/api/block_ip",
                        "quarantine_api": "/api/isolate_host"
                    }
                },
                {
                    "id": "security_team_alert",
                    "type": "multiple",
                    "name": "Alert Security Team",
                    "parameters": {
                        "email": "security@company.com",
                        "slack": "#security-alerts",
                        "pagerduty": "security_escalation"
                    }
                }
            ]
        }
        
        self.print_step("User Request", "I need automated security incident detection and response")
        self.print_step("System Action", "Creating security monitoring workflow...")
        
        response = requests.post(self.api_url, json={"workflow": workflow})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Security monitoring workflow created: {data['workflowId']}")
            return data['workflowId']
        else:
            print(f"❌ FAILED: {response.status_code}")
            return None
    
    def scenario_10_hr_onboarding(self):
        """Scenario 10: Employee onboarding automation"""
        self.print_header("SCENARIO 10: Employee Onboarding Automation")
        
        workflow = {
            "id": "hr_onboarding_010",
            "name": "Complete Employee Onboarding Process",
            "description": "Automate new employee onboarding from offer acceptance to first day",
            "filename": "hr_onboarding.json",
            "nodes": [
                {
                    "id": "offer_acceptance",
                    "type": "webhook",
                    "name": "Offer Accepted",
                    "parameters": {
                        "source": "ats_system",
                        "trigger": "offer_signed"
                    }
                },
                {
                    "id": "create_accounts",
                    "type": "http",
                    "name": "Create System Accounts",
                    "parameters": {
                        "systems": ["active_directory", "email", "slack", "jira"],
                        "template": "standard_employee"
                    }
                },
                {
                    "id": "equipment_request",
                    "type": "http",
                    "name": "Order Equipment",
                    "parameters": {
                        "system": "asset_management",
                        "items": ["laptop", "monitor", "accessories"],
                        "delivery_date": "{{start_date - 2}}"
                    }
                },
                {
                    "id": "calendar_setup",
                    "type": "calendar",
                    "name": "Schedule Onboarding",
                    "parameters": {
                        "events": [
                            {"title": "Welcome Meeting", "duration": 60},
                            {"title": "IT Setup", "duration": 30},
                            {"title": "HR Orientation", "duration": 120}
                        ]
                    }
                },
                {
                    "id": "document_generation",
                    "type": "document",
                    "name": "Generate Documents",
                    "parameters": {
                        "templates": ["employee_handbook", "security_policy", "benefits_guide"],
                        "personalize": True
                    }
                },
                {
                    "id": "welcome_package",
                    "type": "email",
                    "name": "Send Welcome Package",
                    "parameters": {
                        "to": "{{employee_email}}",
                        "template": "welcome_new_employee",
                        "attachments": "{{generated_documents}}"
                    }
                },
                {
                    "id": "manager_notification",
                    "type": "email",
                    "name": "Notify Manager",
                    "parameters": {
                        "to": "{{manager_email}}",
                        "template": "new_team_member_arriving"
                    }
                }
            ]
        }
        
        self.print_step("User Request", "I want to automate the entire employee onboarding process")
        self.print_step("System Action", "Creating comprehensive HR onboarding workflow...")
        
        response = requests.post(self.api_url, json={"workflow": workflow})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: HR onboarding workflow created: {data['workflowId']}")
            return data['workflowId']
        else:
            print(f"❌ FAILED: {response.status_code}")
            return None
    
    def run_all_scenarios(self):
        """Run all user scenarios"""
        print("🎬 STARTING INTERACTIVE WORKFLOW SCENARIOS")
        print("Demonstrating 10 real-world automation use cases")
        
        workflows = []
        scenarios = [
            self.scenario_1_email_automation,
            self.scenario_2_social_media_posting,
            self.scenario_3_data_backup,
            self.scenario_4_customer_support,
            self.scenario_5_ecommerce_order,
            self.scenario_6_content_moderation,
            self.scenario_7_lead_qualification,
            self.scenario_8_expense_approval,
            self.scenario_9_security_monitoring,
            self.scenario_10_hr_onboarding
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            workflow_id = scenario()
            if workflow_id:
                workflows.append(workflow_id)
            time.sleep(1)  # Brief pause between scenarios
        
        # Summary
        self.print_header("SCENARIO TESTING COMPLETE")
        print(f"✅ Successfully created {len(workflows)} workflows")
        print(f"🔗 All workflows can be accessed via the agent interface")
        
        if workflows:
            print("\n📋 Created Workflow IDs:")
            for i, wid in enumerate(workflows, 1):
                print(f"   {i:2d}. {wid}")
                
            print(f"\n🎯 To test any workflow, visit:")
            print(f"   {self.base_url}/dashboard/automation/agent?workflowId=<WORKFLOW_ID>&mode=configure")

if __name__ == "__main__":
    tester = InteractiveWorkflowTester()
    tester.run_all_scenarios()
