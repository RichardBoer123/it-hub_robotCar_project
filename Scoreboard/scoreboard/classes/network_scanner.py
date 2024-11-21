from scapy.all import ARP, Ether, srp
import socket
import time


class NetworkScanner:
    def __init__(self):
        self.local_ip = self.get_local_ip()
        self.network = self.get_network()

    def get_local_ip(self):
        """Get the local IP address of the machine."""
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)

    def get_network(self):
        """Derive the network address (e.g., 192.168.1.0/24) from the local IP."""
        ip_parts = self.local_ip.split('.')
        return f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"

    def scan_network(self):
        """Scan the network for active devices using ARP requests."""
        print(f"Scanning the network for devices in {self.network}...")

        arp_request = ARP(pdst=self.network)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp_request

        result = srp(packet, timeout=2, verbose=False)[0]

        devices = []
        for sent, received in result:
            device_info = {
                "ip": received.psrc,
                "mac": received.hwsrc,
                "name": self.get_device_name(received.psrc)  # Get device name
            }
            devices.append(device_info)

        return devices

    def get_device_name(self, ip):
        """Get the device name using reverse DNS lookup."""
        try:
            return socket.gethostbyaddr(ip)[0]
        except socket.herror:
            return "Unknown"
    
    def is_device_active(self, ip):
        """Check if a device with the given IP address is still active."""
        try:
            arp_request = ARP(pdst=ip)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether / arp_request
            result = srp(packet, timeout=2, verbose=False)[0]
            
            # If result is empty, the device is not active
            return len(result) > 0
        except Exception as e:
            print(f"Error checking device {ip}: {str(e)}")
            return False
