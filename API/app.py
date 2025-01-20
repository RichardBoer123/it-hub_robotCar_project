from flask import Flask, request, jsonify
import socket
import logging
import json

app = Flask(__name__)

data_file = '../data.json'

def save_data(data):
    # Required keys
    required_keys = ["ip", "mac", "deviceName"]
    
    # Check if all required keys exist in the data
    for key in required_keys:
        if key not in data:
            return {"error": f"{key} key does not exist"}, 300

    # Decide where to save the data
    if 'camera_feed' in data:
        key_to_use = 'ESP'
    else:
        key_to_use = 'Arduino'
    
    # Load existing data
    try:
        with open(data_file, "r") as f:
            file_data = json.load(f)
    except json.JSONDecodeError:  # Handle empty file or invalid JSON
        file_data = {"Arduino": [], "ESP": []}

    # Append new data to the appropriate key
    file_data[key_to_use].append(data)
    
    # Write updated data back to the file
    with open(data_file, "w") as f:
        json.dump(file_data, f, indent=4)

    return jsonify({"status": "success", "data": data}), 200


@app.route('/init/', methods=['POST'])
def init():
    data = request.json
    return save_data(data)

@app.route('/status/', methods=['get'])
def test():
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=82, debug=False)