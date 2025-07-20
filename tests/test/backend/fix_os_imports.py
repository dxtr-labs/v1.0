#!/usr/bin/env python3
"""
Fix Missing OS Import in Legacy Drivers
"""

import os
from pathlib import Path

def fix_missing_os_imports():
    """Fix missing os imports in legacy drivers"""
    
    drivers_dir = Path("c:/Users/sugua/Desktop/redo/backend/mcp/drivers")
    
    # Files that need os import fix based on error output
    files_to_fix = [
        "web_hook_driver.py",
        "mcp_llm_driver.py", 
        "if_else_driver.py",
        "loop_items_driver.py",
        "cron_driver.py"
    ]
    
    print("🔧 Fixing missing os imports in legacy drivers...")
    
    for filename in files_to_fix:
        filepath = drivers_dir / filename
        if filepath.exists():
            print(f"   Processing: {filename}")
            
            try:
                # Read the file
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if os import is missing
                if "import os" not in content and "backend_dir = os.path.dirname" in content:
                    # Add os import after sys import
                    content = content.replace("import sys", "import sys\nimport os")
                    
                    # Write back
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"      ✅ Fixed: {filename}")
                else:
                    print(f"      ℹ️ No fix needed: {filename}")
                    
            except Exception as e:
                print(f"      ❌ Error fixing {filename}: {e}")
        else:
            print(f"   ⚠️ File not found: {filename}")
    
    print("✅ OS import fix complete!")

if __name__ == "__main__":
    fix_missing_os_imports()
