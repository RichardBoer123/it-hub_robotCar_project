import tkinter as tk
from tkinter import messagebox
import subprocess
import os

class ProjectLauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Launcher")
        self.root.geometry("300x200")  # Adjusted size to fit 2 buttons
        
        self.create_widgets()

    def create_widgets(self):
        """ Create the interface elements for the project launcher """
        
        # Button to open the Network Scan project
        self.open_network_scan_button = tk.Button(self.root, text="Open Network Scan", command=self.open_network_scan)
        self.open_network_scan_button.pack(pady=10)
        
        # Button to open the Scoreboard project
        self.open_scoreboard_button = tk.Button(self.root, text="Open Scoreboard", command=self.open_scoreboard)
        self.open_scoreboard_button.pack(pady=10)

    def open_network_scan(self):
        """ Open the Network Scan project (the index.py inside /network-scan) """
        network_scan_path = os.path.join(os.getcwd(), 'network-scan', 'index.py')

        if os.path.exists(network_scan_path):
            try:
                # Open the Network Scan project by running its index.py
                subprocess.run(['python', network_scan_path], check=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Error running the project: {e}")
        else:
            messagebox.showerror("Error", "Network Scan project not found!")

    def open_scoreboard(self):
        """ Open the Scoreboard project (the index.py inside /scoreboard) """
        scoreboard_path = os.path.join(os.getcwd(), 'scoreboard', 'index.py')

        if os.path.exists(scoreboard_path):
            try:
                # Open the Scoreboard project by running its index.py
                subprocess.run(['python', scoreboard_path], check=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Error running the project: {e}")
        else:
            messagebox.showerror("Error", "Scoreboard project not found!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectLauncherApp(root)
    root.mainloop()
