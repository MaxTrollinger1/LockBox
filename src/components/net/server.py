import asyncio
import json
from aiohttp import web

clients = {}


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    client_id = request.match_info.get('client_id', "unknown")
    clients[client_id] = ws

    async for message in ws:
        if message.type == web.WSMsgType.TEXT:
            data = json.loads(message.data)
            target_id = data["target"]
            if target_id in clients:
                await clients[target_id].send_json(data)

    del clients[client_id]
    return ws


app = web.Application()
app.router.add_get("/ws/{client_id}", websocket_handler)

web.run_app(app, port=8765)
