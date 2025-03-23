import asyncio
import socket
import __main__ as main

global chat


class P2PChat:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.is_creator = False
        self.server = None  # For the creator to listen for peers
        self.reader = None  # For reading data from a socket
        self.writer = None  # For writing data to a socket
        self.clients = []  # List of connected clients (for creator)

    async def create_room(self):
        """Create a chat room and listen for connections as a server."""
        try:
            main.app.debug_message(f"Attempting to create room at {self.ip}:{self.port}...")
            self.is_creator = True

            # Create a server to listen for connections
            self.server = await asyncio.start_server(self.accept_connection, self.ip, self.port)
            main.app.debug_message(f"Room created and listening at {self.ip}:{self.port}")

            # Keep the server active
            await self.server.serve_forever()

        except Exception as e:
            main.app.debug_message(f"Error creating room: {e}")
            return None

    async def join_room(self):
        """Join a chat room as a client."""
        try:
            main.app.debug_message(f"Attempting to join room at {self.ip}:{self.port}...")

            # Connect to the room (server) as a client
            self.reader, self.writer = await asyncio.open_connection(self.ip, self.port)
            main.app.debug_message(f"Connected to room at {self.ip}:{self.port}")

            # Send a join message
            join_msg = f"Client has joined the room!"
            await self.send_msg(join_msg)
            main.app.debug_message(f"Sent join message: {join_msg}")

            # Start listening for messages from the server
            asyncio.create_task(self.receive_msgs())
            return True

        except Exception as e:
            main.app.debug_message(f"Error joining room: {e}")
            return None

    async def send_msg(self, msg):
        """Send a message to the connected socket."""
        try:
            if not self.writer:
                raise ValueError("No active connection to send messages.")

            # Send the message
            self.writer.write(msg.encode())
            await self.writer.drain()  # Ensure data is sent
            main.app.debug_message(f"Message sent: {msg}")
        except Exception as e:
            main.app.debug_message(f"Error sending message: {e}")

    async def receive_msgs(self):
        """Continuously listen for messages."""
        try:
            while True:
                # Read and decode messages
                data = await self.reader.read(1024)
                if not data:  # Connection closed
                    main.app.debug_message("Disconnected from room.")
                    break

                message = data.decode()
                main.app.debug_message(f"Received message: {message}")

        except Exception as e:
            main.app.debug_message(f"Error receiving message: {e}")

    async def accept_connection(self, reader, writer):
        """Handle a newly connected client (for the creator)."""
        try:
            addr = writer.get_extra_info('peername')
            main.app.debug_message(f"New connection from {addr}")

            self.clients.append(writer)

            # Listen for messages from this client
            while True:
                data = await reader.read(1024)
                if not data:  # Connection closed
                    main.app.debug_message(f"Client {addr} disconnected.")
                    self.clients.remove(writer)
                    break

                # Broadcast message to all other clients
                message = data.decode()
                await self.broadcast_message(message, writer)
        except Exception as e:
            main.app.debug_message(f"Error handling client: {e}")

    async def broadcast_message(self, msg, sender_writer=None):
        """Broadcast a message to all connected clients except the sender."""
        for writer in self.clients:
            if writer == sender_writer:
                continue  # Don't send the message back to the sender
            try:
                writer.write(msg.encode())
                await writer.drain()
                main.app.debug_message(f"Broadcasted message: {msg}")
            except Exception as e:
                main.app.debug_message(f"Error broadcasting message: {e}")


async def setup_p2p(ip, port, is_creator=False):
    """Initialize the P2P chat."""
    global chat
    chat = P2PChat(ip, port)

    if is_creator:
        # Run the server to create the room
        return await chat.create_room()
    else:
        # Join an existing room as a client
        return await chat.join_room()


async def try_send_msg(msg):
    """Send a message to the chat room."""
    try:
        if chat is None:
            raise ValueError("No chat object found! Are you connected?")
        await chat.send_msg(msg)
    except Exception as e:
        main.app.debug_message(f"Error sending message: {e}")
