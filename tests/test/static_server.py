from aiohttp import web
import os

routes = web.RouteTableDef()

@routes.get('/')
async def index(request):
    return web.FileResponse('agent-interface.html')

@routes.get('/{name}')
async def static_file(request):
    name = request.match_info['name']
    return web.FileResponse(name)

app = web.Application()
app.add_routes(routes)

if __name__ == '__main__':
    web.run_app(app, port=8000)
