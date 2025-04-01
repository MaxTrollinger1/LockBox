import asyncio
import json
from aiortc import RTCPeerConnection, RTCSessionDescription
import websockets

SIGNALING_SERVER = "ws://localhost:8765/ws"  # Replace with actual signaling server
client_id = input("Enter your client ID: ")
target_id = input("Enter target ID to connect to: ")

async def connect():
    conn = RTCPeerConnection()
    async with websockets.connect(f"{SIGNALING_SERVER}/{client_id}") as ws:
        print("Connected to signaling server.")

        # Offer/Answer exchange
        offer = await conn.createOffer()
        await conn.setLocalDescription(offer)
        await ws.send(json.dumps({"target": target_id, "sdp": offer.sdp, "type": offer.type}))

        while True:
            message = json.loads(await ws.recv())
            desc = RTCSessionDescription(message["sdp"], message["type"])
            await conn.setRemoteDescription(desc)

asyncio.run(connect())
