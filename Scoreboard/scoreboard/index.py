import http.server
import socketserver
import webbrowser
import threading
import json
import os

# Function to load the data from the JSON file
def load_data():
    data_file_path = os.path.join(os.path.dirname(__file__), '../data.json')  # Correct file path
    if not os.path.exists(data_file_path):
        raise FileNotFoundError(f"Could not find the data.json file at {data_file_path}")
    
    with open(data_file_path, 'r') as file:
        return json.load(file)

# Load the data from the JSON file
data = load_data()

# HTML content with embedded CSS and JavaScript to handle dynamic data
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Camera Streams</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            text-align: center;
            padding: 20px;
        }

        .container {
            background-color: #fff;
            margin: 20px;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }

        .name {
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
        }

        .timer {
            font-size: 18px;
            color: #555;
            margin-top: 10px;
        }

        iframe {
            width: 100%;
            height: 300px;
            border: none;
            margin-top: 15px;
        }

        .container button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 15px;
        }

        .container button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <h1>Camera Streams</h1>

    <div id="cameraContainers"></div>

    <script>
        const data = """ + json.dumps(data) + """; // Embedded JSON data from Python

        // Function to create a camera feed container
        function createCameraContainer(item) {
            const container = document.createElement('div');
            container.classList.add('container');
            
            const name = document.createElement('div');
            name.classList.add('name');
            name.textContent = 'Name: ' + item.custom_name;

            const timer = document.createElement('div');
            timer.classList.add('timer');
            timer.textContent = 'Timer: 00:00';  // Placeholder for now

            const iframe = document.createElement('iframe');
            iframe.src = item.cameraFeed;
            iframe.title = item.custom_name;

            // Append all the elements to the container
            container.appendChild(name);
            container.appendChild(timer);
            container.appendChild(iframe);

            // Append the container to the main div
            document.getElementById('cameraContainers').appendChild(container);
        }

        // Iterate over each item in the data array and create a container
        data.forEach(createCameraContainer);
    </script>

</body>
</html>
"""

# Define a custom request handler
class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        else:
            super().do_GET()

# Define the server settings
port = 8000
handler = MyRequestHandler

# Function to start the server
def start_server():
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at port {port}...")
        httpd.serve_forever()

# Start the server in a separate thread to avoid blocking the main thread
server_thread = threading.Thread(target=start_server)
server_thread.daemon = True  # Allow the server to exit when the program ends
server_thread.start()

# Open the default web browser automatically
webbrowser.open(f'http://localhost:{port}')

# Keep the main thread alive to keep the server running
input("Press Enter to stop the server...")
