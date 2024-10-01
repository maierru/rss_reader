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
        self.pack(fill="both", expand=True)
        self.feed_manager = FeedManager()
        self.feeds = []
        self.create_widgets()
        self.load_feeds()

    def create_widgets(self):
        # Main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)

        # Left panel
        self.left_frame = ctk.CTkFrame(self.main_frame, width=200)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.feed_label = ctk.CTkLabel(self.left_frame, text="RSS Feeds", font=("Arial", 16, "bold"))
        self.feed_label.pack(pady=(10, 5))

        self.entry_frame = ctk.CTkFrame(self.left_frame)
        self.entry_frame.pack(fill="x", padx=10, pady=5)

        self.feed_entry = ctk.CTkEntry(self.entry_frame, placeholder_text="Enter RSS URL")
        self.feed_entry.pack(side="left", padx=(0, 5), fill="x", expand=True)

        self.add_button = ctk.CTkButton(self.entry_frame, text="+", width=30, command=self.add_feed)
        self.add_button.pack(side="right")

        self.feed_scrollable_frame = ctk.CTkScrollableFrame(self.left_frame)
        self.feed_scrollable_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Right panel
        self.right_frame = ctk.CTkFrame(self.main_frame)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.content_title = ctk.CTkLabel(self.right_frame, text="", font=("Arial", 16, "bold"))
        self.content_title.pack(pady=(10, 5))

        self.content_scrollable_frame = ctk.CTkScrollableFrame(self.right_frame)
        self.content_scrollable_frame.pack(fill="both", expand=True, padx=10, pady=5)

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

        label = ctk.CTkLabel(frame, text=f"-> {title}", font=("Arial", 12))
        label.pack(side="left", fill="x", expand=True)
        label.bind("<Button-1>", lambda e, u=url: self.read_feed(u))

        delete_button = ctk.CTkButton(frame, text="🗑", width=30, command=lambda: self.delete_feed(frame, url))
        delete_button.pack(side="right")

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