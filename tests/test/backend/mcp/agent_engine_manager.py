#!/usr/bin/env python3
"""
Agent Engine Manager - Creates and manages isolated agent instances
Prevents task bleeding between different agents by maintaining separate instances
"""

import logging
import threading
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from .isolated_agent_engine import IsolatedAgentEngine

logger = logging.getLogger(__name__)

class AgentEngineManager:
    """
    Manages isolated agent engine instances
    Each agent gets its own completely separate engine instance
    """
    
    def __init__(self, db_manager=None, automation_engine=None, openai_api_key=None):
        """Initialize the agent engine manager"""
        self.db_manager = db_manager
        self.automation_engine = automation_engine
        self.openai_api_key = openai_api_key
        
        # Thread-safe storage for agent instances
        self._instances = {}
        self._lock = threading.Lock()
        
        # Cleanup settings
        self.max_idle_time = timedelta(hours=2)  # Remove idle instances after 2 hours
        self.last_cleanup = datetime.now()
        
        logger.info("Agent Engine Manager initialized")

    def get_or_create_agent_instance(self, agent_id: str, session_id: str, 
                                   agent_data: Dict[str, Any] = None,
                                   agent_expectations: str = None,
                                   agent_context: Dict[str, Any] = None) -> IsolatedAgentEngine:
        """
        Get existing agent instance or create a new isolated one
        Each agent+session combination gets its own unique instance
        """
        
        # Create unique key for this agent+session combination
        instance_key = f"{agent_id}_{session_id}"
        
        with self._lock:
            # Check if instance already exists
            if instance_key in self._instances:
                instance_info = self._instances[instance_key]
                instance_info['last_accessed'] = datetime.now()
                logger.info(f"🔄 Reusing existing agent instance: {instance_key}")
                return instance_info['engine']
            
            # Create new isolated instance
            logger.info(f"🆕 Creating new isolated agent instance: {instance_key}")
            
            engine = IsolatedAgentEngine(
                db_manager=self.db_manager,
                automation_engine=self.automation_engine,
                agent_data=agent_data,
                agent_expectations=agent_expectations,
                agent_id=agent_id,
                session_id=session_id,
                openai_api_key=self.openai_api_key,
                agent_context=agent_context
            )
            
            # Store instance with metadata
            self._instances[instance_key] = {
                'engine': engine,
                'created': datetime.now(),
                'last_accessed': datetime.now(),
                'agent_id': agent_id,
                'session_id': session_id,
                'agent_name': agent_data.get('agent_name', 'Unknown') if agent_data else 'Unknown'
            }
            
            logger.info(f"✅ Agent instance created: {instance_key} ({engine.instance_id})")
            return engine

    def remove_agent_instance(self, agent_id: str, session_id: str) -> bool:
        """Remove a specific agent instance"""
        instance_key = f"{agent_id}_{session_id}"
        
        with self._lock:
            if instance_key in self._instances:
                instance_info = self._instances.pop(instance_key)
                logger.info(f"🗑️ Removed agent instance: {instance_key}")
                return True
            return False

    def cleanup_idle_instances(self) -> int:
        """Remove idle agent instances to free up memory"""
        now = datetime.now()
        
        # Only run cleanup every 30 minutes
        if now - self.last_cleanup < timedelta(minutes=30):
            return 0
        
        removed_count = 0
        
        with self._lock:
            idle_keys = []
            
            for key, instance_info in self._instances.items():
                if now - instance_info['last_accessed'] > self.max_idle_time:
                    idle_keys.append(key)
            
            for key in idle_keys:
                instance_info = self._instances.pop(key)
                logger.info(f"🧹 Cleaned up idle agent instance: {key}")
                removed_count += 1
            
            self.last_cleanup = now
        
        if removed_count > 0:
            logger.info(f"🧹 Cleanup complete: Removed {removed_count} idle agent instances")
        
        return removed_count

    def get_all_instances_status(self) -> Dict[str, Any]:
        """Get status of all active agent instances"""
        with self._lock:
            status = {
                'total_instances': len(self._instances),
                'instances': {},
                'manager_stats': {
                    'last_cleanup': self.last_cleanup.isoformat(),
                    'max_idle_time_hours': self.max_idle_time.total_seconds() / 3600
                }
            }
            
            for key, instance_info in self._instances.items():
                engine = instance_info['engine']
                status['instances'][key] = {
                    'agent_id': instance_info['agent_id'],
                    'session_id': instance_info['session_id'],
                    'agent_name': instance_info['agent_name'],
                    'created': instance_info['created'].isoformat(),
                    'last_accessed': instance_info['last_accessed'].isoformat(),
                    'engine_instance_id': engine.instance_id,
                    'memory_status': engine.get_memory_status()
                }
            
            return status

    def force_cleanup_all(self) -> int:
        """Force cleanup of all agent instances"""
        with self._lock:
            count = len(self._instances)
            self._instances.clear()
            logger.info(f"🧹 Force cleanup: Removed all {count} agent instances")
            return count

# Global manager instance
_global_manager = None

def get_agent_engine_manager(db_manager=None, automation_engine=None, openai_api_key=None) -> AgentEngineManager:
    """Get or create the global agent engine manager"""
    global _global_manager
    
    if _global_manager is None:
        _global_manager = AgentEngineManager(
            db_manager=db_manager,
            automation_engine=automation_engine,
            openai_api_key=openai_api_key
        )
    
    return _global_manager

def create_isolated_agent_engine(agent_id: str, session_id: str, 
                               agent_data: Dict[str, Any] = None,
                               agent_expectations: str = None,
                               agent_context: Dict[str, Any] = None,
                               db_manager=None, automation_engine=None, 
                               openai_api_key=None) -> IsolatedAgentEngine:
    """
    Convenience function to create or get an isolated agent engine
    This is the main entry point for getting agent engines
    """
    
    manager = get_agent_engine_manager(
        db_manager=db_manager,
        automation_engine=automation_engine,
        openai_api_key=openai_api_key
    )
    
    # Cleanup idle instances periodically
    manager.cleanup_idle_instances()
    
    return manager.get_or_create_agent_instance(
        agent_id=agent_id,
        session_id=session_id,
        agent_data=agent_data,
        agent_expectations=agent_expectations,
        agent_context=agent_context
    )

# Export main functions
__all__ = ['AgentEngineManager', 'get_agent_engine_manager', 'create_isolated_agent_engine']
