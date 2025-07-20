#!/usr/bin/env python3
"""Test import of main module"""

try:
    import main
    print("✅ Main module imported successfully")
    print("✅ App created:", main.app)
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
