#!/usr/bin/env python3
"""
Workflow Analysis Script - Extract Required Drivers
Analyzes all JSON workflow files to determine required drivers
"""

import json
import os
import glob
from collections import defaultdict, Counter
from typing import Dict, List, Set
import re

def analyze_workflow_files(workflow_dir: str) -> Dict[str, any]:
    """Analyze all workflow JSON files to extract node types and required drivers"""
    
    # Find all JSON files in the workflows directory
    json_files = glob.glob(os.path.join(workflow_dir, "*.json"))
    
    results = {
        "total_files": len(json_files),
        "node_types": Counter(),
        "service_providers": Counter(),
        "trigger_types": Counter(),
        "action_types": Counter(),
        "credential_types": Counter(),
        "webhook_nodes": [],
        "cron_schedules": [],
        "api_endpoints": [],
        "required_drivers": set(),
        "driver_mappings": defaultdict(list),
        "errors": []
    }
    
    # Node type to driver mapping
    node_to_driver = {
        # Communication & Messaging
        "n8n-nodes-base.slack": "slack_driver",
        "n8n-nodes-base.slackTrigger": "slack_driver",
        "n8n-nodes-base.telegram": "telegram_driver",
        "n8n-nodes-base.telegramTrigger": "telegram_driver",
        "n8n-nodes-base.discord": "discord_driver",
        "n8n-nodes-base.mattermost": "mattermost_driver",
        "n8n-nodes-base.teams": "teams_driver",
        "n8n-nodes-base.twilio": "twilio_driver",
        "n8n-nodes-base.plivo": "plivo_driver",
        
        # Email
        "n8n-nodes-base.emailSend": "email_driver",
        "n8n-nodes-base.gmail": "gmail_driver",
        "n8n-nodes-base.gmailTrigger": "gmail_driver",
        "n8n-nodes-base.emailReadImap": "email_driver",
        "n8n-nodes-base.microsoftOutlook": "outlook_driver",
        "n8n-nodes-base.mailgun": "mailgun_driver",
        "n8n-nodes-base.sendgrid": "sendgrid_driver",
        
        # HTTP & Web
        "n8n-nodes-base.httpRequest": "http_driver",
        "n8n-nodes-base.webhook": "webhook_driver",
        "n8n-nodes-base.respondToWebhook": "webhook_driver",
        "n8n-nodes-base.webflowTrigger": "webflow_driver",
        "n8n-nodes-base.webflow": "webflow_driver",
        
        # Payment & Finance
        "n8n-nodes-base.stripe": "stripe_driver",
        "n8n-nodes-base.stripeTrigger": "stripe_driver",
        "n8n-nodes-base.paypal": "paypal_driver",
        "n8n-nodes-base.chargebee": "chargebee_driver",
        "n8n-nodes-base.quickbooks": "quickbooks_driver",
        
        # CRM & Sales
        "n8n-nodes-base.hubspot": "hubspot_driver",
        "n8n-nodes-base.hubspotTrigger": "hubspot_driver",
        "n8n-nodes-base.salesforce": "salesforce_driver",
        "n8n-nodes-base.copper": "copper_driver",
        "n8n-nodes-base.pipedrive": "pipedrive_driver",
        "n8n-nodes-base.airtable": "airtable_driver",
        "n8n-nodes-base.airtableTrigger": "airtable_driver",
        
        # Google Services
        "n8n-nodes-base.googleSheets": "google_sheets_driver",
        "n8n-nodes-base.googleSheetsTrigger": "google_sheets_driver",
        "n8n-nodes-base.googleDrive": "google_drive_driver",
        "n8n-nodes-base.googleDriveTrigger": "google_drive_driver",
        "n8n-nodes-base.googleSlides": "google_slides_driver",
        "n8n-nodes-base.googleDocs": "google_docs_driver",
        "n8n-nodes-base.googleCalendar": "google_calendar_driver",
        "n8n-nodes-base.googleBigQuery": "google_bigquery_driver",
        "n8n-nodes-base.googleCloudFirestore": "google_firestore_driver",
        "n8n-nodes-base.googleCloudFunctions": "google_cloud_functions_driver",
        
        # Database & Storage
        "n8n-nodes-base.postgres": "postgres_driver",
        "n8n-nodes-base.mysql": "mysql_driver",
        "n8n-nodes-base.mongodb": "mongodb_driver",
        "n8n-nodes-base.redis": "redis_driver",
        "n8n-nodes-base.awsS3": "aws_s3_driver",
        "n8n-nodes-base.awsDynamoDb": "aws_dynamodb_driver",
        "n8n-nodes-base.awsRds": "aws_rds_driver",
        "n8n-nodes-base.awsSqs": "aws_sqs_driver",
        "n8n-nodes-base.awsLambda": "aws_lambda_driver",
        
        # Productivity & Documents
        "n8n-nodes-base.notion": "notion_driver",
        "n8n-nodes-base.notionTrigger": "notion_driver",
        "n8n-nodes-base.coda": "coda_driver",
        "n8n-nodes-base.microsoftWord": "microsoft_word_driver",
        "n8n-nodes-base.microsoftExcel": "microsoft_excel_driver",
        "n8n-nodes-base.microsoftOneDrive": "microsoft_onedrive_driver",
        "n8n-nodes-base.dropbox": "dropbox_driver",
        "n8n-nodes-base.box": "box_driver",
        
        # Project Management
        "n8n-nodes-base.asana": "asana_driver",
        "n8n-nodes-base.asanaTrigger": "asana_driver",
        "n8n-nodes-base.trello": "trello_driver",
        "n8n-nodes-base.jira": "jira_driver",
        "n8n-nodes-base.mondaycom": "monday_driver",
        "n8n-nodes-base.clickup": "clickup_driver",
        "n8n-nodes-base.todoist": "todoist_driver",
        
        # Social Media & Marketing
        "n8n-nodes-base.twitter": "twitter_driver",
        "n8n-nodes-base.twitterTrigger": "twitter_driver",
        "n8n-nodes-base.linkedin": "linkedin_driver",
        "n8n-nodes-base.facebook": "facebook_driver",
        "n8n-nodes-base.instagram": "instagram_driver",
        "n8n-nodes-base.youtube": "youtube_driver",
        "n8n-nodes-base.mailchimp": "mailchimp_driver",
        "n8n-nodes-base.mailchimpTrigger": "mailchimp_driver",
        
        # Data Processing & Logic
        "n8n-nodes-base.set": "data_processor_driver",
        "n8n-nodes-base.code": "code_executor_driver",
        "n8n-nodes-base.function": "code_executor_driver",
        "n8n-nodes-base.functionItem": "code_executor_driver",
        "n8n-nodes-base.if": "conditional_driver",
        "n8n-nodes-base.switch": "conditional_driver",
        "n8n-nodes-base.merge": "data_processor_driver",
        "n8n-nodes-base.splitInBatches": "data_processor_driver",
        "n8n-nodes-base.itemLists": "data_processor_driver",
        "n8n-nodes-base.dateTime": "utility_driver",
        "n8n-nodes-base.crypto": "utility_driver",
        
        # File Processing
        "n8n-nodes-base.readWriteFile": "file_processor_driver",
        "n8n-nodes-base.readBinaryFile": "file_processor_driver",
        "n8n-nodes-base.writeBinaryFile": "file_processor_driver",
        "n8n-nodes-base.readPdf": "file_processor_driver",
        "n8n-nodes-base.html": "html_processor_driver",
        "n8n-nodes-base.xml": "xml_processor_driver",
        "n8n-nodes-base.csv": "csv_processor_driver",
        "n8n-nodes-base.json": "json_processor_driver",
        
        # Triggers & Scheduling
        "n8n-nodes-base.cron": "scheduler_driver",
        "n8n-nodes-base.cronTrigger": "scheduler_driver",
        "n8n-nodes-base.manualTrigger": "trigger_driver",
        "n8n-nodes-base.intervalTrigger": "scheduler_driver",
        "n8n-nodes-base.start": "trigger_driver",
        
        # API Services
        "n8n-nodes-base.openWeatherMap": "weather_api_driver",
        "n8n-nodes-base.clearbit": "clearbit_driver",
        "n8n-nodes-base.typeform": "typeform_driver",
        "n8n-nodes-base.typeformTrigger": "typeform_driver",
        "n8n-nodes-base.calendly": "calendly_driver",
        "n8n-nodes-base.calendlyTrigger": "calendly_driver",
        "n8n-nodes-base.zoom": "zoom_driver",
        "n8n-nodes-base.shopify": "shopify_driver",
        "n8n-nodes-base.shopifyTrigger": "shopify_driver",
        "n8n-nodes-base.woocommerce": "woocommerce_driver",
        "n8n-nodes-base.magento": "magento_driver",
        
        # Security & Authentication
        "n8n-nodes-base.bitwarden": "bitwarden_driver",
        "n8n-nodes-base.okta": "okta_driver",
        "n8n-nodes-base.auth0": "auth0_driver",
        
        # Utilities
        "n8n-nodes-base.wait": "utility_driver",
        "n8n-nodes-base.noOp": "utility_driver",
        "n8n-nodes-base.stopAndError": "utility_driver",
        "n8n-nodes-base.executeCommand": "system_command_driver",
        "n8n-nodes-base.ssh": "ssh_driver",
        "n8n-nodes-base.ftp": "ftp_driver",
        "n8n-nodes-base.httpBin": "http_driver",
        
        # AI & Machine Learning
        "n8n-nodes-base.openai": "openai_driver",
        "n8n-nodes-base.anthropic": "anthropic_driver",
        "n8n-nodes-base.gemini": "gemini_driver",
        "n8n-nodes-base.huggingface": "huggingface_driver",
        
        # Enterprise & Custom
        "n8n-nodes-base.uproc": "uproc_driver",
        "n8n-nodes-base.emelia": "emelia_driver",
        "n8n-nodes-base.n8n": "n8n_driver",
        "n8n-nodes-base.customWebhook": "webhook_driver",
    }
    
    print(f"📊 Analyzing {len(json_files)} workflow files...")
    
    for i, file_path in enumerate(json_files, 1):
        if i % 100 == 0:
            print(f"   Processed {i}/{len(json_files)} files...")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            
            # Extract nodes
            nodes = workflow_data.get("nodes", [])
            
            for node in nodes:
                node_type = node.get("type", "")
                node_name = node.get("name", "")
                
                # Count node types
                results["node_types"][node_type] += 1
                
                # Extract service provider
                if "." in node_type:
                    service = node_type.split(".")[-1]
                    results["service_providers"][service] += 1
                
                # Categorize triggers vs actions
                if "trigger" in node_type.lower() or "cron" in node_type.lower():
                    results["trigger_types"][node_type] += 1
                else:
                    results["action_types"][node_type] += 1
                
                # Extract credentials
                credentials = node.get("credentials", {})
                for cred_type in credentials.keys():
                    results["credential_types"][cred_type] += 1
                
                # Map to required driver
                if node_type in node_to_driver:
                    driver = node_to_driver[node_type]
                    results["required_drivers"].add(driver)
                    results["driver_mappings"][driver].append(node_type)
                else:
                    # Unknown node type - needs custom driver
                    results["required_drivers"].add(f"custom_{service}_driver")
                    results["driver_mappings"][f"custom_{service}_driver"].append(node_type)
                
                # Extract webhook info
                if "webhook" in node_type.lower():
                    webhook_id = node.get("webhookId", "")
                    results["webhook_nodes"].append({
                        "file": os.path.basename(file_path),
                        "name": node_name,
                        "type": node_type,
                        "webhook_id": webhook_id
                    })
                
                # Extract cron schedules
                if "cron" in node_type.lower():
                    parameters = node.get("parameters", {})
                    results["cron_schedules"].append({
                        "file": os.path.basename(file_path),
                        "name": node_name,
                        "parameters": parameters
                    })
                
                # Extract API endpoints
                if node_type == "n8n-nodes-base.httpRequest":
                    parameters = node.get("parameters", {})
                    url = parameters.get("url", "")
                    method = parameters.get("method", "GET")
                    results["api_endpoints"].append({
                        "file": os.path.basename(file_path),
                        "name": node_name,
                        "url": url,
                        "method": method
                    })
                        
        except Exception as e:
            results["errors"].append({
                "file": os.path.basename(file_path),
                "error": str(e)
            })
    
    return results

def generate_driver_report(results: Dict[str, any]) -> str:
    """Generate a comprehensive driver requirements report"""
    
    report = f"""
🚀 DXTR AUTOFLOW DRIVER REQUIREMENTS ANALYSIS
{'='*80}

📊 ANALYSIS SUMMARY:
• Total Workflow Files: {results['total_files']}
• Unique Node Types: {len(results['node_types'])}
• Service Providers: {len(results['service_providers'])}
• Required Drivers: {len(results['required_drivers'])}
• Trigger Types: {len(results['trigger_types'])}
• Action Types: {len(results['action_types'])}
• Credential Types: {len(results['credential_types'])}
• Webhook Nodes: {len(results['webhook_nodes'])}
• Cron Schedules: {len(results['cron_schedules'])}
• API Endpoints: {len(results['api_endpoints'])}

🔧 REQUIRED DRIVERS:
{'='*50}
"""
    
    # Group drivers by category
    driver_categories = {
        "Communication & Messaging": [],
        "Email Services": [],
        "HTTP & Web": [],
        "Payment & Finance": [],
        "CRM & Sales": [],
        "Google Services": [],
        "Database & Storage": [],
        "Productivity & Documents": [],
        "Project Management": [],
        "Social Media & Marketing": [],
        "Data Processing & Logic": [],
        "File Processing": [],
        "Triggers & Scheduling": [],
        "API Services": [],
        "Security & Authentication": [],
        "AI & Machine Learning": [],
        "Utilities": [],
        "Enterprise & Custom": []
    }
    
    # Categorize drivers
    for driver in sorted(results['required_drivers']):
        if any(x in driver for x in ['slack', 'telegram', 'discord', 'mattermost', 'teams', 'twilio', 'plivo']):
            driver_categories["Communication & Messaging"].append(driver)
        elif any(x in driver for x in ['email', 'gmail', 'outlook', 'mailgun', 'sendgrid']):
            driver_categories["Email Services"].append(driver)
        elif any(x in driver for x in ['http', 'webhook', 'webflow']):
            driver_categories["HTTP & Web"].append(driver)
        elif any(x in driver for x in ['stripe', 'paypal', 'chargebee', 'quickbooks']):
            driver_categories["Payment & Finance"].append(driver)
        elif any(x in driver for x in ['hubspot', 'salesforce', 'copper', 'pipedrive', 'airtable']):
            driver_categories["CRM & Sales"].append(driver)
        elif any(x in driver for x in ['google']):
            driver_categories["Google Services"].append(driver)
        elif any(x in driver for x in ['postgres', 'mysql', 'mongodb', 'redis', 'aws', 'database']):
            driver_categories["Database & Storage"].append(driver)
        elif any(x in driver for x in ['notion', 'coda', 'microsoft', 'dropbox', 'box']):
            driver_categories["Productivity & Documents"].append(driver)
        elif any(x in driver for x in ['asana', 'trello', 'jira', 'monday', 'clickup', 'todoist']):
            driver_categories["Project Management"].append(driver)
        elif any(x in driver for x in ['twitter', 'linkedin', 'facebook', 'instagram', 'youtube', 'mailchimp']):
            driver_categories["Social Media & Marketing"].append(driver)
        elif any(x in driver for x in ['data_processor', 'code_executor', 'conditional', 'utility']):
            driver_categories["Data Processing & Logic"].append(driver)
        elif any(x in driver for x in ['file_processor', 'html_processor', 'xml_processor', 'csv_processor', 'json_processor']):
            driver_categories["File Processing"].append(driver)
        elif any(x in driver for x in ['scheduler', 'trigger', 'cron']):
            driver_categories["Triggers & Scheduling"].append(driver)
        elif any(x in driver for x in ['weather', 'clearbit', 'typeform', 'calendly', 'zoom', 'shopify', 'woocommerce', 'magento']):
            driver_categories["API Services"].append(driver)
        elif any(x in driver for x in ['bitwarden', 'okta', 'auth0']):
            driver_categories["Security & Authentication"].append(driver)
        elif any(x in driver for x in ['openai', 'anthropic', 'gemini', 'huggingface']):
            driver_categories["AI & Machine Learning"].append(driver)
        elif any(x in driver for x in ['system_command', 'ssh', 'ftp']):
            driver_categories["Utilities"].append(driver)
        else:
            driver_categories["Enterprise & Custom"].append(driver)
    
    # Generate report for each category
    for category, drivers in driver_categories.items():
        if drivers:
            report += f"\\n📁 {category}:\\n"
            for driver in drivers:
                node_types = results['driver_mappings'].get(driver, [])
                report += f"   ✅ {driver}\\n"
                for node_type in node_types[:3]:  # Show first 3 node types
                    report += f"      • {node_type}\\n"
                if len(node_types) > 3:
                    report += f"      • ... and {len(node_types) - 3} more\\n"
    
    # Top 20 most used node types
    report += f"\\n🔥 TOP 20 MOST USED NODE TYPES:\\n"
    report += "="*50 + "\\n"
    for node_type, count in results['node_types'].most_common(20):
        report += f"{count:4d}x  {node_type}\\n"
    
    # Top service providers
    report += f"\\n🏢 TOP SERVICE PROVIDERS:\\n"
    report += "="*30 + "\\n"
    for service, count in results['service_providers'].most_common(15):
        report += f"{count:4d}x  {service}\\n"
    
    # Credential types
    report += f"\\n🔐 CREDENTIAL TYPES NEEDED:\\n"
    report += "="*30 + "\\n"
    for cred_type, count in results['credential_types'].most_common(15):
        report += f"{count:4d}x  {cred_type}\\n"
    
    # Errors
    if results['errors']:
        report += f"\\n❌ PARSING ERRORS ({len(results['errors'])}):\\n"
        report += "="*30 + "\\n"
        for error in results['errors'][:10]:  # Show first 10 errors
            report += f"• {error['file']}: {error['error']}\\n"
    
    return report

def save_driver_files_list(results: Dict[str, any]) -> None:
    """Save list of required driver files"""
    
    driver_files = []
    for driver in sorted(results['required_drivers']):
        driver_files.append(f"backend/mcp/drivers/universal/{driver}.py")
    
    with open("required_driver_files.txt", "w") as f:
        f.write("# Required Driver Files for DXTR AutoFlow\\n")
        f.write(f"# Total: {len(driver_files)} drivers\\n\\n")
        for file_path in driver_files:
            f.write(f"{file_path}\\n")
    
    print(f"📄 Saved driver files list to: required_driver_files.txt")

if __name__ == "__main__":
    # Analyze workflow files
    workflow_dir = "src/app/dashboard/automation/workflows"
    
    if not os.path.exists(workflow_dir):
        print(f"❌ Workflow directory not found: {workflow_dir}")
        exit(1)
    
    print("🔍 Starting workflow analysis...")
    results = analyze_workflow_files(workflow_dir)
    
    # Generate and save report
    report = generate_driver_report(results)
    
    with open("driver_requirements_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(report)
    print(f"\\n💾 Full report saved to: driver_requirements_report.txt")
    
    # Save driver files list
    save_driver_files_list(results)
    
    # Save raw results as JSON
    # Convert sets to lists for JSON serialization
    results_copy = dict(results)
    results_copy['required_drivers'] = list(results_copy['required_drivers'])
    results_copy['driver_mappings'] = dict(results_copy['driver_mappings'])
    
    with open("workflow_analysis_results.json", "w") as f:
        json.dump(results_copy, f, indent=2)
    
    print(f"📊 Raw analysis data saved to: workflow_analysis_results.json")
    print(f"\\n🎯 Analysis complete! Found {len(results['required_drivers'])} required drivers.")
