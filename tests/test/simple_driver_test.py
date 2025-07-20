"""
Simple Universal Driver Test
Quick verification that the system works
"""

import asyncio
import logging
import sys
import os

# Setup logging without special characters
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_basic_functionality():
    """Test basic universal driver functionality"""
    try:
        # Add backend to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        # Import the universal driver manager
        from backend.mcp.universal_driver_manager import universal_driver_manager, initialize_universal_drivers
        
        logger.info("Starting basic universal driver test...")
        
        # Initialize drivers
        logger.info("Initializing universal drivers...")
        await initialize_universal_drivers()
        
        # Get statistics
        stats = universal_driver_manager.get_driver_statistics()
        logger.info(f"Loaded {stats['total_drivers']} drivers")
        logger.info(f"Coverage: {stats['coverage']['coverage_percentage']:.1f}%")
        
        # Test a simple node execution
        logger.info("Testing sticky note execution...")
        result = await universal_driver_manager.execute_node(
            'n8n-nodes-base.stickyNote',
            {'content': 'Test note', 'color': 'yellow'},
            {'input_data': [{'test': 'data'}]}
        )
        
        if result.get('success'):
            logger.info("SUCCESS: Sticky note execution worked")
        else:
            logger.info(f"FAILED: Sticky note execution failed: {result.get('error')}")
        
        # Test HTTP request
        logger.info("Testing HTTP request execution...")
        result = await universal_driver_manager.execute_node(
            'n8n-nodes-base.httpRequest',
            {'url': 'https://api.github.com/repos/microsoft/vscode', 'method': 'GET'},
            {'input_data': [{}]}
        )
        
        if result.get('success'):
            logger.info("SUCCESS: HTTP request execution worked")
        else:
            logger.info(f"FAILED: HTTP request execution failed: {result.get('error')}")
        
        # Test data set operation
        logger.info("Testing set operation...")
        result = await universal_driver_manager.execute_node(
            'n8n-nodes-base.set',
            {'values': {'name': 'Test User', 'timestamp': '2024-01-01'}},
            {'input_data': [{'id': 1}]}
        )
        
        if result.get('success'):
            logger.info("SUCCESS: Set operation worked")
        else:
            logger.info(f"FAILED: Set operation failed: {result.get('error')}")
        
        logger.info("Basic universal driver test completed!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
