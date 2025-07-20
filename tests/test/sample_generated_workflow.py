#!/usr/bin/env python3
"""
DXTR AutoFlow - Sample Generated Workflow JSON
Demonstrates the complete structure of generated workflow scripts
"""

import json
from datetime import datetime

# Example: Complete Generated Workflow JSON
sample_workflow = {
    "workflow_id": "wf_1752812800_303eebe5",
    "name": "High Priority Task Creation with Team Notification",
    "description": "create task using Asana; send message using Slack",
    "created_at": "2024-01-15T10:30:00",
    "template_id": "task_creation_v1",
    "template_used": True,
    "estimated_execution_time": 11,
    "steps": [
        {
            "step_id": "step_1",
            "name": "Step 1: Create Task",
            "driver": "asana_driver",
            "operation": "create_task",
            "parameters": {
                "name": "Fix login bug",
                "priority": "high",
                "project": "current_project",
                "description": "High priority bug fix for login system",
                "assignee": "dev_team_lead",
                "due_date": "2024-01-17"
            },
            "timeout_seconds": 60,
            "retry_policy": {
                "enabled": True,
                "max_retries": 3
            },
            "dependencies": [],
            "variable_substitution": {
                "enabled": True,
                "previous_step_results": False
            }
        },
        {
            "step_id": "step_2", 
            "name": "Step 2: Send Message",
            "driver": "slack_driver",
            "operation": "send_message",
            "parameters": {
                "channel": "#dev-team",
                "message": "🚨 High priority task created: Fix login bug\n📝 Task ID: {step_1.task_id}\n🔗 Link: {step_1.task_url}\n⏰ Due: 2024-01-17",
                "mentions": ["@dev_team_lead", "@qa_lead"]
            },
            "timeout_seconds": 60,
            "retry_policy": {
                "enabled": True,
                "max_retries": 3
            },
            "dependencies": ["step_1"],
            "variable_substitution": {
                "enabled": True,
                "previous_step_results": True,
                "variables": {
                    "step_1.task_id": "Task ID from Asana creation",
                    "step_1.task_url": "Direct link to the created task"
                }
            }
        }
    ],
    "validation": {
        "is_valid": True,
        "warnings": [],
        "errors": []
    },
    "error_handling": {
        "retry_policy": "exponential_backoff",
        "max_retries": 3,
        "timeout_seconds": 300,
        "failure_actions": [
            {
                "condition": "step_1_fails",
                "action": "send_slack_alert",
                "parameters": {
                    "channel": "#alerts",
                    "message": "Failed to create Asana task - manual intervention required"
                }
            }
        ]
    },
    "monitoring": {
        "track_performance": True,
        "log_execution": True,
        "send_completion_notification": True,
        "metrics": {
            "execution_time": True,
            "success_rate": True,
            "step_performance": True
        }
    },
    "metadata": {
        "created_by": "enhanced_mcp_llm",
        "template_confidence": 0.59,
        "original_request": "Create a high priority task in Asana for fixing the login bug and notify the dev team in Slack",
        "parsed_entities": {
            "priority": "high",
            "task_type": "bug_fix", 
            "assignee": "dev_team",
            "notification_channel": "slack"
        }
    }
}

def display_workflow_structure():
    """Display the complete workflow structure with explanations"""
    
    print("🔧 DXTR AutoFlow - Generated Workflow JSON Structure")
    print("=" * 80)
    print("This is what the enhanced MCP LLM generates for execution:\n")
    
    print("📋 Complete Workflow JSON:")
    print(json.dumps(sample_workflow, indent=2))
    
    print("\n" + "=" * 80)
    print("🔍 Key Features of Generated Workflows:")
    print("=" * 80)
    
    features = [
        "✅ Unique workflow ID with timestamp",
        "✅ Descriptive name and description",
        "✅ Template tracking and confidence scoring", 
        "✅ Step-by-step execution plan",
        "✅ Variable substitution between steps",
        "✅ Comprehensive error handling",
        "✅ Retry policies and timeouts",
        "✅ Performance monitoring and logging",
        "✅ Dependency management",
        "✅ Original request context preservation"
    ]
    
    for feature in features:
        print(feature)
    
    print("\n🚀 Execution Ready:")
    print("This JSON can be directly executed by the DXTR AutoFlow engine")
    print("All 31 production drivers are compatible with this format")
    print("Real-time monitoring and error handling included")

if __name__ == "__main__":
    display_workflow_structure()
