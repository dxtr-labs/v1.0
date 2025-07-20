"""
Driver Knowledge Base for Custom MCP LLM System
Contains detailed information about all available drivers and their capabilities.
"""

DRIVER_CAPABILITIES = {
    "email_send": {
        "name": "Email Send Driver",
        "description": "Sends emails with professional formatting and templates",
        "required_parameters": ["toEmail", "subject", "text"],
        "optional_parameters": {
            "cc": "Carbon copy recipients (comma-separated emails)",
            "bcc": "Blind carbon copy recipients (comma-separated emails)", 
            "priority": "Email priority (normal, high, low)",
            "template_style": "Email template style (professional, casual, modern)",
            "sender_name": "Name to display as sender (default: DXTR Labs)"
        },
        "parameter_aliases": {
            "toEmail": ["to", "recipient", "email"],
            "subject": ["title", "subjectLine"],
            "text": ["content", "body", "message", "html"]
        },
        "example": {
            "toEmail": "customer@example.com",
            "subject": "Welcome to Our Service",
            "text": "Thank you for joining us! We're excited to have you as a customer.",
            "template_style": "professional"
        },
        "use_cases": ["Welcome emails", "Notifications", "Marketing campaigns", "Alerts"]
    },
    
    "http_request": {
        "name": "HTTP Request Driver", 
        "description": "Makes HTTP requests to fetch data from APIs and websites",
        "required_parameters": ["url", "method"],
        "optional_parameters": {
            "headers": "HTTP headers as array of {name, value} objects",
            "body": "Request body with type (json/form) and data",
            "timeout": "Request timeout in seconds"
        },
        "methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
        "example": {
            "url": "https://api.example.com/data",
            "method": "GET",
            "headers": [{"name": "Authorization", "value": "Bearer token"}]
        },
        "use_cases": ["API data fetching", "Website scraping", "Third-party integrations", "Status checks"]
    },
    
    "openai": {
        "name": "OpenAI Driver",
        "description": "Generates AI content using OpenAI GPT models for text processing and creation",
        "required_parameters": ["prompt"],
        "optional_parameters": {
            "model": "OpenAI model to use (gpt-3.5-turbo, gpt-4, etc.)",
            "context": "System context for the AI",
            "max_tokens": "Maximum tokens for response",
            "temperature": "AI creativity level (0.0-2.0)"
        },
        "example": {
            "prompt": "Summarize this data: {{previous_node_output}}",
            "model": "gpt-3.5-turbo",
            "context": "You are a data analyst creating concise summaries",
            "max_tokens": 500,
            "temperature": 0.3
        },
        "use_cases": ["Text summarization", "Content generation", "Data analysis", "Translation"]
    },
    
    "email_read_imap": {
        "name": "Email Read IMAP Driver",
        "description": "Reads emails from IMAP email accounts",
        "required_parameters": ["imap_server", "username", "password"],
        "optional_parameters": {
            "port": "IMAP port (default: 993)",
            "folder": "Email folder to read from (default: INBOX)",
            "limit": "Number of emails to fetch",
            "filter": "Filter criteria for emails"
        },
        "example": {
            "imap_server": "imap.gmail.com",
            "username": "user@gmail.com", 
            "password": "app_password",
            "folder": "INBOX",
            "limit": 10
        },
        "use_cases": ["Email monitoring", "Customer support automation", "Data extraction from emails"]
    },
    
    "cron": {
        "name": "Cron Scheduler Driver",
        "description": "Schedules workflow execution based on time patterns",
        "required_parameters": ["schedule"],
        "optional_parameters": {
            "timezone": "Timezone for schedule execution",
            "max_runs": "Maximum number of executions"
        },
        "schedule_formats": [
            "0 9 * * MON-FRI (9 AM weekdays)",
            "0 0 1 * * (1st of every month)",
            "*/15 * * * * (every 15 minutes)"
        ],
        "example": {
            "schedule": "0 9 * * *",
            "timezone": "UTC"
        },
        "use_cases": ["Daily reports", "Scheduled notifications", "Maintenance tasks", "Recurring processes"]
    },
    
    "if_else": {
        "name": "Conditional Logic Driver",
        "description": "Implements conditional branching in workflows",
        "required_parameters": ["condition"],
        "optional_parameters": {
            "true_path": "Nodes to execute if condition is true",
            "false_path": "Nodes to execute if condition is false"
        },
        "condition_types": ["equals", "contains", "greater_than", "less_than", "exists"],
        "example": {
            "condition": {
                "type": "contains",
                "field": "{{email_subject}}",
                "value": "urgent"
            }
        },
        "use_cases": ["Smart routing", "Data validation", "Error handling", "Business logic"]
    },
    
    "loop_items": {
        "name": "Loop Iterator Driver", 
        "description": "Iterates over arrays and processes each item",
        "required_parameters": ["items"],
        "optional_parameters": {
            "batch_size": "Number of items to process at once",
            "max_iterations": "Maximum number of iterations"
        },
        "example": {
            "items": "{{customer_list}}",
            "batch_size": 5
        },
        "use_cases": ["Bulk processing", "Data transformation", "Multi-recipient communications"]
    },
    
    "webhook": {
        "name": "Webhook Driver",
        "description": "Receives HTTP webhook calls to trigger workflows",
        "required_parameters": ["endpoint"],
        "optional_parameters": {
            "method": "HTTP method to accept (GET, POST, etc.)",
            "authentication": "Authentication requirements",
            "response": "Custom response to send back"
        },
        "example": {
            "endpoint": "/customer-signup",
            "method": "POST",
            "response": "Webhook received successfully"
        },
        "use_cases": ["External system integration", "Real-time triggers", "Event-driven automation"]
    },
    
    "twilio_sms": {
        "name": "Twilio SMS Driver",
        "description": "Sends SMS messages using Twilio service",
        "required_parameters": ["to", "message"],
        "optional_parameters": {
            "from": "Twilio phone number to send from",
            "media_url": "URL of media to include in message"
        },
        "example": {
            "to": "+1234567890",
            "message": "Your order has been confirmed!",
            "from": "+1987654321"
        },
        "use_cases": ["SMS notifications", "Two-factor authentication", "Alerts", "Customer communication"]
    },
    
    "claude": {
        "name": "Claude AI Driver",
        "description": "Generates AI content using Anthropic's Claude model",
        "required_parameters": ["prompt"],
        "optional_parameters": {
            "model": "Claude model version",
            "max_tokens": "Maximum tokens for response",
            "temperature": "AI creativity level"
        },
        "example": {
            "prompt": "Analyze this customer feedback: {{feedback_text}}",
            "max_tokens": 1000,
            "temperature": 0.5
        },
        "use_cases": ["Text analysis", "Content creation", "Data interpretation", "Customer service"]
    }
}

WORKFLOW_TEMPLATES = {
    "email_notification": {
        "name": "Simple Email Notification",
        "description": "Send a single email notification",
        "nodes": [
            {
                "id": "email_1",
                "type": "email_send", 
                "parameters": {
                    "toEmail": "",
                    "subject": "",
                    "text": ""
                }
            }
        ]
    },
    
    "fetch_and_email": {
        "name": "Fetch Data and Email Summary",
        "description": "Fetch data from API, process with AI, and email summary",
        "nodes": [
            {
                "id": "fetch_1",
                "type": "http_request",
                "parameters": {
                    "url": "",
                    "method": "GET"
                }
            },
            {
                "id": "ai_process_1", 
                "type": "openai",
                "parameters": {
                    "prompt": "Summarize this data: {{fetch_1.output}}",
                    "context": "You are a data analyst creating concise summaries"
                }
            },
            {
                "id": "email_1",
                "type": "email_send",
                "parameters": {
                    "toEmail": "",
                    "subject": "Data Summary Report",
                    "text": "{{ai_process_1.output}}"
                }
            }
        ]
    },
    
    "scheduled_report": {
        "name": "Scheduled Report Generation", 
        "description": "Generate and email reports on a schedule",
        "nodes": [
            {
                "id": "schedule_1",
                "type": "cron",
                "parameters": {
                    "schedule": "0 9 * * MON-FRI"
                }
            },
            {
                "id": "fetch_1",
                "type": "http_request", 
                "parameters": {
                    "url": "",
                    "method": "GET"
                }
            },
            {
                "id": "ai_process_1",
                "type": "openai",
                "parameters": {
                    "prompt": "Create a daily report from this data: {{fetch_1.output}}",
                    "context": "You are creating professional daily reports"
                }
            },
            {
                "id": "email_1",
                "type": "email_send",
                "parameters": {
                    "toEmail": "",
                    "subject": "Daily Report - {{current_date}}",
                    "text": "{{ai_process_1.output}}"
                }
            }
        ]
    },
    
    "apology_email": {
        "name": "AI-Generated Apology Email",
        "description": "Generate personalized apology email for missed events",
        "nodes": [
            {
                "id": "ai_generate_1",
                "type": "openai",
                "parameters": {
                    "prompt": "Write a professional apology email for missing an event. Event details: {{event_details}}. Customer name: {{customer_name}}",
                    "context": "You are writing sincere, professional apology emails for a company",
                    "temperature": 0.7
                }
            },
            {
                "id": "email_1", 
                "type": "email_send",
                "parameters": {
                    "toEmail": "{{customer_email}}",
                    "subject": "Sincere Apologies - {{event_name}}",
                    "text": "{{ai_generate_1.output}}",
                    "template_style": "professional"
                }
            }
        ]
    }
}

def get_driver_info(driver_type: str) -> dict:
    """Get detailed information about a specific driver."""
    return DRIVER_CAPABILITIES.get(driver_type, {})

def get_required_parameters(driver_type: str) -> list:
    """Get required parameters for a driver."""
    driver_info = get_driver_info(driver_type)
    return driver_info.get("required_parameters", [])

def get_workflow_template(template_name: str) -> dict:
    """Get a workflow template by name."""
    return WORKFLOW_TEMPLATES.get(template_name, {})

def list_available_drivers() -> list:
    """List all available driver types."""
    return list(DRIVER_CAPABILITIES.keys())

def find_suitable_drivers(use_case: str) -> list:
    """Find drivers suitable for a specific use case."""
    suitable = []
    use_case_lower = use_case.lower()
    
    for driver_type, info in DRIVER_CAPABILITIES.items():
        if any(use_case_lower in uc.lower() for uc in info.get("use_cases", [])):
            suitable.append({
                "type": driver_type,
                "name": info["name"], 
                "description": info["description"]
            })
    
    return suitable
