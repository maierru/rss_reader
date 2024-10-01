# My Tkinter Application

Simple RSS Feed Reader

## Features

- Add and delete RSS feeds
- List all added RSS feeds
- Read and display content from selected RSS feeds

## Setup

1. Ensure you have Python 3.x installed on your system.
2. Clone this repository:
   ```
   git clone https://github.com/maierru/rss_reader
   cd rss_reader
   ```
3. Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

After setting up the environment, you can run the application:

On Unix-like systems (Linux, macOS):
```
./run_app.sh
```

On Windows:
```
run_app.bat
```

Alternatively, you can run the application directly with Python:
```
python main.py
```

## Project Structure

- `main.py`: The entry point of the application
- `gui.py`: Contains the main Application class and GUI logic
- `modules/`: A directory for additional modules (currently empty)

## Dependencies

- Python 3.x
- customtkinter
- feedparser

## License

no licence
