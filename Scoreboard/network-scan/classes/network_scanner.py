import socket
from scapy.all import ARP, Ether, srp

class NetworkScanner:
    def __init__(self):
        self.local_ip = self.get_local_ip()
        self.network = self.get_network()

    def get_local_ip(self):
        """
        Get the local IP address of the machine in a more reliable way by
        creating a dummy connection to determine the active interface IP.
        """
        try:
            # Create a socket connection to an external address
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                # The IP here is arbitrary; it just needs to be a routable address
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception as e:
            # If an error occurs, provide a fallback or raise an exception
            print(f"Error obtaining local IP: {e}")
            return "127.0.0.1"  # Fallback (localhost)

    def get_network(self):
        """
        Automatically calculate the network range based on the local IP.
        This will return the network in CIDR format (e.g., 192.168.1.0/24).
        """
        ip_parts = self.local_ip.split('.')
        return f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"

    def scan_network(self):
        """
        Scan the network for devices using ARP and return a list of devices found.
        """
        print(f"Scanning the network for devices in {self.network}...")

        arp_request = ARP(pdst=self.network)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp_request

        # Send the packet and receive responses
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
        """
        Attempt to get the device name via reverse DNS lookup.
        If the name can't be resolved, return 'Unknown'.
        """
        try:
            # Perform reverse DNS lookup
            return socket.gethostbyaddr(ip)[0]
        except socket.herror:
            # Return 'Unknown' if the name cannot be resolved
            return "Unknown"
