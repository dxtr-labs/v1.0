from aiohttp import web
import asyncio
import json
from aiohttp.web import middleware
from aiohttp import WSMsgType
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Store active WebSocket connections
ws_connections = set()

@middleware
async def cors_middleware(request, handler):
    logger.debug(f"Handling {request.method} request to {request.path}")
    if request.method == "OPTIONS":
        return web.Response(
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
        )
    
    try:
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    except Exception as e:
        logger.error(f"Error handling request: {e}")
        return web.Response(status=500, text=str(e))

async def handle_websocket(request):
    logger.info("WebSocket connection request received")
    ws = web.WebSocketResponse()
    
    try:
        await ws.prepare(request)
        logger.info("WebSocket connection established")
        ws_connections.add(ws)
        
        # Send initial connection success message
        await ws.send_json({
            'type': 'connection',
            'status': 'connected'
        })
        logger.info("Sent connection success message")
        
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    logger.debug(f"Received WebSocket message: {data}")
                    response = {
                        'type': 'response',
                        'message': f'Received: {data}'
                    }
                    await ws.send_json(response)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in WebSocket message: {e}")
                    await ws.send_json({
                        'type': 'error',
                        'message': 'Invalid JSON'
                    })
            elif msg.type == WSMsgType.ERROR:
                logger.error(f'WebSocket error: {ws.exception()}')
    except Exception as e:
        logger.error(f"Error in WebSocket handler: {e}")
    finally:
        ws_connections.remove(ws)
        logger.info("WebSocket connection closed")
    
    return ws

async def get_agents(request):
    logger.debug("Handling GET /api/agents request")
    # Mock response with test agents
    agents = [
        {
            'agent_id': '1',
            'agent_name': 'Test Agent 1',
            'agent_role': 'Integration Testing'
        }
    ]
    logger.debug(f"Returning agents: {agents}")
    return web.json_response(agents)

async def create_agent(request):
    logger.debug("Handling POST /api/agents request")
    try:
        data = await request.json()
        logger.debug(f"Received agent data: {data}")
        
        # Mock response for agent creation
        new_agent = {
            'agent_id': '2',
            'agent_name': data.get('agent_name'),
            'agent_role': data.get('agent_role')
        }
        logger.debug(f"Created new agent: {new_agent}")
        return web.json_response(new_agent)
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        return web.Response(status=500, text=str(e))

async def chat_message(request):
    logger.debug(f"Handling POST /api/agents/{request.match_info['agent_id']}/chat request")
    try:
        data = await request.json()
        agent_id = request.match_info['agent_id']
        logger.debug(f"Received chat message for agent {agent_id}: {data}")
        
        # Mock chat response
        response = {
            'success': True,
            'response': f'Mock response to: {data.get("message")}',
            'agent_id': agent_id
        }
        
        # Broadcast workflow update
        workflow_update = {
            'type': 'workflow_update',
            'agent_id': agent_id,
            'nodes': [
                {
                    'id': 'node_1',
                    'type': 'chat_input',
                    'description': 'User input received'
                },
                {
                    'id': 'node_2',
                    'type': 'ai_processing',
                    'description': 'Processing message'
                }
            ]
        }
        
        for ws in ws_connections:
            try:
                await ws.send_json(workflow_update)
            except Exception as e:
                logger.error(f'Error sending workflow update: {e}')
        
        logger.debug(f"Returning chat response: {response}")
        return web.json_response(response)
    except Exception as e:
        logger.error(f"Error handling chat message: {e}")
        return web.Response(status=500, text=str(e))

app = web.Application(middlewares=[cors_middleware])

# Add routes
app.router.add_get('/ws/agent', handle_websocket)
app.router.add_get('/api/agents', get_agents)
app.router.add_post('/api/agents', create_agent)
app.router.add_post('/api/agents/{agent_id}/chat', chat_message)

if __name__ == '__main__':
    logger.info("Starting mock API server on port 8000")
    web.run_app(app, port=8000)
