#!/usr/bin/env python3
"""
Local Test for Data Fetch + Email Prompt
Tests user input processing without needing backend authentication
"""

import re
import json
from typing import Dict, List, Any

class LocalPromptProcessor:
    def __init__(self):
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.data_keywords = [
            'fetch', 'get', 'retrieve', 'pull', 'extract', 'load', 'query',
            'data', 'information', 'records', 'analytics', 'logs', 'report'
        ]
        self.server_keywords = [
            'server', 'database', 'api', 'endpoint', 'service', 'system',
            'crm', 'analytics', 'platform', 'backend', 'storage'
        ]
        self.email_keywords = [
            'email', 'send', 'mail', 'notify', 'alert', 'message', 'report'
        ]

    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        return re.findall(self.email_pattern, text)

    def detect_intent(self, user_input: str) -> Dict[str, Any]:
        """Detect user intent and extract parameters"""
        text_lower = user_input.lower()
        
        # Count keyword matches
        data_matches = sum(1 for kw in self.data_keywords if kw in text_lower)
        server_matches = sum(1 for kw in self.server_keywords if kw in text_lower)
        email_matches = sum(1 for kw in self.email_keywords if kw in text_lower)
        
        # Extract emails
        emails = self.extract_emails(user_input)
        
        # Determine intent
        intent_scores = {
            'data_processing': data_matches + server_matches,
            'email_automation': email_matches + len(emails),
            'data_email_workflow': data_matches + email_matches + len(emails)
        }
        
        primary_intent = max(intent_scores.keys(), key=lambda k: intent_scores[k])
        confidence = intent_scores[primary_intent] / 10.0  # Normalize to 0-1
        
        return {
            'intent': primary_intent,
            'confidence': min(confidence, 1.0),
            'extracted_emails': emails,
            'data_keywords_found': [kw for kw in self.data_keywords if kw in text_lower],
            'server_keywords_found': [kw for kw in self.server_keywords if kw in text_lower],
            'email_keywords_found': [kw for kw in self.email_keywords if kw in text_lower],
            'keyword_counts': intent_scores
        }

    def generate_workflow_structure(self, user_input: str, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate workflow structure based on intent"""
        workflow = {
            'id': 'local_workflow_001',
            'name': f'User Request: {user_input[:50]}...',
            'description': f'Automated workflow for: {user_input}',
            'user_input': user_input,
            'detected_intent': intent_data['intent'],
            'confidence': intent_data['confidence'],
            'nodes': []
        }
        
        if intent_data['intent'] == 'data_email_workflow':
            # Data fetch + email workflow
            workflow['nodes'] = [
                {
                    'id': 'trigger_1',
                    'type': 'manual_trigger',
                    'name': 'Manual Trigger',
                    'description': 'User initiated the workflow',
                    'parameters': {
                        'user_request': user_input
                    }
                },
                {
                    'id': 'data_fetch',
                    'type': 'data_source',
                    'name': 'Fetch Data from Server',
                    'description': 'Retrieve data based on user request',
                    'parameters': {
                        'source_keywords': intent_data['server_keywords_found'],
                        'data_type': intent_data['data_keywords_found'],
                        'fetch_method': 'auto_detect'
                    }
                },
                {
                    'id': 'data_process',
                    'type': 'data_processor',
                    'name': 'Process Retrieved Data',
                    'description': 'Format and prepare data for email',
                    'parameters': {
                        'format': 'email_friendly',
                        'include_summary': True
                    }
                },
                {
                    'id': 'email_compose',
                    'type': 'email_composer',
                    'name': 'Compose Email',
                    'description': 'Create email with fetched data',
                    'parameters': {
                        'recipients': intent_data['extracted_emails'],
                        'subject': 'Data Report from Server',
                        'include_data': True,
                        'format': 'html_table'
                    }
                },
                {
                    'id': 'email_send',
                    'type': 'email_sender',
                    'name': 'Send Email',
                    'description': 'Send email to specified recipients',
                    'parameters': {
                        'recipients': intent_data['extracted_emails'],
                        'delivery_method': 'smtp',
                        'priority': 'normal'
                    }
                }
            ]
        
        elif intent_data['intent'] == 'data_processing':
            workflow['nodes'] = [
                {
                    'id': 'data_fetch',
                    'type': 'data_source',
                    'name': 'Data Retrieval',
                    'parameters': {
                        'source': 'server',
                        'method': 'api_call'
                    }
                },
                {
                    'id': 'data_output',
                    'type': 'output',
                    'name': 'Output Results',
                    'parameters': {
                        'format': 'structured_data'
                    }
                }
            ]
        
        elif intent_data['intent'] == 'email_automation':
            workflow['nodes'] = [
                {
                    'id': 'email_compose',
                    'type': 'email_composer',
                    'name': 'Compose Email',
                    'parameters': {
                        'recipients': intent_data['extracted_emails']
                    }
                },
                {
                    'id': 'email_send',
                    'type': 'email_sender',
                    'name': 'Send Email',
                    'parameters': {
                        'recipients': intent_data['extracted_emails']
                    }
                }
            ]
        
        return workflow

    def test_specific_prompt(self, user_input: str) -> Dict[str, Any]:
        """Test a specific user prompt"""
        print(f"🔍 ANALYZING USER INPUT")
        print(f"Input: {user_input}")
        print("-" * 60)
        
        # Detect intent
        intent_data = self.detect_intent(user_input)
        
        print(f"✅ INTENT DETECTION RESULTS:")
        print(f"   Primary Intent: {intent_data['intent']}")
        print(f"   Confidence: {intent_data['confidence']:.2f}")
        print(f"   Extracted Emails: {intent_data['extracted_emails']}")
        print(f"   Data Keywords: {intent_data['data_keywords_found']}")
        print(f"   Server Keywords: {intent_data['server_keywords_found']}")
        print(f"   Email Keywords: {intent_data['email_keywords_found']}")
        
        # Generate workflow
        workflow = self.generate_workflow_structure(user_input, intent_data)
        
        print(f"\n🔧 GENERATED WORKFLOW:")
        print(f"   Workflow ID: {workflow['id']}")
        print(f"   Name: {workflow['name']}")
        print(f"   Node Count: {len(workflow['nodes'])}")
        
        for i, node in enumerate(workflow['nodes'], 1):
            print(f"   {i}. {node['name']} ({node['type']})")
            if 'recipients' in node.get('parameters', {}):
                recipients = node['parameters']['recipients']
                print(f"      → Recipients: {recipients}")
        
        # Validate workflow
        validation = self.validate_workflow(workflow, intent_data)
        
        print(f"\n📋 WORKFLOW VALIDATION:")
        for check, result in validation.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check}")
        
        return {
            'user_input': user_input,
            'intent_data': intent_data,
            'workflow': workflow,
            'validation': validation,
            'success': all(validation.values())
        }

    def validate_workflow(self, workflow: Dict[str, Any], intent_data: Dict[str, Any]) -> Dict[str, bool]:
        """Validate the generated workflow"""
        validation = {}
        
        # Check if email was properly extracted
        has_email = len(intent_data['extracted_emails']) > 0
        validation['Email Address Detected'] = has_email
        
        # Check if specific email is found
        target_email = 'slakshanand1105@gmail.com'
        has_target_email = target_email in intent_data['extracted_emails']
        validation[f'Target Email ({target_email}) Found'] = has_target_email
        
        # Check if data fetching is included
        has_data_fetch = any(node['type'] in ['data_source', 'data_processor'] for node in workflow['nodes'])
        validation['Data Fetching Nodes Present'] = has_data_fetch
        
        # Check if email sending is included
        has_email_send = any(node['type'] in ['email_sender', 'email_composer'] for node in workflow['nodes'])
        validation['Email Sending Nodes Present'] = has_email_send
        
        # Check workflow completeness
        has_trigger = any(node['type'] in ['manual_trigger', 'trigger'] for node in workflow['nodes'])
        validation['Workflow Has Trigger'] = has_trigger
        
        # Check if workflow matches intent
        correct_intent = intent_data['intent'] == 'data_email_workflow'
        validation['Correct Intent Detected'] = correct_intent
        
        return validation

def main():
    processor = LocalPromptProcessor()
    
    print("🎯 LOCAL DATA FETCH + EMAIL PROMPT TESTING")
    print("=" * 70)
    
    # Test the specific prompt
    user_prompt = "Fetch data from server and send email to slakshanand1105@gmail.com"
    result = processor.test_specific_prompt(user_prompt)
    
    # Test variations
    print(f"\n" + "=" * 70)
    print("🔄 TESTING PROMPT VARIATIONS")
    print("=" * 70)
    
    variations = [
        "Get customer data from database and email report to slakshanand1105@gmail.com",
        "Retrieve sales data from server and send to slakshanand1105@gmail.com",
        "Pull analytics from API and email summary to slakshanand1105@gmail.com",
        "Extract user logs from system and mail results to slakshanand1105@gmail.com"
    ]
    
    variation_results = []
    for i, variation in enumerate(variations, 1):
        print(f"\n📋 Variation {i}: {variation}")
        print("-" * 40)
        
        var_result = processor.test_specific_prompt(variation)
        variation_results.append(var_result)
    
    # Summary
    print(f"\n" + "=" * 70)
    print("📊 COMPREHENSIVE TESTING SUMMARY")
    print("=" * 70)
    
    # Original prompt results
    original_success = result['success']
    print(f"Original Prompt: {'✅ SUCCESS' if original_success else '❌ FAILED'}")
    
    # Variation results
    successful_variations = sum(1 for r in variation_results if r['success'])
    total_variations = len(variation_results)
    print(f"Variations: {successful_variations}/{total_variations} successful")
    
    # Overall assessment
    if original_success and successful_variations >= total_variations * 0.8:
        print(f"\n🎉 EXCELLENT! Your data fetch + email prompts work perfectly!")
        print(f"📧 Email (slakshanand1105@gmail.com) is consistently detected")
        print(f"📊 Data fetching requirements are properly understood")
        print(f"🔧 Appropriate workflows are being generated")
    elif original_success:
        print(f"\n✅ GOOD! Your main prompt works, variations need refinement")
    else:
        print(f"\n⚠️  NEEDS WORK: The system needs improvement for this type of prompt")
    
    # Save results
    all_results = {
        'original_prompt': result,
        'variations': variation_results,
        'summary': {
            'original_success': original_success,
            'successful_variations': successful_variations,
            'total_variations': total_variations,
            'overall_success_rate': (1 if original_success else 0 + successful_variations) / (1 + total_variations)
        }
    }
    
    with open('local_data_email_test_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: local_data_email_test_results.json")
    
    return all_results

if __name__ == "__main__":
    main()
