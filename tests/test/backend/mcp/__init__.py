# backend/mcp/__init__.py
# MCP (Model Context Protocol) automation package

# Import the new isolated agent system
from .isolated_agent_engine import IsolatedAgentEngine
from .agent_engine_manager import AgentEngineManager, create_isolated_agent_engine, get_agent_engine_manager

# Keep backward compatibility with the old system
from .custom_mcp_llm_iteration import CustomMCPLLMIterationEngine

# Simple init file for testing

class McpError(Exception):
    """Base MCP error class"""
    
    def __init__(self, message: str, code: int = -1):
        super().__init__(message)
        self.code = code
        self.message = message

class ClientSession:
    """MCP client session"""
    
    def __init__(self):
        self.connected = False
        
    async def initialize(self):
        """Initialize the session"""
        self.connected = True
        
    async def close(self):
        """Close the session"""
        self.connected = False

# Export everything for FastMCP compatibility
__all__ = [
    "McpError", 
    "ClientSession"
]
