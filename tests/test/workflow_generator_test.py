import json
import random
from datetime import datetime, timedelta
import uuid  # Impo        # Add a placeholder action for webhook
        workflow["workflow"]["actions"].append({
            "node": "httpRequest", 
            "parameters": {
                "url": "https://example.com/process_webhook_data", 
                "method": "POST", 
                "body": "{{$json.webhook_payload}}"
            }
        }) uuid for generating unique IDs

def generate_conceptual_workflow(intent_type, details):
    """Generates a conceptual JSON workflow based on intent and details."""
    workflow = {
        "workflow": {
            "trigger": {"node": "manual", "parameters": {}}, # Default trigger for LLM output
            "logic": [],
            "actions": []
        }
    }

    if intent_type == "email_send":
        workflow["workflow"]["actions"].append({
            "node": "emailSend",
            "parameters": {
                "toEmail": details.get("recipient", "user_email"),
                "subject": details.get("subject", "Automated Message"),
                "text": details.get("body", "This is an automated message.")
            }
        })
    elif intent_type == "http_request":
        workflow["workflow"]["actions"].append({
            "node": "httpRequest",
            "parameters": {
                "url": details.get("url", "api_endpoint"),
                "method": details.get("method", "GET"),
                "headers": details.get("headers", []),
                "body": details.get("body", {})
            }
        })
    elif intent_type == "twilio_message":
        workflow["workflow"]["actions"].append({
            "node": "twilio",
            "parameters": {
                "to": details.get("phone_number", "user_phone_number"),
                "message": details.get("message", "Automated notification."),
                "toWhatsapp": details.get("to_whatsapp", False)
            }
        })
    elif intent_type == "email_read_imap":
        workflow["workflow"]["actions"].append({
            "node": "emailReadImap",
            "parameters": {
                "mailbox": details.get("mailbox", "INBOX"),
                "postProcessAction": details.get("post_process_action", "read"),
                "format": details.get("format", "simple"),
                "options": details.get("options", {})
            }
        })
    elif intent_type == "database_query":
        workflow["workflow"]["actions"].append({
            "node": "DatabaseQuery",
            "parameters": {
                "sql_query": details.get("query", "SELECT * FROM table"),
                "query_params": details.get("query_params", {})
            }
        })
    elif intent_type == "llm_generate_content":
        workflow["workflow"]["actions"].append({
            "node": "LLMGenerateContent",
            "parameters": {
                "prompt": details.get("prompt", "Summarize this content."),
                "input_data_path": details.get("input_path", "raw_data"),
                "output_key": details.get("output_key", "summary")
            }
        })
    elif intent_type == "cron_trigger":
        workflow["workflow"]["trigger"] = {
            "node": "cron",
            "parameters": {
                "hour": details.get("hour", 9),
                "minute": details.get("minute", 0),
                "weekday": details.get("weekday", "*")
            }
        }
        # Add a placeholder action for cron
        workflow["workflow"]["actions"].append({"node": "emailSend", "parameters": {"toEmail": "admin@example.com", "subject": "Daily Report Triggered", "text": "This is a daily report."}})
    elif intent_type == "webhook_trigger":
        workflow["workflow"]["trigger"] = {
            "node": "webhook",
            "parameters": {
                "path": details.get("path", "/incoming_event"),
                "method": details.get("method", "POST")
            }
        }
        # Add a placeholder action for webhook
        workflow["workflow"]["actions"].append({"node": "httpRequest", "parameters": {"url": "https://example.com/process_webhook_data", "method": "POST", "body": "{{$json.webhook_payload}}"}}})
    elif intent_type == "if_else":
        workflow["workflow"]["logic"].append({
            "node": "ifElse",
            "parameters": {
                "condition": details.get("condition", "{{$json.status == 'success'}}"),
                "truePath": details.get("true_path", [{"node": "emailSend", "parameters": {"toEmail": "success@example.com", "subject": "Success"}}]),
                "falsePath": details.get("false_path", [{"node": "emailSend", "parameters": {"toEmail": "failure@example.com", "subject": "Failure"}}])
            }
        })
        # Add a placeholder action if logic is top-level
        if not workflow["workflow"]["actions"]:
             workflow["workflow"]["actions"].append({"node": "emailSend", "parameters": {"toEmail": "placeholder@example.com", "subject": "Logic Test", "text": "Workflow with logic."}})
    elif intent_type == "loop_items":
        workflow["workflow"]["logic"].append({
            "node": "loopItems",
            "parameters": {
                "items": details.get("items_expression", "{{$node['GetData'].json.list_of_items}}"),
                "loopBody": details.get("loop_body", [{"node": "emailSend", "parameters": {"toEmail": "{{$json.item.email}}", "subject": "Item Processed", "text": "Processing item: {{$json.item.name}}"}}])
            }
        })
        # Add a placeholder action if logic is top-level
        if not workflow["workflow"]["actions"]:
             workflow["workflow"]["actions"].append({"node": "emailSend", "parameters": {"toEmail": "placeholder@example.com", "subject": "Loop Test", "text": "Workflow with loop."}})
    elif intent_type == "call":
        workflow["workflow"]["actions"].append({
            "node": "call",
            "parameters": {
                "to": details.get("to_number", "+1234567890"),
                "from": details.get("from_number", "your_twilio_number"),
                "message": details.get("message", "This is an automated call.")
            }
        })
    elif intent_type == "conversational_call":
        workflow["workflow"]["actions"].append({
            "node": "conversationalCall",
            "parameters": {
                "to": details.get("to_number", "+1234567890"),
                "from": details.get("from_number", "your_twilio_number"),
                "voiceWebhookUrl": details.get("webhook_url", "https://your-domain.com/api/twilio/voice_webhook"),
                "initialMessage": details.get("initial_message", "Hello, how can I help you today?")
            }
        })
    elif intent_type == "sms_read":
        workflow["workflow"]["actions"].append({
            "node": "SMSRead",
            "parameters": {
                "phoneNumber": details.get("phone_number", "+1234567890"),
                "direction": details.get("direction", "inbound"),
                "messageContains": details.get("contains", "invoice")
            }
        })
    
    return workflow

# --- Prompt and Detail Generators ---

def get_email_prompts():
    prompts = [
        "Send an email to {recipient} with the subject '{subject}' and body '{body}'.",
        "Draft an email for {recipient} titled '{subject}' saying '{body}'.",
        "Can you send a quick email to {recipient} about '{subject}'? The message is '{body}'.",
        "Automate sending an email to {recipient} with the subject '{subject}' and body '{body}'.",
        "I need to send an email. Recipient: {recipient}, Subject: {subject}, Body: {body}.",
    ]
    details = [
        {"recipient": "sales@example.com", "subject": "New Lead Inquiry", "body": "We received a new lead. Please follow up."},
        {"recipient": "support@company.com", "subject": "Issue Reported", "body": "A customer reported an issue with their service."},
        {"recipient": "team@myorg.com", "subject": "Daily Standup Reminder", "body": "Don't forget the daily standup at 9 AM."},
    ]
    return [(p.format(**d), generate_conceptual_workflow("email_send", d)) for p in prompts for d in details]

def get_http_prompts():
    prompts = [
        "Make a GET request to {url}.",
        "Send a POST request to {url} with body {body}.",
        "Update data at {url} using a PUT request with {body}.",
        "Fetch user data from {url} with headers {headers}.",
        "Delete record at {url} with DELETE method.",
    ]
    details = [
        {"url": "https://api.crm.com/leads", "method": "GET"},
        {"url": "https://api.inventory.com/products", "method": "POST", "body": {"name": "New Product", "price": 100}},
        {"url": "https://api.userdb.com/users/123", "method": "PUT", "body": {"status": "active"}},
        {"url": "https://api.analytics.com/data", "method": "GET", "headers": [{"name": "Authorization", "value": "Bearer token"}]},
    ]
    return [(p.format(**d), generate_conceptual_workflow("http_request", d)) for p in prompts for d in details]

def get_twilio_prompts():
    prompts = [
        "Send an SMS to {phone_number} saying '{message}'.",
        "Text {phone_number} with the message '{message}'.",
        "Send a WhatsApp message to {phone_number}: '{message}'.",
        "Notify {phone_number} via SMS: '{message}'.",
    ]
    details = [
        {"phone_number": "+1234567890", "message": "Your order has shipped!"},
        {"phone_number": "+1987654321", "message": "Meeting reminder: 3 PM today."},
        {"phone_number": "+1122334455", "message": "Your support ticket has been updated.", "to_whatsapp": True},
    ]
    return [(p.format(**d), generate_conceptual_workflow("twilio_message", d)) for p in prompts for d in details]

def get_email_read_prompts():
    prompts = [
        "Read new emails from my {mailbox}.",
        "Check {mailbox} for unread messages.",
        "Process emails in {mailbox} and mark them as {post_process_action}.",
        "Get emails from {mailbox} and extract details in {format} format.",
    ]
    details = [
        {"mailbox": "INBOX", "post_process_action": "read", "format": "simple"},
        {"mailbox": "Quotes", "post_process_action": "read", "format": "resolved", "options": {"subject_contains": "quotation"}},
        {"mailbox": "Support", "post_process_action": "delete", "format": "simple"},
    ]
    return [(p.format(**d), generate_conceptual_workflow("email_read_imap", d)) for p in prompts for d in details]

def get_database_query_prompts():
    prompts = [
        "Fetch all users from the 'users' table.",
        "Get customer details for ID {customer_id} from the 'customers' table.",
        "Select recent orders from 'orders' table where status is '{status}'.",
        "Retrieve product inventory for product '{product_name}'.",
    ]
    details = [
        {"query": "SELECT * FROM users", "query_params": {}},
        {"query": "SELECT * FROM customers WHERE id = $1", "query_params": {"customer_id": "dynamic_id"}},
        {"query": "SELECT * FROM orders WHERE status = $1", "query_params": {"status": "pending"}},
        {"query": "SELECT quantity FROM products WHERE name = $1", "query_params": {"product_name": "dynamic_product"}},
    ]
    return [(p.format(**d), generate_conceptual_workflow("database_query", d)) for p in prompts for d in details]

def get_llm_generate_content_prompts():
    prompts = [
        "Summarize the following text: '{text_to_summarize}'",
        "Generate a TLDR for the email body: '{email_body}'.",
        "Draft a sales pitch based on these points: '{points}'.",
        "Create a daily report summary from the data: '{data}'.",
    ]
    details = [
        {"text_to_summarize": "{{$node['PreviousNode'].json.long_text}}", "prompt": "Summarize this:", "input_path": "long_text", "output_key": "summary"},
        {"email_body": "{{$node['EmailRead'].json.body}}", "prompt": "TLDR for email:", "input_path": "body", "output_key": "tldr"},
        {"points": "{{$json.sales_points}}", "prompt": "Draft sales pitch from:", "input_path": "sales_points", "output_key": "sales_pitch"},
        {"data": "{{$node['DatabaseQuery'].json.report_data}}", "prompt": "Generate daily report from:", "input_path": "report_data", "output_key": "daily_report"},
    ]
    return [(p.format(**d), generate_conceptual_workflow("llm_generate_content", d)) for p in prompts for d in details]

def get_cron_prompts():
    prompts = [
        "Run a workflow daily at {hour}:{minute}.",
        "Schedule a task every weekday at {hour}:{minute}.",
        "Execute this automation every {day_of_month}th of the month at {hour}:{minute}.",
    ]
    details = [
        {"hour": 9, "minute": 0, "weekday": "*", "day_of_month": "*"},
        {"hour": 10, "minute": 30, "weekday": "1-5", "day_of_month": "*"},
        {"hour": 14, "minute": 0, "weekday": "*", "day_of_month": 1},
    ]
    return [(p.format(**d), generate_conceptual_workflow("cron_trigger", d)) for p in prompts for d in details]

def get_webhook_prompts():
    prompts = [
        "Create a webhook listener for new lead signups at path {path}.",
        "Set up a webhook to receive payment notifications at {path} using {method} method.",
        "Listen for events at {path} via POST requests.",
    ]
    details = [
        {"path": "/new_lead", "method": "POST"},
        {"path": "/payment_status", "method": "POST"},
        {"path": "/order_update", "method": "PUT"},
    ]
    return [(p.format(**d), generate_conceptual_workflow("webhook_trigger", d)) for p in prompts for d in details]

def get_if_else_prompts():
    prompts = [
        "If {condition}, then {true_action}, otherwise {false_action}.",
        "Check if {condition}. If true, {true_action}. Else, {false_action}.",
        "Run {true_action} if {condition} is met, otherwise run {false_action}.",
    ]
    details = [
        {"condition": "{{$json.amount > 100}}", "true_action": "send an email to manager", "false_action": "log a message"},
        {"condition": "{{$json.status == 'completed'}}", "true_action": "update CRM", "false_action": "send a reminder"},
    ]
    # Convert actions to conceptual nodes
    converted_prompts = []
    for p in prompts:
        for d in details:
            true_node = {"node": "emailSend", "parameters": {"toEmail": "manager@example.com", "subject": "Action Needed", "text": "Condition met."}} if "email to manager" in d["true_action"] else {"node": "httpRequest", "parameters": {"url": "crm_api", "method": "POST", "body": {"update": "true"}}} if "update CRM" in d["true_action"] else {"node": "log", "parameters": {"message": "True path executed"}}
            false_node = {"node": "log", "parameters": {"message": "Condition not met."}} if "log a message" in d["false_action"] else {"node": "emailSend", "parameters": {"toEmail": "user@example.com", "subject": "Reminder", "text": "Reminder sent."}} if "send a reminder" in d["false_action"] else {"node": "log", "parameters": {"message": "False path executed"}}
            
            converted_prompts.append((
                p.format(**d),
                generate_conceptual_workflow("if_else", {
                    "condition": d["condition"],
                    "true_path": [true_node],
                    "false_path": [false_node]
                })
            ))
    return converted_prompts

def get_loop_items_prompts():
    prompts = [
        "For each {item_type} in {list_source}, {action_per_item}.",
        "Iterate over {list_source} and {action_per_item} for each entry.",
        "Process every {item_type} from {list_source} by {action_per_item}.",
    ]
    details = [
        {"item_type": "user", "list_source": "{{$node['GetUsers'].json.users}}", "action_per_item": "send a welcome email"},
        {"item_type": "order", "list_source": "{{$node['GetOrders'].json.orders}}", "action_per_item": "update its status in CRM"},
    ]
    # Convert actions to conceptual nodes
    converted_prompts = []
    for p in prompts:
        for d in details:
            loop_body_node = {"node": "emailSend", "parameters": {"toEmail": "{{$json.item.email}}", "subject": "Welcome", "text": "Welcome!"}} if "welcome email" in d["action_per_item"] else {"node": "httpRequest", "parameters": {"url": "crm_api/order/{{$json.item.id}}", "method": "PUT", "body": {"status": "processed"}}}
            converted_prompts.append((
                p.format(**d),
                generate_conceptual_workflow("loop_items", {
                    "items_expression": d["list_source"],
                    "loop_body": [loop_body_node]
                })
            ))
    return converted_prompts

def get_call_prompts():
    prompts = [
        "Call {to_number} and play the message '{message}'.",
        "Make an automated call to {to_number} and say '{message}'.",
        "Initiate a phone call to {to_number} with the voice message '{message}'.",
    ]
    details = [
        {"to_number": "+1234567890", "message": "Your appointment is confirmed."},
        {"to_number": "+1987654321", "message": "This is a test call from your automation platform."},
    ]
    return [(p.format(**d), generate_conceptual_workflow("call", d)) for p in prompts for d in details]

def get_conversational_call_prompts():
    prompts = [
        "Create a conversational phone agent that calls {to_number} for customer support.",
        "Deploy a 24/7 AI voice agent to handle calls to {to_number} starting with '{initial_message}'.",
        "Set up an interactive phone call agent for {to_number} to confirm details.",
    ]
    details = [
        {"to_number": "+15551112222", "initial_message": "Hello, how can I assist you today?"},
        {"to_number": "+1800SUPPORT", "initial_message": "Welcome to our support line."},
    ]
    return [(p.format(**d), generate_conceptual_workflow("conversational_call", {**d, "webhook_url": "https://your-domain.com/api/twilio/voice_webhook"})) for p in prompts for d in details]

def get_sms_read_prompts():
    prompts = [
        "Read all inbound SMS messages from {phone_number}.",
        "Find messages from {phone_number} that contain '{contains_text}'.",
        "Get all outbound SMS messages sent to {phone_number} yesterday.",
    ]
    details = [
        {"phone_number": "+1234567890", "direction": "inbound"},
        {"phone_number": "+1987654321", "contains_text": "order confirmation"},
        {"phone_number": "+1122334455", "direction": "outbound", "date_after": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")},
    ]
    return [(p.format(**d), generate_conceptual_workflow("sms_read", d)) for p in prompts for d in details]


# --- Complex Scenarios (Combining multiple drivers) ---

def get_prr_travels_prompts():
    prompts = [
        "For PRR TRAVELS: Get gas inputs from the tracker, verify with the bill received via email, and if there's an error, send an email to operations.",
        "For PRR TRAVELS: Compare the assigned distance for a vehicle with its actual traveled distance from the tracker. If it exceeds, send an SMS to the admin team.",
        "For PRR TRAVELS: Send a personalized email and an SMS reminder to customers 24 hours before their travel.",
        "For PRR TRAVELS: Constantly read emails from ds@prrtravels.com for 'vehicle needs' or 'quotation requests', extract details, and email the driver team manager.",
        "PRR TRAVELS: Automate daily fuel data reconciliation. Fetch tracker data, read email bills, use AI to extract amounts, compare, and alert if discrepancies.",
        "PRR TRAVELS: Before each trip, send a confirmation email with details from the database and a quick SMS reminder."
    ]
    # These are high-level, the LLM needs to break them down into multiple nodes.
    # The 'output' here is a simplified conceptual representation.
    outputs = [
        {
            "workflow": {
                "trigger": {"node": "cron", "parameters": {"hour": 2, "minute": 0}}, # Daily check
                "actions": [
                    {"node": "httpRequest", "parameters": {"url": "tracker_api/fuel", "method": "GET", "output_key": "tracker_fuel_data"}},
                    {"node": "emailReadImap", "parameters": {"mailbox": "bills@prrtravels.com", "postProcessAction": "read", "format": "simple", "output_key": "bill_email"}},
                    {"node": "LLMGenerateContent", "parameters": {"prompt": "Extract amount and vehicle ID from this email: {{$node['emailReadImap'].json.body}}", "input_data_path": "bill_email.body", "output_key": "extracted_bill_data"}},
                    {"node": "ifElse", "parameters": {
                        "condition": "{{$node['httpRequest'].json.tracker_fuel_data.gas_input != $node['LLMGenerateContent'].json.extracted_bill_data.amount}}",
                        "truePath": [{"node": "emailSend", "parameters": {"toEmail": "operations@prrtravels.com", "subject": "Fuel Discrepancy Alert", "text": "Details: {{$json.discrepancy_details}}"}}],
                        "falsePath": [{"node": "log", "parameters": {"message": "Fuel data matched."}}]
                    }}
                ]
            }
        },
        {
            "workflow": {
                "trigger": {"node": "cron", "parameters": {"hour": 23, "minute": 59}}, # End of day check
                "actions": [
                    {"node": "DatabaseQuery", "parameters": {"sql_query": "SELECT assigned_distance FROM vehicle_assignments WHERE vehicle_id = '{{$json.vehicle_id}}'", "output_key": "assigned_distance"}},
                    {"node": "httpRequest", "parameters": {"url": "tracker_api/distance/{{$json.vehicle_id}}", "method": "GET", "output_key": "actual_distance"}},
                    {"node": "ifElse", "parameters": {
                        "condition": "{{$node['actual_distance'].json.distance > $node['assigned_distance'].json.distance_limit}}",
                        "truePath": [{"node": "twilio", "parameters": {"to": "admin_phone_number", "message": "Vehicle {{$json.vehicle_id}} exceeded distance limit."}}],
                        "falsePath": [{"node": "log", "parameters": {"message": "Distance within limits."}}]
                    }}
                ]
            }
        },
        {
            "workflow": {
                "trigger": {"node": "cron", "parameters": {"hour": 8, "minute": 0}}, # Example: 8 AM daily, then filter by travel date
                "actions": [
                    {"node": "DatabaseQuery", "parameters": {"sql_query": "SELECT * FROM upcoming_travels WHERE travel_date = CURRENT_DATE + INTERVAL '1 day'", "output_key": "upcoming_travels"}},
                    {"node": "loopItems", "parameters": {
                        "items": "{{$node['DatabaseQuery'].json.upcoming_travels}}",
                        "loopBody": [
                            {"node": "emailSend", "parameters": {"toEmail": "{{$json.item.customer_email}}", "subject": "Your Upcoming Trip Reminder", "text": "Details: {{$json.item.details}}."}},
                            {"node": "twilio", "parameters": {"to": "{{$json.item.customer_phone}}", "message": "Reminder: Your trip is tomorrow! Details: {{$json.item.details}}"}}
                        ]
                    }}
                ]
            }
        },
        {
            "workflow": {
                "trigger": {"node": "cron", "parameters": {"hour": 0, "minute": 5}}, # Frequent check
                "actions": [
                    {"node": "emailReadImap", "parameters": {"mailbox": "ds@prrtravels.com", "postProcessAction": "read", "format": "simple", "options": {"subject_contains_any": ["needs", "quotation"]}}},
                    {"node": "LLMGenerateContent", "parameters": {"prompt": "Extract vehicle needs or quotation request details from this email: {{$node['emailReadImap'].json.body}}", "input_data_path": "body", "output_key": "extracted_details"}},
                    {"node": "emailSend", "parameters": {"toEmail": "driverteam_manager@prrtravels.com", "subject": "New Vehicle/Quotation Request", "text": "Details: {{$node['LLMGenerateContent'].json.extracted_details}}"}}
                ]
            }
        },
        {
             "workflow": {
                "trigger": {"node": "cron", "parameters": {"hour": 3, "minute": 0}},
                "actions": [
                    {"node": "httpRequest", "parameters": {"url": "tracker_api/daily_fuel_data", "method": "GET", "output_key": "tracker_data"}},
                    {"node": "emailReadImap", "parameters": {"mailbox": "fuel_bills@prrtravels.com", "postProcessAction": "read", "format": "simple", "output_key": "bill_emails"}},
                    {"node": "loopItems", "parameters": {
                        "items": "{{$node['bill_emails'].json.emails}}",
                        "loopBody": [
                            {"node": "LLMGenerateContent", "parameters": {"prompt": "Extract bill amount and date from: {{$json.item.body}}", "input_data_path": "item.body", "output_key": "extracted_bill"}},
                            {"node": "ifElse", "parameters": {
                                "condition": "{{$node['tracker_data'].json.fuel_for_date[$node['extracted_bill'].json.date] != $node['extracted_bill'].json.amount}}",
                                "truePath": [{"node": "emailSend", "parameters": {"toEmail": "finance@prrtravels.com", "subject": "Fuel Discrepancy", "text": "Discrepancy found for date {{$node['extracted_bill'].json.date}}"}}],
                                "falsePath": [{"node": "log", "parameters": {"message": "Fuel bill matched for {{$node['extracted_bill'].json.date}}."}}]
                            }}
                        ]
                    }}
                ]
            }
        },
        {
            "workflow": {
                "trigger": {"node": "manual", "parameters": {}},
                "actions": [
                    {"node": "DatabaseQuery", "parameters": {"sql_query": "SELECT customer_email, customer_phone, trip_details FROM trip_bookings WHERE booking_id = '{{$json.booking_id}}'", "output_key": "trip_info"}},
                    {"node": "emailSend", "parameters": {"toEmail": "{{$node['trip_info'].json.customer_email}}", "subject": "Your Trip Confirmation", "text": "Details: {{$node['trip_info'].json.trip_details}}"}},
                    {"node": "twilio", "parameters": {"to": "{{$node['trip_info'].json.customer_phone}}", "message": "Your trip is confirmed! Check email for details."}}
                ]
            }
        }
    ]
    return list(zip(prompts, outputs))


def generate_prompts():
    all_prompts = []

    # Simple prompts for each core driver
    all_prompts.extend(get_email_prompts())
    all_prompts.extend(get_http_prompts())
    all_prompts.extend(get_twilio_prompts())
    all_prompts.extend(get_email_read_prompts())
    all_prompts.extend(get_database_query_prompts())
    all_prompts.extend(get_llm_generate_content_prompts())
    all_prompts.extend(get_cron_prompts())
    all_prompts.extend(get_webhook_prompts())
    all_prompts.extend(get_if_else_prompts())
    all_prompts.extend(get_loop_items_prompts())
    all_prompts.extend(get_call_prompts())
    all_prompts.extend(get_conversational_call_prompts())
    all_prompts.extend(get_sms_read_prompts())

    # Add specific PRR Travels use cases
    all_prompts.extend(get_prr_travels_prompts())

    # Generate more complex combinations to reach 1500
    # This part will combine random elements to create diverse scenarios
    core_actions = [
        {"node": "emailSend", "params": {"toEmail": "random@example.com", "subject": "Generated Email", "text": "Test."}},
        {"node": "httpRequest", "params": {"url": "https://api.random.com/data", "method": "GET"}},
        {"node": "twilio", "params": {"to": "+10000000000", "message": "Generated SMS."}},
        {"node": "DatabaseQuery", "params": {"sql_query": "SELECT 1", "query_params": {}}},
        {"node": "LLMGenerateContent", "params": {"prompt": "Generate a short text.", "output_key": "short_text"}},
    ]
    
    for _ in range(1500 - len(all_prompts)): # Aim for 1500 total
        num_actions = random.randint(1, 3)
        actions = []
        prompt_parts = []
        
        # Add random actions
        for i in range(num_actions):
            action_choice = random.choice(core_actions)
            action_node = action_choice["node"]
            action_params = action_choice["params"].copy() # Copy to avoid modifying original

            # Add dynamic elements if applicable
            if action_node == "emailSend":
                action_params["toEmail"] = f"user{random.randint(1,100)}@example.com"
                action_params["subject"] = f"Automated Subject {random.randint(1,100)}"
                action_params["text"] = f"This is a message for user {random.randint(1,100)}."
                prompt_parts.append(f"send an email to {action_params['toEmail']} about {action_params['subject']}")
            elif action_node == "httpRequest":
                action_params["url"] = f"https://api.example.com/resource/{random.randint(1,100)}"
                action_params["method"] = random.choice(["GET", "POST", "PUT"])
                prompt_parts.append(f"make a {action_params['method']} request to {action_params['url']}")
            elif action_node == "twilio":
                action_params["to"] = f"+1{random.randint(1000000000, 9999999999)}"
                action_params["message"] = f"Alert {random.randint(1,100)}."
                prompt_parts.append(f"send an SMS to {action_params['to']} saying {action_params['message']}")
            elif action_node == "DatabaseQuery":
                action_params["sql_query"] = f"SELECT * FROM table_{random.randint(1,5)} WHERE id = '{uuid.uuid4()}'"
                prompt_parts.append(f"fetch data from database using query {action_params['sql_query']}")
            elif action_node == "LLMGenerateContent":
                action_params["prompt"] = f"Summarize the following: '{{$node['prev_node'].json.data_{random.randint(1,5)}}}'"
                action_params["input_data_path"] = f"prev_node.data_{random.randint(1,5)}"
                action_params["output_key"] = f"summary_{random.randint(1,5)}"
                prompt_parts.append(f"summarize some data using AI and store it as {action_params['output_key']}")

            actions.append({"node": action_node, "parameters": action_params})
        
        # Add optional trigger
        trigger_choice = random.choice(["manual", "cron", "webhook"])
        trigger_node = {"node": "manual", "parameters": {}}
        if trigger_choice == "cron":
            trigger_node = {"node": "cron", "parameters": {"hour": random.randint(0,23), "minute": random.randint(0,59)}}
            prompt_parts.insert(0, f"Daily at {trigger_node['parameters']['hour']}:{trigger_node['parameters']['minute']},")
        elif trigger_choice == "webhook":
            trigger_node = {"node": "webhook", "parameters": {"path": f"/event/{random.randint(1,100)}"}}
            prompt_parts.insert(0, f"When an event comes to webhook {trigger_node['parameters']['path']},")

        # Add optional logic
        if random.random() < 0.3: # 30% chance of adding if/else
            condition_expr = random.choice(["{{$json.value > 100}}", "{{$json.status == 'active'}}", "{{$json.count < 5}}"])
            true_action_node = random.choice(core_actions)
            false_action_node = random.choice(core_actions)
            
            logic_node = {
                "node": "ifElse",
                "parameters": {
                    "condition": condition_expr,
                    "truePath": [{"node": true_action_node["node"], "parameters": true_action_node["params"]}],
                    "falsePath": [{"node": false_action_node["node"], "parameters": false_action_node["params"]}]
                }
            }
            workflow_obj = {
                "workflow": {
                    "trigger": trigger_node,
                    "logic": [logic_node],
                    "actions": actions # Actions might be before or after logic, for simplicity put after
                }
            }
            prompt_parts.append(f"and if {condition_expr.replace('{{', '').replace('}}', '')}, then perform an action.")
        elif random.random() < 0.1: # 10% chance of adding loop
            items_expr = random.choice(["{{$node['fetch_list'].json.items}}", "{{$json.data.users}}"])
            loop_body_node = random.choice(core_actions)
            
            logic_node = {
                "node": "loopItems",
                "parameters": {
                    "items": items_expr,
                    "loopBody": [{"node": loop_body_node["node"], "parameters": loop_body_node["params"]}]
                }
            }
            workflow_obj = {
                "workflow": {
                    "trigger": trigger_node,
                    "logic": [logic_node],
                    "actions": actions
                }
            }
            prompt_parts.append(f"and for each item in {items_expr.replace('{{', '').replace('}}', '')}, perform an action.")
        else:
            workflow_obj = {
                "workflow": {
                    "trigger": trigger_node,
                    "actions": actions
                }
            }

        all_prompts.append((" ".join(prompt_parts).capitalize() + ".", workflow_obj))
    
    return all_prompts

if __name__ == "__main__":
    generated_data = generate_prompts()
    
    # Ensure exactly 1500 prompts if possible, or trim/pad
    if len(generated_data) > 1500:
        generated_data = random.sample(generated_data, 1500)
    elif len(generated_data) < 1500:
        print(f"Warning: Could only generate {len(generated_data)} unique prompts. Consider expanding prompt/detail lists.")
        # You could add more generic prompts here to reach 1500 if needed
        while len(generated_data) < 1500:
            # Add simple generic prompts if not enough complex ones generated
            simple_prompt = random.choice(["Send a test email.", "Make a simple HTTP GET request.", "Send a quick SMS.", "Fetch some database data."])
            simple_output = {"workflow": {"trigger": {"node": "manual", "parameters": {}}, "actions": [{"node": "emailSend", "parameters": {"toEmail": "test@example.com", "subject": "Generic Test", "text": "Generic test email."}}]}} # Placeholder
            generated_data.append((simple_prompt, simple_output))


    output_file = "test_prompts.jsonl"
    with open(output_file, 'w', encoding='utf-8') as f:
        for prompt, workflow_json in generated_data:
            f.write(json.dumps({"input": prompt, "output": workflow_json}) + '\n')

    print(f"Generated {len(generated_data)} test prompts and conceptual workflows to {output_file}")
