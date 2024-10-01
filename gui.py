import tkinter as tk
from tkinter import ttk, messagebox
import feedparser
import requests
from PIL import Image, ImageTk
from io import BytesIO
from tkhtmlview import HTMLLabel
import sqlite3
import os
from modules.feed_manager import FeedManager

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("RSS Feed Reader")
        self.master.geometry("800x600")
        self.pack(fill=tk.BOTH, expand=True)
        self.feed_manager = FeedManager()
        self.feeds = []
        self.create_widgets()
        self.load_feeds()

    def create_widgets(self):
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Left panel
        self.left_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.left_frame, weight=1)

        self.feed_label = ttk.Label(self.left_frame, text="RSS Feeds", font=("Arial", 16, "bold"))
        self.feed_label.pack(pady=(10, 5))

        self.entry_frame = ttk.Frame(self.left_frame)
        self.entry_frame.pack(fill=tk.X, padx=10, pady=5)

        self.feed_entry = ttk.Entry(self.entry_frame, width=30)
        self.feed_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.feed_entry.insert(0, "Enter RSS URL")
        self.feed_entry.bind("<FocusIn>", self.clear_placeholder)
        self.feed_entry.bind("<FocusOut>", self.restore_placeholder)

        self.add_button = ttk.Button(self.entry_frame, text="+", width=3, command=self.add_feed)
        self.add_button.pack(side=tk.LEFT)

        self.feed_canvas = tk.Canvas(self.left_frame)
        self.feed_canvas.pack(side="left", fill=tk.BOTH, expand=True, padx=(10, 0), pady=5)

        self.feed_frame = ttk.Frame(self.feed_canvas)
        self.feed_canvas.create_window((0, 0), window=self.feed_frame, anchor="nw")

        self.scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.feed_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.feed_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.feed_frame.bind("<Configure>", lambda e: self.feed_canvas.configure(scrollregion=self.feed_canvas.bbox("all")))

        # Right panel
        self.right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.right_frame, weight=2)

        self.content_title = ttk.Label(self.right_frame, text="", font=("Arial", 16, "bold"))
        self.content_title.pack(pady=(10, 5))

        # Remove the content_text widget
        self.content_text = tk.Text(self.right_frame, wrap=tk.WORD, font=("Arial", 12))
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def clear_placeholder(self, event):
        if self.feed_entry.get() == "Enter RSS URL":
            self.feed_entry.delete(0, tk.END)

    def restore_placeholder(self, event):
        if not self.feed_entry.get():
            self.feed_entry.insert(0, "Enter RSS URL")

    def add_feed(self):
        url = self.feed_entry.get().strip()
        if url and url != "Enter RSS URL" and url not in [feed[1] for feed in self.feeds]:
            try:
                feed = feedparser.parse(url)
                feed_title = feed.feed.title
                self.feed_manager.save_feed(feed_title, url)
                self.feeds.append((feed_title, url))
                self.create_feed_item(feed_title, url)
                self.feed_entry.delete(0, tk.END)
                self.feed_entry.insert(0, "Enter RSS URL")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add feed: {str(e)}")
        else:
            messagebox.showwarning("Warning", "Please enter a valid and unique RSS feed URL.")

    def create_feed_item(self, title, url):
        frame = ttk.Frame(self.feed_frame)
        frame.pack(fill=tk.X, padx=5, pady=2)

        label = ttk.Label(frame, text=f"-> {title}", font=("Arial", 12))
        label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        label.bind("<Button-1>", lambda e, u=url: self.read_feed(u))

        delete_button = ttk.Button(frame, text="🗑", width=3, command=lambda: self.delete_feed(frame, url))
        delete_button.pack(side=tk.RIGHT)

    def delete_feed(self, frame, url):
        frame.destroy()
        self.feed_manager.delete_feed(url)
        self.feeds = [(title, u) for title, u in self.feeds if u != url]

    def read_feed(self, url):
        try:
            feed = feedparser.parse(url)
            self.content_title.config(text=feed.feed.title)
            
            # Clear the existing content
            for widget in self.right_frame.winfo_children():
                if widget != self.content_title:
                    widget.destroy()
            
            # Create a canvas to hold the feed items
            canvas = tk.Canvas(self.right_frame)
            canvas.pack(side="left", fill=tk.BOTH, expand=True, padx=(10, 0), pady=5)
            
            # Create a frame inside the canvas to hold the feed items
            frame = ttk.Frame(canvas)
            
            # Create a scrollbar for the canvas
            scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=canvas.yview)
            scrollbar.pack(side="right", fill=tk.Y)
            
            # Configure the canvas
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.create_window((0, 0), window=frame, anchor="nw")
            
            for entry in feed.entries[:10]:  # Display the first 10 entries
                # Create a frame for each entry
                entry_frame = ttk.Frame(frame)
                entry_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)

                # Create HTML content
                html_content = f"""
                <h2>{entry.title}</h2>
                <p><i>{entry.published if 'published' in entry else ''}</i></p>
                {entry.description if 'description' in entry else entry.summary}
                <hr>
                """

                # Create HTMLLabel for the entry content
                html_label = HTMLLabel(entry_frame, html=html_content, wrap=tk.WORD)
                html_label.pack(fill=tk.BOTH, expand=True)

            # Update the canvas scroll region
            frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
            
            # Bind the canvas to respond to mouse wheel
            canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read feed: {str(e)}")

    def load_feeds(self):
        self.feeds = self.feed_manager.load_feeds()
        for feed_title, url in self.feeds:
            self.create_feed_item(feed_title, url)

    def on_closing(self):
        self.feed_manager.close()
        self.master.destroy()
