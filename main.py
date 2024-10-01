import tkinter as tk
from tkinter import ttk
from gui import Application

def main():
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('default')  # You can try different themes like 'alt', 'default', 'classic'
    app = Application(master=root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()
