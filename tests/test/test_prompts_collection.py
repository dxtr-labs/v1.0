#!/usr/bin/env python3
"""
User Input Prompt Testing Suite
Collection of diverse prompts to test the system's user input processing capabilities
"""

# Email Automation Prompts to Test
EMAIL_PROMPTS = [
    # Simple email requests
    "Send a welcome email to john@example.com",
    "Email the invoice to billing@client.com",
    "Send reminder to team@company.com about the meeting",
    
    # Complex email scenarios
    "Send a follow-up email to sarah@startup.io about our demo yesterday and include the pricing proposal",
    "Create a newsletter about our Q4 product updates and send it to all subscribers@list.com",
    "Email the quarterly performance report to managers@company.com and executives@company.com",
    
    # Bulk email operations
    "Send thank you emails to all customers who purchased last month",
    "Email survey invitations to our beta users asking for feedback",
    "Send product launch announcement to our entire mailing list",
    
    # Scheduled/automated emails
    "Set up automated welcome emails for new user registrations",
    "Send weekly digest emails every Monday morning to subscribers",
    "Email monthly reports to the finance team on the 1st of each month"
]

# Content Creation Prompts to Test
CONTENT_PROMPTS = [
    # Blog and article creation
    "Generate a blog post about AI automation trends for 2025",
    "Write an article about the benefits of workflow automation for small businesses",
    "Create content for our company newsletter highlighting recent achievements",
    
    # Social media content
    "Create social media posts about our new product launch for LinkedIn and Twitter",
    "Generate Instagram captions for our automation platform demo videos",
    "Write Facebook posts promoting our upcoming webinar series",
    
    # Technical documentation
    "Write API documentation for our new webhook endpoints",
    "Create user guides for our automation platform features",
    "Generate troubleshooting documentation for common integration issues",
    
    # Marketing materials
    "Create compelling marketing copy for our email automation features",
    "Write product descriptions for our e-commerce automation tools",
    "Generate case studies showcasing successful customer implementations",
    
    # Internal content
    "Create training materials for new employee onboarding",
    "Write meeting summaries from our quarterly business review",
    "Generate FAQ content for our customer support knowledge base"
]

# Data Processing Prompts to Test
DATA_PROMPTS = [
    # Analysis and reporting
    "Analyze sales data from our CRM and generate a monthly performance report",
    "Process customer feedback surveys and create insights dashboard",
    "Extract user behavior data from analytics and identify usage patterns",
    
    # Data transformation
    "Convert CSV files from our legacy system to JSON format for API integration",
    "Parse application logs and identify error patterns from the last 30 days",
    "Transform customer data from multiple sources into a unified format",
    
    # Database operations
    "Extract user activity logs from the database and generate usage statistics",
    "Clean and validate customer contact information in our CRM database",
    "Aggregate website analytics data and create performance metrics dashboard",
    
    # Integration tasks
    "Sync customer data between Salesforce and HubSpot every hour",
    "Import product inventory data from our warehouse management system",
    "Export financial data to our accounting software in the required format",
    
    # Real-time processing
    "Monitor API response times and alert if they exceed 2 seconds",
    "Process incoming webhook data and update customer records in real-time",
    "Analyze streaming data from IoT sensors and detect anomalies"
]

# Complex Automation Prompts to Test
COMPLEX_AUTOMATION_PROMPTS = [
    # Multi-step workflows
    "When a new customer registers, send them a welcome email, create a CRM record, and notify the sales team",
    "When a support ticket is created, categorize it, route to the appropriate team, and send confirmation to customer",
    "When inventory falls below 10 units, automatically reorder from suppliers and update the procurement team",
    
    # Scheduled automations
    "Every Monday morning, generate a weekly summary from our analytics and email it to all managers",
    "Daily at 6 PM, backup our database and send status report to the IT team",
    "On the 1st of each month, generate invoices for recurring customers and send payment reminders",
    
    # Event-triggered workflows
    "When someone fills out our contact form, qualify the lead and assign to appropriate sales representative",
    "When a customer cancels their subscription, send exit survey and update billing system",
    "When a new blog post is published, share it on all social media platforms and notify subscribers",
    
    # Integration automations
    "Sync data between our CRM, marketing platform, and support system every 2 hours",
    "When a deal closes in Salesforce, update the customer success platform and trigger onboarding workflow",
    "Monitor social media mentions and automatically respond to customer service inquiries",
    
    # Monitoring and alerting
    "Monitor website uptime and send Slack alerts if response time exceeds 5 seconds",
    "Track competitor pricing changes and notify the pricing team when discrepancies are detected",
    "Monitor server health metrics and automatically scale resources when needed"
]

# Edge Case and Complex Prompts to Test
EDGE_CASE_PROMPTS = [
    # Ambiguous requests
    "Help me with email stuff for our customers",
    "Create something for social media about our product",
    "Process the data and make it useful",
    
    # Multi-category requests
    "Generate a report about our email campaign performance and send it to marketing@company.com",
    "Create a blog post about our data processing capabilities and schedule it for publication",
    "Analyze customer support tickets and create automated email responses",
    
    # Very specific requests
    "Send a personalized email to john@client.com with our Q4 pricing proposal, including the 15% discount we discussed, and CC sarah@ourcompany.com",
    "Generate a 500-word blog post about 'The Future of Automation in Healthcare' optimized for SEO with keywords 'healthcare automation' and 'medical workflows'",
    "Extract all customer complaints from support tickets created between January 1-15, 2025, categorize by issue type, and create a summary report for the product team",
    
    # Conditional logic
    "If the customer hasn't opened our emails in 30 days, move them to a re-engagement campaign",
    "When API calls exceed 1000 per minute, throttle requests and notify the development team",
    "If a blog post gets more than 100 shares in 24 hours, promote it with paid social media ads"
]

# International and Special Character Prompts
INTERNATIONAL_PROMPTS = [
    "Enviar un email de bienvenida a nuevo@cliente.es",
    "发送季度报告给团队@公司.com",
    "Отправить уведомление на support@сайт.рф",
    "Send email to müller@österreich.at with special pricing",
    "Create content with émojis 🚀 and spëciâl characters for joão@empresa.com.br"
]

# Test prompt categories
PROMPT_CATEGORIES = {
    "📧 Email Automation": EMAIL_PROMPTS,
    "✍️ Content Creation": CONTENT_PROMPTS,
    "📊 Data Processing": DATA_PROMPTS,
    "🔄 Complex Automation": COMPLEX_AUTOMATION_PROMPTS,
    "🎯 Edge Cases": EDGE_CASE_PROMPTS,
    "🌍 International": INTERNATIONAL_PROMPTS
}

def print_test_prompts():
    """Print all test prompts organized by category"""
    print("🎯 USER INPUT PROMPTS FOR TESTING")
    print("=" * 70)
    print("Use these prompts to test the system's ability to understand and process user inputs")
    print("=" * 70)
    
    total_prompts = 0
    
    for category, prompts in PROMPT_CATEGORIES.items():
        print(f"\n{category} ({len(prompts)} prompts)")
        print("-" * 50)
        
        for i, prompt in enumerate(prompts, 1):
            print(f"{i:2d}. {prompt}")
        
        total_prompts += len(prompts)
    
    print("\n" + "=" * 70)
    print(f"📊 TOTAL PROMPTS: {total_prompts}")
    print("=" * 70)
    
    print("\n🔍 TESTING INSTRUCTIONS:")
    print("1. Copy any prompt from above")
    print("2. Test it with your workflow system")
    print("3. Check if the system correctly identifies:")
    print("   - Intent/category (email, content, data, automation)")
    print("   - Key parameters (emails, dates, requirements)")
    print("   - Appropriate workflow structure")
    print("4. Verify the generated workflow makes sense for the request")

def get_prompts_by_category(category_name: str):
    """Get prompts for a specific category"""
    for category, prompts in PROMPT_CATEGORIES.items():
        if category_name.lower() in category.lower():
            return prompts
    return []

def get_random_prompts(count: int = 10):
    """Get random prompts from all categories"""
    import random
    all_prompts = []
    for prompts in PROMPT_CATEGORIES.values():
        all_prompts.extend(prompts)
    
    return random.sample(all_prompts, min(count, len(all_prompts)))

def create_test_batch(category: str = "all", count: int = 5):
    """Create a test batch of prompts"""
    if category == "all":
        return get_random_prompts(count)
    else:
        prompts = get_prompts_by_category(category)
        return prompts[:count] if prompts else []

if __name__ == "__main__":
    print_test_prompts()
    
    print("\n🎲 RANDOM TEST BATCH (10 prompts):")
    print("-" * 40)
    random_prompts = get_random_prompts(10)
    for i, prompt in enumerate(random_prompts, 1):
        print(f"{i:2d}. {prompt}")
    
    print("\n💾 You can also use the functions:")
    print("- get_prompts_by_category('email') - Get email prompts")
    print("- get_random_prompts(5) - Get 5 random prompts")
    print("- create_test_batch('content', 3) - Get 3 content prompts")
