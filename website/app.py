import os
import sqlite3
import sys
import threading
from datetime import datetime

from flask import Flask, render_template, jsonify
import subprocess

# Add the parent directory to the system path to allow imports from the higher-level directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import run_scrapers
from run_sync import sync_gitmate

app = Flask(__name__)

# SQLite database file
DATABASE = 'scraper_data.db'


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
    Updates the database with the number of products, last scraped time, and status.
    """
    try:
        # Set status to "Running" when scraping starts
        update_scraper_status(restaurant_name, "Running")

        # Run the scraper for the given restaurant
        result = run_scrapers(restaurant_names=[restaurant_name])

        # Extract the values from the result dictionary
        restaurant_names = result["restaurant_names"]
        total_products_scraped = result["total_products_scraped"]

        # Update the database with the number of products, last scraped timestamp, and status as "Finished"
        update_scraper_info(restaurant_name, total_products_scraped)
        update_scraper_status(restaurant_name, "Finished")

    except Exception as e:
        print(f"Error running scraper for {restaurant_name}: {e}")
        # If there's an error, set the status to "Failed"
        update_scraper_status(restaurant_name, "Failed")


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


if __name__ == "__main__":
    # Initialize the database when the app starts
    init_db()

    app.run(host="0.0.0.0", port=5000, threaded=True, debug=True)
