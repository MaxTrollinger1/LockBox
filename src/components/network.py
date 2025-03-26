from p2pd import P2PNode, P2P_DIRECT, list_interfaces, load_interfaces, dict_child, SIGNAL_PIPE_NO, NET_CONF
import __main__

global chat


class P2PChat:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.node = None
        self.pipe = None
        self.nickname = None  # Store our node's nickname

    async def create_room(self):
        try:
            __main__.app.debug_message(f"Attempting Connection...")

            # Load available network interfaces
            if_names = await list_interfaces()
            ifs = await load_interfaces(if_names)

            # Configuration for the P2P node
            node_conf = dict_child({
                "enable_upnp": True,  # Enable UPnP for better reachability (if possible)
                "sig_pipe_no": SIGNAL_PIPE_NO,  # Ensure signaling pipe is set up
            }, NET_CONF)

            # Create and start the P2P node
            self.node = await P2PNode(ifs=ifs, port=self.port, conf=node_conf)
            __main__.app.debug_message(f"Room created at {self.ip}:{self.port}")

            # Register a nickname for the node
            self.nickname = await self.node.nickname("room_owner")  # Automatically adds a TLD
            __main__.app.debug_message(f"Nickname registered: {self.nickname}")

            # Add callback for receiving messages
            self.node.add_msg_cb(self.on_message_received)

            return self.node
        except Exception as e:
            __main__.app.debug_message(f"Error creating room: {e}")
            return None

    async def join_room(self, room_nickname):
        try:
            # Create a new node for the joiner
            self.node = await P2PNode()

            # Use the room owner's nickname to join
            self.pipe = await self.node.connect(room_nickname, strategies=[P2P_DIRECT])
            __main__.app.debug_message(f"Joined room using nickname: {room_nickname}")

            return self.node
        except Exception as e:
            __main__.app.debug_message(f"Error joining room: {e}")
            return None

    async def send_msg(self, msg):
        try:
            if self.pipe is None:
                raise ValueError("No pipe available! Are you connected?")
            await self.pipe.send(msg.encode())  # Encode the message to bytes
            response = await self.pipe.recv()  # Wait to receive a response
            __main__.app.debug_message(f"Received response: {response.decode()}")  # Decode bytes to string
        except Exception as e:
            __main__.app.debug_message(f"Error sending message: {e}")

    async def on_message_received(self, msg, client_tup, pipe):
        try:
            if pipe not in self.node.pipes.values():
                # Store the pipe for communication if it's a new one
                self.pipe = pipe
                __main__.app.debug_message(f"New peer connected: {client_tup}")

            # Log any message received
            __main__.app.debug_message(f"Received message: {msg.decode()}")

        except Exception as e:
            __main__.app.debug_message(f"Error in message callback: {e}")


async def setup_p2p(ip, port, is_creator=False, room_nickname=None):
    global chat
    chat = P2PChat(ip, port)

    if is_creator:
        # If is_creator is True, create the room
        return await chat.create_room()
    else:
        # Otherwise, join the room using the provided nickname
        if room_nickname is None:
            raise ValueError("room_nickname must be provided when joining a room!")
        return await chat.join_room(room_nickname)


async def try_send_msg(msg):
    try:
        if chat is None:
            raise ValueError("No chat object found! Are you connected?")
        await chat.send_msg(msg)
    except Exception as e:
        __main__.app.debug_message(f"Error sending message: {e}")
