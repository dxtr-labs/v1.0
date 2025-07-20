"""
Universal Driver for Langchain Chat Driver
Auto-generated driver for handling 1 node types
"""

import logging
import asyncio
from typing import Dict, Any, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from universal_driver_manager import BaseUniversalDriver

class LangchainChatDriverDriver(BaseUniversalDriver):
    """Universal driver for langchain_chat_driver service"""
    
    def __init__(self):
        super().__init__()
        self.service_name = "langchain_chat_driver"
        self.supported_node_types = ['@n8n/n8n-nodes-langchain.chatTrigger']
    
    def get_supported_node_types(self) -> List[str]:
        """Get list of supported node types"""
        return self.supported_node_types
    
    def get_required_parameters(self, node_type: str) -> List[str]:
        """Get required parameters for node type"""
        # Default required parameters - override in specific implementations
        common_params = {"url", "endpoint", "method", "data", "headers", "auth"}
        
        if node_type in self.supported_node_types:
            return list(common_params.intersection(self._get_common_params(node_type)))
        return []
    
    def _get_common_params(self, node_type: str) -> set:
        """Get common parameters for node type"""
        if "http" in node_type.lower() or "request" in node_type.lower():
            return {"url", "method", "headers"}
        elif "email" in node_type.lower() or "mail" in node_type.lower():
            return {"to", "subject", "body", "from"}
        elif "trigger" in node_type.lower():
            return {"event", "condition"}
        elif "webhook" in node_type.lower():
            return {"url", "method", "data"}
        else:
            return {"data", "config"}
    
    async def execute(self, node_type: str, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute node based on type"""
        if node_type not in self.supported_node_types:
            return {
                "success": False,
                "error": f"Unsupported node type: {node_type}",
                "supported_types": self.supported_node_types
            }
        
        # Validate parameters
        if not self.validate_parameters(node_type, parameters):
            return {
                "success": False,
                "error": f"Missing required parameters for {node_type}",
                "required": self.get_required_parameters(node_type)
            }
        
        # Route to specific method
        method_name = self._node_type_to_method_name(node_type)
        
        if hasattr(self, method_name):
            return await getattr(self, method_name)(parameters, context)
        else:
            return await self._execute_generic(node_type, parameters, context)
    
    def _node_type_to_method_name(self, node_type: str) -> str:
        """Convert node type to method name"""
        # Remove prefixes and convert to valid method name
        clean_name = node_type.replace('n8n-nodes-base.', '').replace('@n8n/n8n-nodes-langchain.', '').replace('-', '_').replace('.', '_')
        return f"execute_{clean_name}"
    
    async def _execute_generic(self, node_type: str, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generic execution for any node type"""
        self.logger.info(f"Executing generic {node_type} with parameters: {list(parameters.keys())}")
        
        try:
            # Generic successful execution
            result = {
                "success": True,
                "node_type": node_type,
                "service": self.service_name,
                "message": f"Executed {node_type} successfully (generic handler)",
                "data": parameters,
                "output": f"Generic output for {node_type}"
            }
            
            self.logger.info(f"✅ {node_type} completed (generic)")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ {node_type} failed: {e}")
            return {
                "success": False,
                "node_type": node_type,
                "error": str(e),
                "message": f"{node_type} execution failed (generic)"
            }

    async def execute_chatTrigger(self, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute @n8n/n8n-nodes-langchain.chatTrigger node"""
        self.logger.info(f"Executing @n8n/n8n-nodes-langchain.chatTrigger with parameters: {list(parameters.keys())}")
        
        try:
            # TODO: Implement actual @n8n/n8n-nodes-langchain.chatTrigger logic
            result = {
                "success": True,
                "node_type": "@n8n/n8n-nodes-langchain.chatTrigger",
                "message": f"Executed @n8n/n8n-nodes-langchain.chatTrigger successfully",
                "data": parameters,
                "output": f"Mock output for @n8n/n8n-nodes-langchain.chatTrigger"
            }
            
            self.logger.info(f"✅ @n8n/n8n-nodes-langchain.chatTrigger completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ @n8n/n8n-nodes-langchain.chatTrigger failed: {e}")
            return {
                "success": False,
                "node_type": "@n8n/n8n-nodes-langchain.chatTrigger",
                "error": str(e),
                "message": f"@n8n/n8n-nodes-langchain.chatTrigger execution failed"
            }
