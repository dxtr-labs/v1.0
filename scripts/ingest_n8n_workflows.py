#!/usr/bin/env python3
"""
N8N Workflow Ingestion Script
Ingests n8n workflows into PostgreSQL database as agent templates
"""

import asyncio
import asyncpg
import os
import json
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv('.env.local')

# Database configuration
DB_CONFIG = {
    "host": os.getenv("PGHOST", "34.44.98.81"),
    "port": int(os.getenv("PGPORT", 5432)),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", "devhouse"),
    "database": os.getenv("PGDATABASE", "postgres")
}

# Path to the directory containing n8n workflow JSON files
# Using local workflow files from the project
N8N_WORKFLOWS_DIR = os.path.join(os.path.dirname(__file__), '..', 'src', 'app', 'dashboard', 'automation', 'workflows')

# --- Category Mapping ---
# This dictionary maps keywords found in workflow filenames to categories.
# You can expand this mapping based on the types of workflows you have.
CATEGORY_KEYWORDS = {
    "Telegram": "Communication",
    "Slack": "Communication",
    "Twilio": "Communication",
    "SMS": "Communication",
    "Email": "Communication",
    "WhatsApp": "Communication",
    "Facebook": "Social Media",
    "Twitter": "Social Media",
    "GoogleSheets": "Data Management",
    "Database": "Data Management",
    "Cockpit": "Data Management",
    "Bitwarden": "Security & Auth",
    "Auth": "Security & Auth",
    "Stripe": "Payments",
    "Chargebee": "Payments",
    "Mailchimp": "Marketing",
    "Hunter": "Marketing",
    "CRM": "CRM",
    "Copper": "CRM",
    "Todoist": "Task Management",
    "Project": "Project Management",
    "Gitlab": "Development & CI/CD",
    "Bitbucket": "Development & CI/CD",
    "API": "API Integration",
    "HTTP": "API Integration",
    "Webhook": "API Integration",
    "Cron": "Scheduling",
    "Weather": "Utilities",
    "Process": "Utilities",
    "File": "File Operations",
    "Binary": "File Operations",
    "Coda": "Productivity",
    "GoogleSlides": "Productivity",
    "Mattermost": "Collaboration",
    "Openweathermap": "External Services",
    # Add more mappings as you analyze your 1000+ workflows
}

def infer_category(filename: str, workflow_name: str) -> str:
    """Infers a category based on keywords in the filename or workflow name."""
    text_to_analyze = (filename + " " + workflow_name).lower()
    for keyword, category in CATEGORY_KEYWORDS.items():
        if keyword.lower() in text_to_analyze:
            return category
    return "General" # Default category if no keyword matches

async def ingest_n8n_workflows():
    conn = None
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        print("Connected to database successfully.")

        # Set RLS context for admin user to allow inserts into agent_templates
        await conn.execute("SET app.current_user_id = '00000000-0000-0000-0000-000000000000';") # Dummy admin user ID
        await conn.execute("SET ROLE app_admin;") # Assume 'app_admin' can insert templates

        if not os.path.exists(N8N_WORKFLOWS_DIR):
            print(f"Error: N8N workflows directory not found at {N8N_WORKFLOWS_DIR}")
            print("Please ensure the workflows directory exists in src/app/dashboard/automation/workflows/")
            return

        for filename in os.listdir(N8N_WORKFLOWS_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(N8N_WORKFLOWS_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        n8n_workflow_json = json.load(f)

                    # Extract template name from filename or workflow name if available
                    template_name = n8n_workflow_json.get('name', filename.replace('.json', '').replace('_', ' ').title())
                    template_description = n8n_workflow_json.get('description', f"Automated workflow imported from n8n: {template_name}")
                    
                    # Infer category based on filename and workflow name
                    category = infer_category(filename, template_name)

                    # Generate generic agent properties for the template
                    agent_name_template = f"{template_name} Agent"
                    agent_role_template = f"Automates tasks related to {template_name.lower()}"
                    agent_personality_template = json.dumps({"tone": "efficient", "style": "direct"})
                    agent_expectations_template = f"Execute the '{template_name}' workflow precisely as defined."

                    # The initial_workflow_definition stores the raw n8n workflow JSON
                    initial_workflow_definition_jsonb = json.dumps(n8n_workflow_json)

                    insert_query = """
                    INSERT INTO agent_templates (
                        template_name, template_description, category,
                        agent_name_template, agent_role_template,
                        agent_personality_template, agent_expectations_template,
                        initial_workflow_definition
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (template_name) DO UPDATE SET
                        template_description = EXCLUDED.template_description,
                        category = EXCLUDED.category,
                        agent_name_template = EXCLUDED.agent_name_template,
                        agent_role_template = EXCLUDED.agent_role_template,
                        agent_personality_template = EXCLUDED.agent_personality_template,
                        agent_expectations_template = EXCLUDED.agent_expectations_template,
                        initial_workflow_definition = EXCLUDED.initial_workflow_definition,
                        updated_at = CURRENT_TIMESTAMP;
                    """
                    await conn.execute(
                        insert_query,
                        template_name, template_description, category,
                        agent_name_template, agent_role_template,
                        agent_personality_template, agent_expectations_template,
                        initial_workflow_definition_jsonb
                    )
                    print(f"Ingested/Updated template: {template_name} (Category: {category})")

                except json.JSONDecodeError:
                    print(f"Skipping {filename}: Invalid JSON format.")
                except Exception as e:
                    print(f"Error ingesting {filename}: {e}")
        
        print("\nN8N workflow ingestion complete.")

    except Exception as e:
        print(f"Database connection or ingestion error: {e}")
    finally:
        if conn:
            await conn.execute("RESET ROLE;")
            await conn.execute("RESET app.current_user_id;")
            await conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    asyncio.run(ingest_n8n_workflows())
