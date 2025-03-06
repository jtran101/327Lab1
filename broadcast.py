import socket
import sys

MESSAGE = "Hello, Cluster B!"
PORT = 5000

# IP addresses for Cluster B nodes
CLUSTER_B_IPS = [f"192.168.100.{i}" for i in range(10, 18)]  # 10 to 17 for all Cluster B nodes

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Send to all Cluster B nodes
for ip in CLUSTER_B_IPS:
    sock.sendto(MESSAGE.encode(), (ip, PORT))
    print(f"Broadcasted message to {ip}: {MESSAGE}")

# Close the socket
sock.close()