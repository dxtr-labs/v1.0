#!/usr/bin/env python3
"""Debug import issues in main.py"""

import sys
import os

# Add paths like main.py does
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

print("🔍 Testing individual imports...")

try:
    from fastapi import FastAPI
    print("✅ FastAPI imported")
except Exception as e:
    print(f"❌ FastAPI import failed: {e}")

try:
    from dotenv import load_dotenv
    print("✅ dotenv imported")
except Exception as e:
    print(f"❌ dotenv import failed: {e}")

try:
    from mcp.simple_mcp_llm import MCP_LLM_Orchestrator
    print("✅ MCP_LLM_Orchestrator imported")
except Exception as e:
    print(f"❌ MCP_LLM_Orchestrator import failed: {e}")

try:
    from mcp.automation_engine import AutomationEngine
    print("✅ AutomationEngine imported")
except Exception as e:
    print(f"❌ AutomationEngine import failed: {e}")

try:
    from core.simple_agent_manager import AgentManager
    print("✅ AgentManager imported")
except Exception as e:
    print(f"❌ AgentManager import failed: {e}")

try:
    from db.postgresql_manager import db_manager, init_db, close_db
    print("✅ postgresql_manager imported")
except Exception as e:
    print(f"❌ postgresql_manager import failed: {e}")

print("\n🔍 Now testing main module import...")
try:
    import main
    print("✅ Main module imported successfully")
except Exception as e:
    print(f"❌ Main module import failed: {e}")
    import traceback
    traceback.print_exc()
