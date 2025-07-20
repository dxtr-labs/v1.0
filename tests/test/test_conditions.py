#!/usr/bin/env python3
"""
Simple test to check the condition logic
"""

def test_conditions():
    """Test the exact conditions that should trigger workflow preview"""
    print('🧪 Testing Backend Condition Logic')
    print('=' * 40)
    
    # Test message after service selection
    message = "service:inhouse using ai generate a sales pitch to sell healthy ice cream products and send those in email to slakshanand1105@gmail.com"
    
    print(f'Message: {message}')
    print(f'Length: {len(message)}')
    
    # Test old logic conditions
    has_service = "service:" in message.lower()
    has_email_word = "email" in message.lower()
    has_at_symbol = "@" in message
    
    print(f'\nOld Logic Conditions:')
    print(f'  - Contains "service:": {has_service}')
    print(f'  - Contains "email": {has_email_word}')
    print(f'  - Contains "@": {has_at_symbol}')
    print(f'  - Combined condition: {has_service and (has_email_word or has_at_symbol)}')
    
    # Test what service is extracted
    ai_service = "inhouse"  # default
    if "service:openai" in message.lower():
        ai_service = "openai"
    elif "service:claude" in message.lower():
        ai_service = "claude"
    elif "service:inhouse" in message.lower():
        ai_service = "inhouse"
    
    print(f'\nExtracted AI service: {ai_service}')
    
    # Test email extraction
    import re
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, message)
    print(f'Extracted emails: {emails}')
    
    # Test what conflicts with sales pitch condition
    sales_words = ["sales", "sell", "product", "service", "business", "company"]
    found_sales_words = [word for word in sales_words if word in message.lower()]
    print(f'\nSales words found: {found_sales_words}')
    print(f'Would trigger sales pitch: {len(found_sales_words) > 0}')
    
    # Test new enhanced logic
    print(f'\nNew Enhanced Logic:')
    
    # AI keywords
    ai_keywords = ["using ai", "use ai", "with ai", "ai to", "ai for", "ai help"]
    has_ai_keyword = any(keyword in message.lower() for keyword in ai_keywords)
    print(f'  - Has AI keywords: {has_ai_keyword}')
    
    # Automation keywords
    automation_keywords = ["email", "send", "automation", "workflow", "@"]
    has_automation_keyword = any(keyword in message.lower() for keyword in automation_keywords)
    print(f'  - Has automation keywords: {has_automation_keyword}')
    
    # Content generation
    content_keywords = ["write", "create", "generate", "draft", "compose", "make"]
    has_content_generation = any(term in message.lower() for term in content_keywords)
    print(f'  - Has content generation: {has_content_generation}')
    
    # Determine intent
    if has_ai_keyword and automation_keywords and has_content_generation:
        intent = "ai_content_email"
    elif has_content_generation and has_automation_keyword:
        intent = "content_email"
    else:
        intent = "other"
    
    print(f'  - Detected intent: {intent}')
    
    print(f'\n🔍 DIAGNOSIS:')
    if has_service and (has_email_word or has_at_symbol):
        print('✅ Should trigger workflow preview with OLD logic')
    else:
        print('❌ Would NOT trigger workflow preview with OLD logic')
    
    if found_sales_words and not has_service:
        print('⚠️ Would trigger sales pitch instead (NEW logic)')
    elif has_service:
        print('✅ Service selection should override sales pitch (NEW logic)')

if __name__ == "__main__":
    test_conditions()
