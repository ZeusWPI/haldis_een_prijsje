import os

from flask import Flask, render_template, jsonify
import subprocess

app = Flask(__name__)


# Define the restaurant scraper functions
def run_scraper(restaurant_name):
    try:
        # Get the absolute path to the `run.sh` script in the parent directory
        run_script_path = os.path.join(os.getcwd(), "run.sh")
        # return run_script_path

        # Ensure the `run.sh` script is executable
        if not os.access(run_script_path, os.X_OK):
            os.chmod(run_script_path, 0o755)

        # Run the `run.sh` script with the provided restaurant name
        result = subprocess.run(
            [run_script_path, "--restaurant-name", restaurant_name],
            capture_output=True,
            text=True,
        )
        return result.stdout  # Return the output of the command
    except Exception as e:
        return str(e)


# route to display the current working directory and files (ls) used for debuting !!! remove afterward can be a
# security issue
@app.route("/ls")
def ls():
    try:
        # Get the current working directory
        cwd = os.getcwd()

        # Run `ls` to get the list of files in the current directory
        result = subprocess.run(['ls', '-l'], capture_output=True, text=True)

        # Split the result into lines and format them neatly
        files = result.stdout.splitlines()

        # Format the ls output to display it nicely
        formatted_files = []
        for file in files:
            parts = file.split()
            filename = " ".join(parts[8:])
            formatted_files.append(f"File: {filename}")

        return jsonify({
            'cwd': cwd,
            'files': formatted_files
        })
    except Exception as e:
        # Return the error message and log it
        return jsonify({
            "error": "An error occurred while listing files.",
            "message": str(e)
        }), 500


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/scrape/<restaurant>")
def scrape(restaurant):
    output = run_scraper(restaurant)
    return jsonify({"status": "success", "restaurant": restaurant, "output": output})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
