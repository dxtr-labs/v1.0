#!/usr/bin/env python3
"""
Fix Legacy Driver Import Issues
Updates all legacy drivers to use correct import paths
"""

import os
import re
from pathlib import Path

def fix_legacy_driver_imports():
    """Fix import statements in all legacy drivers"""
    
    drivers_dir = Path("c:/Users/sugua/Desktop/redo/backend/mcp/drivers")
    print(f"🔧 Fixing legacy driver imports in: {drivers_dir}")
    
    # Pattern to match the old import
    old_import_pattern = r"from \.base_driver import BaseDriver"
    
    # New import lines to replace with
    new_import_lines = """import sys

# Add the backend directory to the path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(backend_dir)

from mcp.drivers.base_driver import BaseDriver"""
    
    # Counter for fixed files
    fixed_count = 0
    
    # Process all Python files in the drivers directory (not subdirectories)
    for driver_file in drivers_dir.glob("*.py"):
        if driver_file.name in ["__init__.py", "base_driver.py"]:
            continue
            
        print(f"   Processing: {driver_file.name}")
        
        try:
            # Read the file
            with open(driver_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if it needs fixing
            if "from .base_driver import BaseDriver" in content:
                # Add import statements if they don't exist
                if "import sys" not in content:
                    content = content.replace("import os", "import os\nimport sys")
                
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
    
    print(f"\n✅ Legacy driver import fix complete! Fixed {fixed_count} driver files")

def main():
    """Main function"""
    print("🔧 Legacy Driver Import Fixer")
    print("=" * 50)
    
    fix_legacy_driver_imports()
    
    print("\n" + "=" * 50)
    print("🏆 All legacy driver imports fixed!")

if __name__ == "__main__":
    main()
