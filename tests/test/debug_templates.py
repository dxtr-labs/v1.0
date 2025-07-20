#!/usr/bin/env python3
"""
Quick debug script to find the problematic template
"""

import random

# Copy the exact same data as in the main script
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

# Sample data
data_types = ["customer", "sales", "financial", "operational"]
datasets = ["sales data", "customer data", "financial data", "operational metrics"]
sources = ["CRM", "database", "spreadsheet", "API"]
data = ["customer", "sales", "product", "user"]
metrics = ["performance", "sales", "customer satisfaction", "efficiency"]
databases = ["CRM and ERP", "sales and marketing", "customer and product", "financial and operational"]
reports = ["monthly", "quarterly", "annual", "weekly"]

print("Testing each template...")

for i, template in enumerate(data_processing_automations):
    try:
        request = template.format(
            data_type=random.choice(data_types),
            dataset=random.choice(datasets),
            source=random.choice(sources),
            data=random.choice(data),
            metrics=random.choice(metrics),
            databases=random.choice(databases),
            reports=random.choice(reports)
        )
        print(f"✅ Template {i+1}: {template} -> {request}")
    except KeyError as e:
        print(f"❌ Template {i+1}: {template} -> KeyError: {e}")
        
print("\nChecking for any missing variables...")
all_vars = ['data_type', 'dataset', 'source', 'data', 'metrics', 'databases', 'reports']
for template in data_processing_automations:
    for var in all_vars:
        if f'{{{var}}}' in template:
            print(f"Template '{template}' uses variable: {var}")
