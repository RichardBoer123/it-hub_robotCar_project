from flask import Flask, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

# File to store logs and device data
log_file = 'log.json'
data_file = '../data.json'

# Ensure log file exists
if not os.path.exists(log_file):
    with open(log_file, 'w') as file:
        json.dump([], file)

# Ensure data file exists
if not os.path.exists(data_file):
    with open(data_file, 'w') as file:
        json.dump([], file)

def log_to_file(message):
    """Log a message to the log file with a timestamp."""
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": message
    }

    # Load existing logs
    try:
        with open(log_file, 'r') as file:
            log_data = json.load(file)
    except FileNotFoundError:
        log_data = []

    # Append new log entry and save
    log_data.append(log_entry)
    with open(log_file, 'w') as file:
        json.dump(log_data, file, indent=4)

@app.route('/logRobot', methods=['POST'])
def log_robot():
    data = request.json
    mac = data.get('mac')
    if not mac:
        return jsonify({"error": "MAC address is required"}), 400

    log_entry = f"Robot {mac} is online"
    log_to_file(log_entry)

    return jsonify({"status": "success", "message": log_entry})

@app.route('/initRobot', methods=['POST'])
def init_robot():
    data = request.json
    mac_address = data.get('macAddress')
    ip = data.get('ip')
    device_name = data.get('deviceName')
    camera_feed = data.get('cameraFeed')

    if not mac_address or not ip or not device_name:
        return jsonify({"error": "macAddress, ip, and deviceName are required"}), 400

    # Load existing device data
    try:
        with open(data_file, 'r') as file:
            devices = json.load(file)
    except FileNotFoundError:
        devices = []

    # Check if device with the same mac or ip exists and update
    device_exists = False
    for device in devices:
        if device['mac'] == mac_address or device['ip'] == ip:
            # Update the existing device data
            device['name'] = device_name
            device['cameraFeed'] = camera_feed
            device_exists = True
            break

    if not device_exists:
        # Add new device if it doesn't exist
        new_device = {
            "ip": ip,
            "mac": mac_address,
            "name": device_name,
            "cameraFeed": camera_feed
        }
        devices.append(new_device)

    # Save updated devices data to the file
    with open(data_file, 'w') as file:
        json.dump(devices, file, indent=4)

    # Create response messages
    if device_exists:
        message = f"Device {device_name} with MAC {mac_address} updated at IP {ip}, camera feed: {camera_feed}"
    else:
        message = f"Device {device_name} initialized with MAC {mac_address} at IP {ip}, camera feed: {camera_feed}"

    # Log the response message
    log_to_file(message)

    return jsonify({"status": "success", "message": message})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Change port if necessary
