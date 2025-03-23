# chat_frontend.py
import tkinter as tk
from tkinter import ttk, scrolledtext
import asyncio
from src.lockbox.components.config import Config as config
import __main__ as main


class ChatFrontend:
    def __init__(self, root):
        self.root = root

        config.apply_config(root)

        # Initialize asyncio event loop
        self.loop = asyncio.get_event_loop()

        # Initialize variables for callbacks (now coroutines)
        self.send_callback = None
        self.join_callback = None
        self.create_callback = None
        self.stop_host_callback = None

        self.running = True

        # Setup the GUI
        self._setup_menu()
        self._setup_chat_window()
        self._setup_input_field()

    def _setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        main_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Main", menu=main_menu)
        main_menu.add_command(label="Exit", command=self.root.quit)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)

        host_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Host", menu=host_menu)
        host_menu.add_command(label="Join Chat", command=self._open_join_window)
        host_menu.add_command(label="Create Chat", command=self._on_create_sync)
        host_menu.add_command(label="Stop Host", command=self._on_stop_sync)

        privacy_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Privacy", menu=privacy_menu)
        privacy_menu.add_command(label="Settings",
                                 command=lambda: self.debug_message("Privacy settings not implemented"))

    def _setup_chat_window(self):
        self.chat_window = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='disabled')
        self.chat_window.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    def _setup_input_field(self):
        input_frame = ttk.Frame(self.root)
        input_frame.pack(padx=10, pady=10, fill=tk.X)

        self.message_entry = ttk.Entry(input_frame)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.message_entry.bind("<Return>", lambda event: self._on_send_sync())

        send_btn = ttk.Button(input_frame, text="Send", command=self._on_send_sync)
        send_btn.pack(side=tk.RIGHT, padx=5)

    def _open_join_window(self):
        join_window = tk.Toplevel(self.root)
        join_window.title("Join Chat")
        join_window.geometry("300x150")
        join_window.transient(self.root)
        join_window.grab_set()

        ttk.Label(join_window, text="IP Address:").pack(pady=5)
        ip_entry = ttk.Entry(join_window)
        ip_entry.pack(pady=5, padx=10, fill=tk.X)

        ttk.Label(join_window, text="Port:").pack(pady=5)
        port_entry = ttk.Entry(join_window)
        port_entry.pack(pady=5, padx=10, fill=tk.X)

        connect_btn = ttk.Button(join_window, text="Connect",
                                 command=lambda: self._on_join_sync(ip_entry.get(), port_entry.get(), join_window))
        connect_btn.pack(pady=10)

    async def update_tk(self):
        """Update Tkinter within the asyncio loop"""
        while self.running:
            try:
                self.root.update()  # Process Tkinter events
                await asyncio.sleep(0.01)  # Yield to asyncio
            except tk.TclError:
                # Tkinter window was destroyed
                self.running = False
                break

    async def _on_send(self):
        """Async callback for sending messages"""
        message = self.message_entry.get().strip()
        if message and self.send_callback:
            await self.send_callback(message)
        self.message_entry.delete(0, tk.END)

    def _on_send_sync(self):
        """Synchronous wrapper for async send"""
        if main.is_hosting():
            asyncio.ensure_future(self._on_send(), loop=self.loop)

    async def _on_join(self, ip, port, window):
        """Async callback for joining chat"""
        if ip.strip() and port.strip() and self.join_callback:
            await self.join_callback(ip.strip(), port.strip())
            window.destroy()

    def _on_join_sync(self, ip, port, window):
        """Synchronous wrapper for async join"""
        asyncio.ensure_future(self._on_join(ip, port, window), loop=self.loop)

    def _on_stop_sync(self):
        """Synchronous wrapper for async stop"""
        if main.is_hosting():
            asyncio.ensure_future(self._on_stop_host(), loop=self.loop)

    async def _on_stop_host(self):
        if main.is_hosting() and self.stop_host_callback is not None:
            await self.stop_host_callback()

    async def _on_create(self):
        """Async callback for creating chat"""
        if self.create_callback:
            await self.create_callback()
        else:
            self.debug_message("Create Chat callback not set")

    def _on_create_sync(self):
        """Synchronous wrapper for async create"""
        asyncio.ensure_future(self._on_create(), loop=self.loop)

    def set_send_callback(self, callback):
        """Set the async callback function for sending messages"""
        self.send_callback = callback

    def set_stop_host_callback(self, callback):
        """Set the async callback function for stopping host"""
        self.stop_host_callback = callback

    def set_join_callback(self, callback):
        """Set the async callback function for joining chat"""
        self.join_callback = callback

    def set_create_callback(self, callback):
        """Set the async callback function for creating chat"""
        self.create_callback = callback

    def display_message(self, message, sender="User"):
        """Display a message in the chat window (synchronous)"""
        self.chat_window.configure(state='normal')
        self.chat_window.insert(tk.END, f"{sender}: {message}\n")
        self.chat_window.configure(state='disabled')
        self.chat_window.see(tk.END)

    def debug_message(self, message):
        """Display a debug message in the chat window (synchronous)"""
        self.chat_window.configure(state='normal')
        self.chat_window.insert(tk.END, f"[DEBUG]: {message}\n", "debug")
        self.chat_window.configure(state='disabled')
        self.chat_window.see(tk.END)
        self.chat_window.tag_configure("debug", foreground="gray")