#!/usr/bin/env python3
"""
Fix specific string literal issue in custom_mcp_llm_iteration.py
"""

def fix_string_literal_issue():
    """Fix the specific unterminated string literal issue"""
    
    file_path = "mcp/custom_mcp_llm_iteration.py"
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and fix the problematic section
    for i, line in enumerate(lines):
        if "I've compiled a comprehensive database of the **top 10 AI investors**" in line:
            print(f"Found problematic line at {i+1}: {line.strip()}")
            
            # Check if this line has proper quotes
            if line.count('"""') == 0 and not line.strip().endswith('"""'):
                # This line is part of a multi-line string that should be properly formatted
                # Let's rebuild this entire section properly
                
                # Find the start of the f-string
                start_idx = i
                while start_idx > 0 and 'f"""' not in lines[start_idx]:
                    start_idx -= 1
                
                # Find the end of the f-string
                end_idx = i
                while end_idx < len(lines) and '""",' not in lines[end_idx]:
                    end_idx += 1
                
                print(f"String section spans lines {start_idx+1} to {end_idx+1}")
                
                # Replace the entire section with a properly formatted version
                new_content = '''                "response": f"""**AI Investor Database Automation Created!**

I've compiled a comprehensive database of the **top 10 AI investors** actively funding automation and AI startups in 2025.

**What you'll receive:**
• Complete contact information for each investor
• Fund sizes totaling $42.7B in available capital  
• Investment focus areas and recent AI investments
• Key contact persons at each firm
• Investment stage preferences (Seed to Growth)

**Featured Investors Include:**
• Andreessen Horowitz (a16z) - $7.2B fund
• Google Ventures (GV) - $2.4B fund  
• Sequoia Capital - $8.5B fund
• Intel Capital - $2.0B fund
• And 6 more top-tier AI investors...

The complete database will be sent to **{recipient_email}** with actionable outreach strategies and recent investment examples.

Ready to send this investor database?""",
'''
                
                # Replace the problematic section
                lines[start_idx:end_idx+1] = [new_content]
                break
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Fixed string literal issue")

if __name__ == "__main__":
    fix_string_literal_issue()
