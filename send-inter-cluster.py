import socket

PORT = 5003  # Port used for inter-cluster communication
# CLUSTER_A_MASTER_IP = "192.168.100.2"
CLUSTER_A_MASTER_NAME = "clusterA_master"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

message = "Hello, Cluster B!"
# sock.connect((CLUSTER_A_MASTER_IP, PORT))
sock.connect((CLUSTER_A_MASTER_NAME, PORT))
sock.send(message.encode())
# sock.sendto(message.encode(), (CLUSTER_A_MASTER_IP, PORT))
print(f"Sent inter-cluster message: {message}")