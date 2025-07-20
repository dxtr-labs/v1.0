#!/usr/bin/env python3
"""
Fix Universal Driver Import Issues
Updates all drivers to use correct import paths
"""

import os
import re
from pathlib import Path

def fix_driver_imports():
    """Fix import statements in all universal drivers"""
    
    drivers_dir = Path("c:/Users/sugua/Desktop/redo/backend/mcp/drivers/universal")
    print(f"🔧 Fixing driver imports in: {drivers_dir}")
    
    # Pattern to match the old import
    old_import_pattern = r"from universal_driver_manager import BaseUniversalDriver"
    
    # New import lines to replace with
    new_import_lines = """# Add the parent directories to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(backend_dir)
mcp_dir = os.path.join(backend_dir, 'mcp')
sys.path.append(mcp_dir)

from mcp.universal_driver_manager import BaseUniversalDriver"""
    
    # Counter for fixed files
    fixed_count = 0
    
    # Process all Python files in the drivers directory
    for driver_file in drivers_dir.glob("*.py"):
        if driver_file.name == "__init__.py":
            continue
            
        print(f"   Processing: {driver_file.name}")
        
        try:
            # Read the file
            with open(driver_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if it needs fixing
            if "from universal_driver_manager import BaseUniversalDriver" in content:
                # Add import statements if they don't exist
                if "import sys" not in content:
                    content = content.replace("import logging", "import logging\nimport sys")
                if "import os" not in content:
                    content = content.replace("import sys", "import sys\nimport os")
                
                # Replace the old import
                content = re.sub(old_import_pattern, new_import_lines, content)
                
                # Write the fixed content back
                with open(driver_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"      ✅ Fixed: {driver_file.name}")
                fixed_count += 1
            else:
                print(f"      ℹ️ No fix needed: {driver_file.name}")
                
        except Exception as e:
            print(f"      ❌ Error fixing {driver_file.name}: {e}")
    
    print(f"\n✅ Import fix complete! Fixed {fixed_count} driver files")

def main():
    """Main function"""
    print("🔧 Universal Driver Import Fixer")
    print("=" * 50)
    
    fix_driver_imports()
    
    print("\n" + "=" * 50)
    print("🏆 All driver imports fixed!")

if __name__ == "__main__":
    main()
