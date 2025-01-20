from flask import Flask, render_template, jsonify, request
import webbrowser as wb
import os
import json

app = Flask(__name__)

wb.open('http://127.0.0.1:8080/')

# Helper function to get the data.json file path
def get_data_file_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, '..', 'data.json')



@app.route('/update-custom-name', methods=['PUT'])
def update_custom_name():
    file_path = get_data_file_path()
    request_data = request.json

    ip_to_update = request_data.get('ip')  # IP of the device
    new_custom_name = request_data.get('custom_name')  # New custom name

    if not ip_to_update or not new_custom_name:
        return jsonify({"error": "Both 'ip' and 'custom_name' are required"}), 400

    try:
        # Read the current data
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)

        # Check if data is a list of devices
        if not isinstance(data, list):
            return jsonify({"error": "Data is not in the expected format"}), 500

        # Find the device with the matching IP
        device_found = False
        for device in data:
            if device.get('ip') == ip_to_update:
                device['custom_name'] = new_custom_name  # Update the custom name
                device_found = True
                break

        if not device_found:
            return jsonify({"error": f"Device with IP '{ip_to_update}' not found"}), 404

        # Write the updated data back to the file
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=2)

        return jsonify({"message": f"Custom name for device with IP '{ip_to_update}' updated successfully"}), 200

    except FileNotFoundError:
        return jsonify({"error": "data.json file not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding JSON"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/clear-data', methods=['POST'])
def clear_data():
    file_path = get_data_file_path()

    try:
        with open(file_path, 'w') as json_file:
            json.dump([], json_file)  # Write an empty list to the file
        return jsonify({"message": "Data cleared successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-data', methods=['GET'])
def get_data():
    file_path = get_data_file_path()

    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        return jsonify(data)  # Return the data as a JSON response
    except FileNotFoundError:
        return jsonify({"error": "data.json file not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding JSON"}), 500

@app.route('/delete-key', methods=['DELETE'])
def delete_key():
    file_path = get_data_file_path()
    key_to_delete = request.json.get('key')  # Expecting the key in the request body

    try:
        # Read the current data
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)

        # Check if data is a dictionary or a list of dictionaries
        if isinstance(data, dict):
            if key_to_delete in data:
                del data[key_to_delete]
            else:
                return jsonify({"error": f"Key '{key_to_delete}' not found"}), 404
        elif isinstance(data, list):
            data = [item for item in data if item.get('key') != key_to_delete]

        # Write the updated data back to the file
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=2)

        return jsonify({"message": f"Key '{key_to_delete}' deleted successfully"}), 200
    except FileNotFoundError:
        return jsonify({"error": "data.json file not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding JSON"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update-best-time', methods=['PUT'])
def update_best_time():
    file_path = get_data_file_path()
    try:
        # Parse request data
        request_data = request.json
        ip = request_data.get('ip')  # Robot IP
        best_time = request_data.get('best_time')  # New best time

        if not ip or not best_time:
            return jsonify({"error": "IP and best_time are required"}), 400

        # Read current data
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)

        # Find and update the relevant robot
        updated = False
        for device in data:
            if device.get('ip') == ip:
                device['best_time'] = best_time
                updated = True
                break

        if not updated:
            return jsonify({"error": f"No device found with IP {ip}"}), 404

        # Write updated data back to the file
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=2)

        return jsonify({"message": f"Best time for IP {ip} updated successfully"}), 200
    except FileNotFoundError:
        return jsonify({"error": "data.json file not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding JSON"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return render_template('pages/homepage.html')

@app.route("/scoreboard")
def run():
    return render_template('pages/scoreboard.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('pages/404.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
