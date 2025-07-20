from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
# MCP schema removed
# from mcp.schema import MCPRequest
from core.prompt_builder import build_prompt
from core.model_router import stream_model_response
import asyncio

router = APIRouter()

@router.post("/")
async def stream_chat(request: Request):
    data = await request.json()
    mcp_request = MCPRequest(**data)
    prompt = build_prompt(mcp_request)

    async def event_generator():
        async for chunk in stream_model_response(prompt, mcp_request.model):
            yield f"data: {chunk}\n\n"
            await asyncio.sleep(0.01)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
