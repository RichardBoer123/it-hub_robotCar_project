from flask import Flask, render_template
import json
import os
import webbrowser
from threading import Timer
import socket

# Create a Flask app
app = Flask(__name__)

# Function to check if data.json is empty
def is_data_json_empty():
    try:
        # Check if data.json exists and is not empty
        with open("data.json", "r") as file:
            # Read the file and check if it contains data
            data = file.read().strip()
            return not bool(data)  # Return True if empty, False otherwise
    except FileNotFoundError:
        print("Error: 'data.json' file not found!")
        return True

# Route for the homepage
@app.route("/")
def home():
    try:
        # Read the data from the JSON file
        with open("data.json", "r") as file:
            data = json.load(file)
            print("Loaded data:", data)
    except FileNotFoundError:
        print("Error: 'data.json' file not found!")
        data = {"error": "Data file not found."}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        data = {"error": "Invalid JSON format."}

    # Pass the data to the HTML template
    return render_template("index.html", data=data)

# Function to get the local IP address
def get_local_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

# Function to open the browser automatically
def open_browser():
    local_ip = get_local_ip()
    webbrowser.open_new(f"http://{local_ip}:81")

# Run the app
if __name__ == "__main__":
    # Check if data.json is empty before starting the server
    if is_data_json_empty():
        print("Error: 'data.json' is empty. Server will not start.")
    else:
        # Start the browser in a separate thread to avoid blocking the app
        Timer(1, open_browser).start()
        # Bind to 0.0.0.0 to make the server accessible via the local IP
        app.run(host="0.0.0.0", port=81, debug=True)
