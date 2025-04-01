import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
import json

class P2PChat:
    def __init__(self):
        self.pc = RTCPeerConnection(RTCConfiguration([
            RTCIceServer(urls="stun:stun.l.google.com:19302")
        ]))
        self.channel = None

    async def create_room(self):
        self.channel = self.pc.createDataChannel("chat")
        self.channel.on("message", self.on_message_received)
        offer = await self.pc.createOffer()
        await self.pc.setLocalDescription(offer)
        return json.dumps({"sdp": self.pc.localDescription.sdp, "type": self.pc.localDescription.type})

    async def join_room(self, offer_json):
        offer = json.loads(offer_json)
        offer_desc = RTCSessionDescription(sdp=offer["sdp"], type=offer["type"])
        await self.pc.setRemoteDescription(offer_desc)
        answer = await self.pc.createAnswer()
        await self.pc.setLocalDescription(answer)
        return json.dumps({"sdp": self.pc.localDescription.sdp, "type": self.pc.localDescription.type})

    async def set_answer(self, answer_json):
        answer = json.loads(answer_json)
        answer_desc = RTCSessionDescription(sdp=answer["sdp"], type=answer["type"])
        await self.pc.setRemoteDescription(answer_desc)

    def on_message_received(self, message):
        print("Received message:", message)

    async def send_message(self, message):
        if self.channel and self.channel.readyState == "open":
            self.channel.send(message)
        else:
            print("[ERROR] Channel is not open.")

async def setup_p2p(is_creator):
    chat = P2PChat()
    if is_creator:
        return await chat.create_room()
    else:
        return chat
