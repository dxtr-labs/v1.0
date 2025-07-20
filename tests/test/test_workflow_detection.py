#!/usr/bin/env python3
"""
Test the workflow detection in chat API
"""

import sys
sys.path.append('backend')

def is_workflow_request(user_input: str) -> bool:
    """Determine if the user input is requesting workflow automation"""
    workflow_keywords = [
        'workflow', 'automate', 'automation', 'trigger', 'schedule',
        'email automation', 'data processing', 'webhook', 'api call',
        'create workflow', 'build automation', 'set up trigger',
        # Email-related workflow keywords
        'send email', 'generate email', 'email for', 'send to',
        'sales email', 'marketing email', 'send message'
    ]
    
    user_lower = user_input.lower()
    return any(keyword in user_lower for keyword in workflow_keywords)

# Test the function
user_input = "Use AI to generate a sales email for our product Roomify- Find your roomates for college students and send it to test@example.com. The email should highlight our using our product include a special discount offer, and have a professional tone. Make sure to show me a preview before sending."

print("🧪 Testing workflow detection...")
print(f"User input: {user_input}")
print(f"Is workflow request: {is_workflow_request(user_input)}")

# Check which keywords match
workflow_keywords = [
    'workflow', 'automate', 'automation', 'trigger', 'schedule',
    'email automation', 'data processing', 'webhook', 'api call',
    'create workflow', 'build automation', 'set up trigger',
    'send email', 'generate email', 'email for', 'send to',
    'sales email', 'marketing email', 'send message'
]

user_lower = user_input.lower()
matching_keywords = [keyword for keyword in workflow_keywords if keyword in user_lower]
print(f"Matching keywords: {matching_keywords}")
