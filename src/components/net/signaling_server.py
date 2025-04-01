import asyncio
import websockets
import json

clients = {}

async def signaling_handler(websocket, path):
    peer_id = await websocket.recv()  # First message is peer's ID
    clients[peer_id] = websocket
    print(f"Client {peer_id} connected.")

    try:
        async for message in websocket:
            data = json.loads(message)
            target_id = data["target"]

            if target_id in clients:
                await clients[target_id].send(json.dumps(data))  # Forward messages
            else:
                print(f"Target {target_id} not found.")

    except websockets.exceptions.ConnectionClosed:
        del clients[peer_id]

server = websockets.serve(signaling_handler, "0.0.0.0", 8765)
asyncio.get_event_loop().run_until_complete(server)
asyncio.get_event_loop().run_forever()
