import asyncio
import tkinter as tk
from tkinter import ttk, messagebox
import json
from threading import Thread
from src.components.net.network import P2PChat, setup_p2p

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("P2P Chat")
        self.chat = None
        self.loop = None  # Will be set in the thread
        self.setup_ui()
        self.start_asyncio_loop()

    def setup_ui(self):
        self.host_btn = ttk.Button(self.root, text="Host", command=self.host_chat)
        self.host_btn.pack(pady=5)

        self.join_btn = ttk.Button(self.root, text="Join", command=self.show_join_dialog)
        self.join_btn.pack(pady=5)

        self.chat_display = tk.Text(self.root, height=10, width=50, state="disabled")
        self.chat_display.pack(pady=5)

        self.msg_entry = ttk.Entry(self.root, width=40)
        self.msg_entry.pack(side=tk.LEFT, padx=5)
        self.send_btn = ttk.Button(self.root, text="Send", command=self.send_message)
        self.send_btn.pack(side=tk.LEFT)

    def start_asyncio_loop(self):
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()

        self.async_thread = Thread(target=run_loop, daemon=True)
        self.async_thread.start()

    def run_coro(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop).result()

    def update_chat_display(self, message):
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.config(state="disabled")
        self.chat_display.see(tk.END)

    def host_chat(self):
        async def run_host():
            offer_json = await setup_p2p(True)
            self.update_chat_display("Your offer (share this with the peer):\n" + offer_json)
            self.chat = P2PChat()
            await self.chat.create_room()
            self.chat.channel.on("message", lambda msg: self.root.after(0, self.on_message_received, msg))
            messagebox.showinfo("Host", "Share the offer with your peer, then enter their answer.")
            self.show_answer_dialog()

        self.run_coro(run_host())

    def show_join_dialog(self):
        self.join_window = tk.Toplevel(self.root)
        self.join_window.title("Join Chat")
        ttk.Label(self.join_window, text="Enter Host's Offer (JSON):").pack(pady=5)
        self.offer_entry = ttk.Entry(self.join_window, width=50)
        self.offer_entry.pack(pady=5)
        ttk.Button(self.join_window, text="Connect", command=self.join_chat).pack(pady=5)

    def join_chat(self):
        offer_json = self.offer_entry.get()
        self.join_window.destroy()

        async def run_join():
            self.chat = await setup_p2p(False)
            answer_json = await self.chat.join_room(offer_json)
            self.chat.channel = self.chat.pc.createDataChannel("chat")
            self.chat.channel.on("message", lambda msg: self.root.after(0, self.on_message_received, msg))
            self.update_chat_display("Your answer (share this with the host):\n" + answer_json)
            messagebox.showinfo("Join", "Share the answer with the host.")

        self.run_coro(run_join())

    def show_answer_dialog(self):
        self.answer_window = tk.Toplevel(self.root)
        self.answer_window.title("Enter Answer")
        ttk.Label(self.answer_window, text="Enter Peer's Answer (JSON):").pack(pady=5)
        self.answer_entry = ttk.Entry(self.answer_window, width=50)
        self.answer_entry.pack(pady=5)
        ttk.Button(self.answer_window, text="Submit", command=self.submit_answer).pack(pady=5)

    def submit_answer(self):
        answer_json = self.answer_entry.get()
        self.answer_window.destroy()

        async def run_answer():
            await self.chat.set_answer(answer_json)
            self.update_chat_display("Connected! You can now chat.")

        self.run_coro(run_answer())

    def on_message_received(self, message):
        self.update_chat_display(f"Peer: {message}")

    def send_message(self):
        message = self.msg_entry.get()
        if message and self.chat:
            async def send():
                await self.chat.send_message(message)
            self.run_coro(send())
            self.update_chat_display(f"You: {message}")
            self.msg_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()