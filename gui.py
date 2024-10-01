import customtkinter as ctk
from tkinter import messagebox
import feedparser
import requests
from PIL import Image, ImageTk
from io import BytesIO
from tkhtmlview import HTMLLabel
import sqlite3
import os
from modules.feed_manager import FeedManager

class Application(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("RSS Feed Reader")
        self.master.geometry("800x600")
        self.grid(row=0, column=0, sticky="nsew")
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.feed_manager = FeedManager()
        self.feeds = []
        self.create_widgets()
        self.load_feeds()

    def create_widgets(self):
        # Create all widgets
        self.create_frames()
        self.create_labels()
        self.create_entry()
        self.create_buttons()
        self.create_scrollable_frames()

        # Configure grid layout
        self.configure_grid()

    def create_frames(self):
        self.left_frame = ctk.CTkFrame(self, width=200)
        self.right_frame = ctk.CTkFrame(self)
        self.entry_frame = ctk.CTkFrame(self.left_frame)

    def create_labels(self):
        self.feed_label = ctk.CTkLabel(self.left_frame, text="RSS Feeds", font=("Arial", 16, "bold"))
        self.content_title = ctk.CTkLabel(self.right_frame, text="", font=("Arial", 16, "bold"))

    def create_entry(self):
        self.feed_entry = ctk.CTkEntry(self.entry_frame, placeholder_text="Enter RSS URL")

    def create_buttons(self):
        self.add_button = ctk.CTkButton(self.entry_frame, text="+", width=30, command=self.add_feed)

    def create_scrollable_frames(self):
        self.feed_scrollable_frame = ctk.CTkScrollableFrame(self.left_frame)
        self.content_scrollable_frame = ctk.CTkScrollableFrame(self.right_frame)

    def configure_grid(self):
        # Main grid configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left frame
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.left_frame.grid_rowconfigure(2, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        # Right frame
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Widgets in left frame
        self.feed_label.grid(row=0, column=0, pady=(10, 5))
        self.entry_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.feed_scrollable_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

        # Widgets in entry frame
        self.entry_frame.grid_columnconfigure(0, weight=1)
        self.feed_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.add_button.grid(row=0, column=1)

        # Widgets in right frame
        self.content_title.grid(row=0, column=0, pady=(10, 5))
        self.content_scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

    def add_feed(self):
        url = self.feed_entry.get().strip()
        if url and url not in [feed[1] for feed in self.feeds]:
            try:
                feed = feedparser.parse(url)
                feed_title = feed.feed.title
                self.feed_manager.save_feed(feed_title, url)
                self.feeds.append((feed_title, url))
                self.create_feed_item(feed_title, url)
                self.feed_entry.delete(0, "end")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add feed: {str(e)}")
        else:
            messagebox.showwarning("Warning", "Please enter a valid and unique RSS feed URL.")

    def create_feed_item(self, title, url):
        frame = ctk.CTkFrame(self.feed_scrollable_frame)
        frame.pack(fill="x", padx=5, pady=2)

        frame.grid_columnconfigure(0, weight=1)

        label = ctk.CTkLabel(frame, text=f"{title}", font=("Arial", 12), anchor="w")
        label.grid(row=0, column=0, sticky="ew", padx=(5, 0))
        label.bind("<Button-1>", lambda e, u=url: self.read_feed(u))

        delete_button = ctk.CTkButton(frame, text="🗑", width=30, command=lambda: self.delete_feed(frame, url))
        delete_button.grid(row=0, column=1, padx=(5, 5))

    def delete_feed(self, frame, url):
        frame.destroy()
        self.feed_manager.delete_feed(url)
        self.feeds = [(title, u) for title, u in self.feeds if u != url]

    def read_feed(self, url):
        try:
            feed = feedparser.parse(url)
            self.content_title.configure(text=feed.feed.title)
            
            # Clear the existing content
            for widget in self.content_scrollable_frame.winfo_children():
                widget.destroy()
            
            for entry in feed.entries[:10]:  # Display the first 10 entries
                # Create a frame for each entry
                entry_frame = ctk.CTkFrame(self.content_scrollable_frame)
                entry_frame.pack(fill="x", expand=True, padx=5, pady=5)

                # Create HTML content
                html_content = f"""
                <h2>{entry.title}</h2>
                <p><i>{entry.published if 'published' in entry else ''}</i></p>
                {entry.description if 'description' in entry else entry.summary}
                <hr>
                """

                # Create HTMLLabel for the entry content
                html_label = HTMLLabel(entry_frame, html=html_content, wrap="word")
                html_label.pack(fill="both", expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read feed: {str(e)}")

    def load_feeds(self):
        self.feeds = self.feed_manager.load_feeds()
        for feed_title, url in self.feeds:
            self.create_feed_item(feed_title, url)

    def on_closing(self):
        self.feed_manager.close()
        self.master.destroy()