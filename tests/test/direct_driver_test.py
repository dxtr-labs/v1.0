"""
Direct Driver Test - Test drivers we created manually
"""

import asyncio
import logging
import sys
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_manual_drivers():
    """Test the manually created drivers directly"""
    try:
        # Add paths
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        sys.path.append(backend_path)
        sys.path.append(os.path.join(backend_path, 'mcp'))
        sys.path.append(os.path.join(backend_path, 'mcp', 'drivers', 'universal'))
        
        logger.info("Testing manually created drivers...")
        
        # Test HTTP Driver
        logger.info("Testing HTTP Driver...")
        try:
            from http_driver import HttpDriver
            http_driver = HttpDriver()
            
            result = await http_driver.execute(
                'n8n-nodes-base.httpRequest',
                {'url': 'https://api.github.com/repos/microsoft/vscode', 'method': 'GET'},
                {'input_data': [{}]}
            )
            
            if result.get('success'):
                logger.info("SUCCESS: HTTP Driver works!")
            else:
                logger.info(f"FAILED: HTTP Driver failed: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"HTTP Driver test failed: {e}")
        
        # Test Data Processor Driver
        logger.info("Testing Data Processor Driver...")
        try:
            from data_processor_driver import DataProcessorDriver
            data_driver = DataProcessorDriver()
            
            result = await data_driver.execute(
                'n8n-nodes-base.set',
                {'values': {'name': 'Test User', 'status': 'active'}},
                {'input_data': [{'id': 1}]}
            )
            
            if result.get('success'):
                logger.info("SUCCESS: Data Processor Driver works!")
                logger.info(f"Result data: {result.get('data')}")
            else:
                logger.info(f"FAILED: Data Processor Driver failed: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Data Processor Driver test failed: {e}")
        
        # Test Utility Driver
        logger.info("Testing Utility Driver...")
        try:
            from utility_driver import UtilityDriver
            utility_driver = UtilityDriver()
            
            result = await utility_driver.execute(
                'n8n-nodes-base.stickyNote',
                {'content': 'This is a test note!', 'color': 'yellow'},
                {'input_data': [{'test': 'data'}]}
            )
            
            if result.get('success'):
                logger.info("SUCCESS: Utility Driver works!")
                logger.info(f"Note content: {result.get('note_content')}")
            else:
                logger.info(f"FAILED: Utility Driver failed: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Utility Driver test failed: {e}")
        
        # Test LangChain Driver
        logger.info("Testing LangChain Driver...")
        try:
            from langchain_driver import LangchainDriver
            langchain_driver = LangchainDriver()
            
            result = await langchain_driver.execute(
                '@n8n/n8n-nodes-langchain.lmChatOpenAi',
                {'prompt': 'What is AI?', 'model': 'gpt-3.5-turbo'},
                {'input_data': [{}]}
            )
            
            if result.get('success'):
                logger.info("SUCCESS: LangChain Driver works!")
                logger.info(f"AI Response: {result.get('text', 'No text found')}")
            else:
                logger.info(f"FAILED: LangChain Driver failed: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"LangChain Driver test failed: {e}")
        
        logger.info("Manual driver testing completed!")
        
    except Exception as e:
        logger.error(f"Manual driver test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_manual_drivers())
