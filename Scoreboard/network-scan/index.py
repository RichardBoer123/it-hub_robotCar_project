# /test/index.py

import tkinter as tk
from tkinter import messagebox
import json
from classes.network_scanner import NetworkScanner  # Import the NetworkScanner class

class NetworkScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Scanner")
        self.root.geometry("800x600")
        self.root.configure(bg='lightblue')

        self.network_scanner = NetworkScanner()
        self.devices = []
        self.selected_devices = self.load_selected_devices()
        self.custom_names = {}  # To store custom names for devices

        self.create_widgets()

    def create_widgets(self):
        # Create a button to start scanning the network
        self.scan_button = tk.Button(self.root, text="Scan Network", command=self.scan_network)
        self.scan_button.pack(pady=10)

        # Create a scrollable frame for device checkboxes
        self.device_frame = tk.Frame(self.root)
        self.device_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.device_frame)
        self.scrollbar = tk.Scrollbar(self.device_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.device_list_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.device_list_frame, anchor="nw")
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Save button (hidden until devices are selected)
        self.save_button = tk.Button(self.root, text="Save Selected Devices", command=self.save_devices, state=tk.DISABLED)
        self.save_button.pack(pady=10)

        # Add Custom Name button (hidden until devices are saved)
        self.add_custom_name_button = tk.Button(self.root, text="Add Custom Name", command=self.add_custom_name, state=tk.DISABLED)
        self.add_custom_name_button.pack(pady=10)

        # Save all custom names button (hidden until custom names are added)
        self.save_custom_names_button = tk.Button(self.root, text="Save All Custom Names", command=self.save_custom_names, state=tk.DISABLED)
        self.save_custom_names_button.pack(pady=10)

        # Console log at the bottom
        self.console_log = tk.Text(self.root, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self.console_log.pack(fill=tk.X, padx=10, pady=5)

    def scan_network(self):
        """ Start scanning the network """
        self.log_message("Scanning network...")
        self.devices = self.network_scanner.scan_network()
        self.display_devices()

    def display_devices(self):
        """ Display devices in the GUI with checkboxes """
        # Clear previous device list
        for widget in self.device_list_frame.winfo_children():
            widget.destroy()

        if not self.devices:
            self.log_message("No devices found.")
            return

        self.log_message(f"Devices found: {len(self.devices)}")

        # Create checkboxes for each device
        self.device_checkbuttons = []
        for device in self.devices:
            var = tk.IntVar()
            # Check if the device info is in the selected devices
            if any(dev['mac'] == device['mac'] for dev in self.selected_devices):
                var.set(1)  # Pre-select the checkbox if the device is found in the selected list

            checkbutton = tk.Checkbutton(self.device_list_frame, text=f"{device['name']} - {device['ip']} ({device['mac']})", variable=var)
            checkbutton.device_info = device  # Store device data in the checkbutton
            self.device_checkbuttons.append((checkbutton, var))

            checkbutton.pack(anchor="w")

        # Enable the save button
        self.save_button.config(state=tk.NORMAL)

    def save_devices(self):
        """ Save selected devices to a list or file """
        selected_devices = []
        for checkbutton, var in self.device_checkbuttons:
            if var.get() == 1:  # If checkbox is selected
                selected_devices.append(checkbutton.device_info)

        if selected_devices:
            self.log_message(f"Selected {len(selected_devices)} devices to save.")
            # Here you can save the devices to a JSON file
            self.save_devices_to_file(selected_devices)
        else:
            self.log_message("No devices selected to save.")

    def save_devices_to_file(self, devices):
        """ Save the selected devices to a JSON file """
        with open("data.json", "w") as f:
            json.dump(devices, f, indent=4)

        self.log_message("Devices saved to data.json.")
        self.add_custom_name_button.config(state=tk.NORMAL)

    def load_selected_devices(self):
        """ Load selected devices from the JSON file """
        try:
            with open("data.json", "r") as f:
                devices = json.load(f)
                return devices
        except FileNotFoundError:
            return []  # Return an empty list if the file doesn't exist

    def add_custom_name(self):
        """ Add custom names for saved devices """
        self.custom_name_entries = []

        # Clear the device frame before displaying input fields
        for widget in self.device_list_frame.winfo_children():
            widget.destroy()

        # Display devices with input fields for custom names
        saved_devices = self.load_selected_devices()  # Only show devices already saved
        if not saved_devices:
            self.log_message("No devices saved. Please save devices before adding custom names.")
            return

        for device in saved_devices:
            frame = tk.Frame(self.device_list_frame)
            frame.pack(fill=tk.X, pady=5)

            name_label = tk.Label(frame, text=f"Device: {device['name']} - {device['ip']} ({device['mac']})")
            name_label.pack(side=tk.LEFT)

            custom_name_entry = tk.Entry(frame)
            custom_name_entry.insert(0, self.custom_names.get(device['mac'], ''))  # Pre-fill with custom name if available
            custom_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

            self.custom_name_entries.append((device['mac'], custom_name_entry))

        # Enable the "Save All Custom Names" button
        self.save_custom_names_button.config(state=tk.NORMAL)

    def save_custom_names(self):
        """ Save custom names for devices """
        for mac, entry in self.custom_name_entries:
            custom_name = entry.get()
            self.custom_names[mac] = custom_name

        # Now save the devices with custom names in data.json
        updated_devices = []
        saved_devices = self.load_selected_devices()

        for device in saved_devices:
            device_copy = device.copy()  # Copy the device data
            device_copy['custom_name'] = self.custom_names.get(device['mac'], 'Unknown')  # Add custom name
            updated_devices.append(device_copy)

        # Save the updated data with custom names
        self.save_devices_to_file(updated_devices)
        self.log_message("Custom names saved for all devices.")

    def log_message(self, message):
        """ Log messages to the console at the bottom """
        self.console_log.config(state=tk.NORMAL)
        self.console_log.insert(tk.END, f"[{self.get_current_time()}] {message}\n")
        self.console_log.config(state=tk.DISABLED)
        self.console_log.yview(tk.END)

    def get_current_time(self):
        """ Get current date and time as a string """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Set up Tkinter window and run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkScannerApp(root)
    root.mainloop()
