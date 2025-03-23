import asyncio
import tkinter as tk
import src.components.network as net
import requests

from src.components.ui_base import ChatFrontend
from datetime import datetime

global app
global serv
global root

serv = None
app = None
root = None

C_PORT = 12345


#region Networking

def get_public_ip():
    """Fetch the public IP address synchronously."""
    try:
        response = requests.get('https://api.ipify.org')
        return response.text
    except requests.RequestException as e:
        return f"Error: {e}"


async def setup_serv(ip, port, is_creator):
    """Set up server if not already running."""
    global serv
    serv = await net.setup_p2p(get_public_ip(), C_PORT, True)


async def update_async_tk(root, interval=0.05):
    """Run the tkinter mainloop with an asyncio event loop."""
    try:
        while True:
            root.update()  # Process tkinter updates
            await asyncio.sleep(interval)  # Yield control to the asyncio loop
    except asyncio.CancelledError:
        print("[DEBUG] update_async_tk was cancelled")
        raise  # Reraise it if cleanup or cancellation should propagate

#endregion

#region Cleanup
async def cleanup():
    """Perform cleanup before exiting the application."""
    global serv

    try:
        await asyncio.sleep(0.1)
        print("[DEBUG] Cleaning up resources...")
        if serv is not None:
            await serv.close()  # Clean up the server connection
            serv = None
        print("[DEBUG] Cleanup complete.")
    except Exception as e:
        print(f"[ERROR] Exception during cleanup: {e}")


def terminate():
    """Handle the application exit event."""
    print("[DEBUG] Quit requested, running cleanup...")
    asyncio.create_task(quit_app())

async def quit_app():
    """Quit the app gracefully (Async)."""
    await cleanup()  # Perform all cleanup tasks
    if root is not None:
        root.destroy()
    print("[DEBUG] Application closed.")
#endregion

#region Mutables

def is_hosting():
    return serv is not None

#endregion
async def main():
    """
    Main async function to run the application.
    """
    try:
        global app
        global root

        # Initialize tkinter root
        root = tk.Tk()
        app = ChatFrontend(root)
        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        app.debug_message(f"Application started at time = {current_time}")

        root.protocol("WM_DELETE_WINDOW", terminate)

        # Define callbacks
        async def send_message(message):
            await serv.try_send_msg(message)
            app.display_message(message, "You")

        async def join_chat(ip, port):
            app.debug_message(f"Attempting to join {ip}:{port}")
            await setup_serv(ip, port, False)
            app.debug_message(f"Joined host at {ip}:{port}")

        async def create_chat():
            app.debug_message(f"Starting host on {get_public_ip()} on port {C_PORT}")
            await setup_serv(get_public_ip(), C_PORT, True)
            app.debug_message("Chat host created")

        async def stop_host():
            app.debug_message("Stopping host...")
            await cleanup()

            app.debug_message("Chat host stopped")

        # Connect callbacks
        app.set_send_callback(send_message)
        app.set_join_callback(join_chat)
        app.set_create_callback(create_chat)
        app.set_stop_host_callback(stop_host)

        await update_async_tk(root)
    except asyncio.CancelledError:
        print("[DEBUG] asyncio CancelledError occurred")
        await cleanup()
    except KeyboardInterrupt:
        print("[DEBUG] KeyboardInterrupt detected")
        await cleanup()
    finally:
        print("[DEBUG] Event loop is shutting down.")



if __name__ == "__main__":
    asyncio.run(main())
