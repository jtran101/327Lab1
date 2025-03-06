import socket
import time
from typing import Tuple

def measure_rtt(ip: str, port: int) -> Tuple[str, float]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)  # Set timeout for response

    try:
        start_time = time.time()
        sock.sendto(b'ping', (ip, port))
        _, _ = sock.recvfrom(1024)  # Wait for response
        rtt = time.time() - start_time
        return ip, rtt
    except socket.timeout:
        return ip, float('inf')
    finally:
        sock.close()

# Define Cluster B nodes
CLUSTER_B_IPS = [f"192.168.100.{i}" for i in range(10, 18)]
PORT = 5001
MESSAGE = "Hello, nearest container!"

rtts = [measure_rtt(ip, PORT) for ip in CLUSTER_B_IPS]
NEAREST_NODE_IP = min(rtts, key=lambda x: x[1])[0]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.sendto(MESSAGE.encode(), (NEAREST_NODE_IP, PORT))
print(f"Sent anycast message to {NEAREST_NODE_IP}: {MESSAGE}")
sock.close()