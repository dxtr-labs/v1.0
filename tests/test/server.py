from aiohttp import web
import asyncio
import json
from aiohttp.web import middleware
from aiohttp import WSMsgType
import logging
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Store active WebSocket connections
ws_connections = set()

# Server state
class ServerState:
    def __init__(self):
        self.agents = [
            {
                'agent_id': '1',
                'agent_name': 'Test Agent 1',
                'agent_role': 'Integration Testing'
            }
        ]
        self.next_agent_id = 2

# Initialize server state
server_state = ServerState()

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
        if not isinstance(response, web.FileResponse):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    except Exception as e:
        logger.error(f"Error handling request: {e}")
        return web.Response(status=500, text=str(e))

# WebSocket handling
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

# API Routes
async def get_agents(request):
    logger.debug("Handling GET /api/agents request")
    logger.debug(f"Current agents list: {server_state.agents}")
    return web.json_response(server_state.agents)

async def get_agent(request):
    logger.debug("Handling GET /api/agents/{agent_id} request")
    agent_id = request.match_info['agent_id']
    logger.debug(f"Looking for agent with ID: {agent_id} in agents list: {server_state.agents}")
    
    try:
        agent = next((a for a in server_state.agents if str(a['agent_id']) == str(agent_id)), None)
        if agent:
            logger.debug(f"Found agent: {agent}")
            return web.json_response(agent)
        else:
            logger.error(f"Agent with ID {agent_id} not found")
            return web.Response(status=404, text=f"Agent with ID {agent_id} not found")
    except Exception as e:
        logger.error(f"Error retrieving agent: {e}")
        return web.Response(status=500, text=str(e))

async def create_agent(request):
    logger.debug("Handling POST /api/agents request")
    try:
        data = await request.json()
        logger.debug(f"Received agent data: {data}")
        
        # Create new agent with unique ID
        agent_id = str(server_state.next_agent_id)
        server_state.next_agent_id += 1
        
        new_agent = {
            'agent_id': agent_id,
            'agent_name': data.get('agent_name'),
            'agent_role': data.get('agent_role')
        }
        logger.info(f"Creating new agent: {new_agent}")
        
        server_state.agents.append(new_agent)
        logger.info(f"Current agents list: {server_state.agents}")
        
        # Broadcast the update to all connected WebSocket clients
        update_message = {
            'type': 'agents_updated',
            'agents': server_state.agents,
            'created_agent': new_agent  # Include the newly created agent
        }
        logger.info(f"Broadcasting update message: {update_message}")
        
        for ws in ws_connections:
            try:
                logger.info(f"Sending update to WebSocket: {id(ws)}")
                await ws.send_json(update_message)
                logger.info("Update sent successfully")
            except Exception as e:
                logger.error(f'Error broadcasting agent update: {e}')
        
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

# Static file handling
async def handle_static(request):
    logger.debug(f"Handling static file request: {request.path}")
    try:
        filepath = request.path.lstrip('/')
        if filepath == '' or filepath == '/':
            filepath = 'agent-interface.html'
        
        if os.path.exists(filepath):
            return web.FileResponse(filepath)
        else:
            logger.error(f"File not found: {filepath}")
            return web.Response(status=404, text="File not found")
    except Exception as e:
        logger.error(f"Error serving static file: {e}")
        return web.Response(status=500, text=str(e))

# Create app with middleware
app = web.Application(middlewares=[cors_middleware])

# Add routes
app.router.add_get('/ws/agent', handle_websocket)
app.router.add_get('/api/agents', get_agents)
app.router.add_get('/api/agents/{agent_id}', get_agent)
app.router.add_post('/api/agents', create_agent)
app.router.add_post('/api/agents/{agent_id}/chat', chat_message)
app.router.add_get('/{path:.*}', handle_static)

if __name__ == '__main__':
    logger.info("Starting combined server on port 8080")
    web.run_app(app, port=8080)
