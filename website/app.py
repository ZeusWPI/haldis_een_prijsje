import os
import sqlite3
import sys
import threading
from datetime import datetime

from flask import Flask, render_template, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler

# Add the parent directory to the system path to allow imports from the higher-level directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import run_scrapers
from run_sync import sync_gitmate

app = Flask(__name__)
lock = threading.Lock()

# SQLite database file
DATABASE = 'scraper_data.db'


# Class to hold the status of scrapers
class ScraperStatus:
    def __init__(self):
        self.status = {
            'metropol': False,
            'bicyclette': False,
            'simpizza': False,
            'pizza_donna': False,
            'bocca_ovp': False,
            's5': False
        }

    def is_running(self, scraper_name):
        with lock:
            return self.status.get(scraper_name, False)

    def set_running(self, scraper_name, running):
        with lock:
            if scraper_name in self.status:
                self.status[scraper_name] = running


# Instantiate the scraper status tracker
scraper_status = ScraperStatus()


# Function to update the database with scraper info
def update_scraper_info(restaurant_name, products_count):
    last_scraped = datetime.now()
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO scrapers (name, products_count, last_scraped)
            VALUES (?, ?, ?)
        """, (restaurant_name, products_count, last_scraped))
        conn.commit()


# Function to get all scraper info from the database
def get_scraper_info():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, products_count, last_scraped, status FROM scrapers")
        return cursor.fetchall()


def update_scraper_status(restaurant_name, status):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE scrapers
            SET status = ?
            WHERE name = ?
        """, (status, restaurant_name))
        conn.commit()


def run_scraper_in_background(restaurant_name):
    """
    Function to run the scraper in a background thread.
    Updates the status of the scraper in the ScraperStatus class.
    """
    if scraper_status.is_running(restaurant_name):
        print(f"Scraper for {restaurant_name} is already running. Skipping.")
        return

    try:
        # Mark the scraper as running
        scraper_status.set_running(restaurant_name, True)
        update_scraper_status(restaurant_name, "Running")
        print(f"Starting scraper for {restaurant_name}...")

        # Run the scraper for the given restaurant
        result = run_scrapers(restaurant_names=[restaurant_name])
        total_products_scraped = result["total_products_scraped"]

        update_scraper_info(restaurant_name, total_products_scraped)
        update_scraper_status(restaurant_name, "Finished")
        print(f"Scraper for {restaurant_name} completed. Products scraped: {total_products_scraped}")
    except Exception as e:
        print(f"Error running scraper for {restaurant_name}: {e}")
        update_scraper_status(restaurant_name, "Failed")
    finally:
        # Mark the scraper as not running
        scraper_status.set_running(restaurant_name, False)


@app.route("/scrape/<restaurant_name>", methods=['POST'])
def scrape(restaurant_name):
    """
    Start the scraper in a background thread for the given restaurant.
    """
    try:
        # Start a new thread to run the scraper for the given restaurant
        scraper_thread = threading.Thread(target=run_scraper_in_background, args=(restaurant_name,))
        scraper_thread.start()

        return jsonify({"message": f"Scraping started for {restaurant_name}"}), 200

    except Exception as e:
        # If there's an error, return the error message in JSON format
        return jsonify({"error": str(e)}), 500


@app.route("/scrape-all", methods=['POST'])
def scrape_all():
    """
    Trigger scraping for all restaurants.
    """
    try:
        # Get all the restaurant names from the database
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM scrapers")
            restaurant_names = [row[0] for row in cursor.fetchall()]

        # Run scrapers in background for all restaurants
        for restaurant_name in restaurant_names:
            # Start each scraper in a background thread
            scraper_thread = threading.Thread(target=run_scraper_in_background, args=(restaurant_name,))
            scraper_thread.start()

        return jsonify({"message": "Scraping started for all restaurants."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/update-scraper-info")
def update_scraper_info_page():
    """
    Fetch the scraper information from the database and update the frontend table.
    """
    scraper_info = get_scraper_info()
    return render_template("index.html", scraper_info=scraper_info)


# Database initialization
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
                    CREATE TABLE IF NOT EXISTS scrapers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        products_count INTEGER,
                        last_scraped TIMESTAMP,
                        status TEXT DEFAULT 'Never Run'
                    )
                """)
        conn.commit()

        # Check if the table is empty before populating it
        cursor.execute("SELECT COUNT(*) FROM scrapers")
        count = cursor.fetchone()[0]

        # Only populate the database if it's empty
        if count == 0:
            epoch_zero = 0
            restaurants = [
                ('metropol', -1, epoch_zero, "never run"),
                ('bicyclette', -1, epoch_zero, "never run"),
                ('simpizza', -1, epoch_zero, "never run"),
                ('pizza_donna', -1, epoch_zero, "never run"),
                ('bocca_ovp', -1, epoch_zero, "never run"),
                ('s5', -1, epoch_zero, "never run")
            ]
            cursor.executemany("""
                INSERT INTO scrapers (name, products_count, last_scraped, status)
                VALUES (?, ?, ?, ?)
            """, restaurants)
            conn.commit()


@app.route("/")
def home():
    scraper_info = get_scraper_info()
    return render_template('index.html', scraper_info=scraper_info)


@app.route("/sync-all", methods=["POST"])
def sync_all_files():
    """
    Sync all files to GitMate.
    """
    try:
        # Call the `sync_gitmate` function without arguments to sync all files
        print("Syncing all files to GitMate...")
        sync_gitmate()
        print("Synced all files to GitMate")
        return jsonify({"message": "All files synced successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


scheduler = BackgroundScheduler()
scheduler.add_job(scrape_all, 'interval', minutes=30)  # Scrape every 30 minutes
scheduler.add_job(sync_all_files, 'interval', minutes=30)  # Sync every 30 minutes
scheduler.start()


@app.route("/editor_selector")
def editor_selector():
    scraper_info = get_scraper_info()
    return render_template("editor_selector.html", scraper_info=scraper_info)


UPLOAD_FOLDER = 'hlds_files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Route to serve the editor page for a specific file
@app.route('/edit/<filename>', methods=['GET'])
def edit_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.hlds")
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            content = file.read()
        header = extract_header(content)
        return render_template('editor.html', filename=filename, header=header)  # Render the frontend editor
    else:
        return f"File {filename}.hlds not found", 404


@app.route('/read_file', methods=['GET'])
def read_file():
    filename = request.args.get('filename')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.hlds")

    if os.path.exists(filepath) and filepath.endswith('.hlds'):
        with open(filepath, 'r') as file:
            content = file.read()
        return jsonify({'content': content})
    else:
        return jsonify({'error': f'File {filepath} not found or invalid file type'}), 404


@app.route('/save_file', methods=['POST'])
def save_file():
    data = request.json
    filename = data.get('filename')
    content = data.get('content')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.hlds")

    if os.path.exists(filepath) and filepath.endswith('.hlds'):
        with open(filepath, 'w') as file:
            file.write(content)
        return jsonify({'message': 'File saved successfully'})
    else:
        return jsonify({'error': 'File not found or invalid file type'}), 404


def extract_header(content):
    # Define the header pattern (this can be customized based on your actual header structure)
    header_lines = content.splitlines()[:6]  # Assuming the header is the first 5 lines
    header = {}

    # Default to empty string if a part of the header is missing
    header['name_key'] = ""
    header['name_value'] = ""
    header['osm'] = ""
    header['phone'] = ""
    header['address'] = ""
    header['website'] = ""

    if len(header_lines) >= 5:
        print(len(header_lines))
        header['name_key'] = header_lines[1].split(":")[0].strip()
        header['name_value'] = header_lines[1].split(":")[1].strip()
        header['osm'] = header_lines[2].split("https://")[1].strip()
        header['phone'] = " ".join(header_lines[3].split(" ")[1:]).strip()
        header['address'] = " ".join(header_lines[4].split(" ")[1:]).strip()
        header['website'] = " ".join(header_lines[5].split(" ")[1:]).strip().split("https://")[1].strip()

    return header

if __name__ == "__main__":
    # Initialize the database when the app starts
    init_db()

    app.run(host="0.0.0.0", port=5000, threaded=True, debug=True)
