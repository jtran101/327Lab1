#!/usr/bin/env python3
import socket
import sys
import os

#For worker nodes, can only communicate with master
INTRA_PORT = 5004
MULTICAST_PORT = 8080

CLUSTER_B_CONTAINERS = ['192.168.100.11', '192.168.100.12', '192.168.100.13',
                        '192.168.100.14', '192.168.100.15', '192.168.100.16',
                        '192.168.100.17' ]

CLUSTER_A_CONTAINERS = ['192.168.100.3', '192.168.100.4', '192.168.100.5',
                        '192.168.100.6', '192.168.100.7', '192.168.100.8',
                        '192.168.100.9']

CLUSTER_B_MASTER = '192.168.100.10'
CLUSTER_A_MASTER = '192.168.100.2'

def get_container_name(ip):
    try:
        container_full_name = socket.gethostbyaddr(ip)[0]
        container_name = container_full_name.split('.')[0]  # Extract only container name

        # ✅ Check if the result is a valid container name, not an ID
        if container_name.startswith("f") or container_name.isalnum():
            return socket.gethostname()  # Use hostname as a fallback

        return container_name
    except socket.herror:
        return socket.gethostname()

def start_listener():
    sock = socket.socket(socket.AF_INET ,socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET ,socket.SO_REUSEADDR ,1)
    sock.setsockopt(socket.SOL_SOCKET ,socket.SO_REUSEPORT ,1)


    try:
        sock.bind(("0.0.0.0" ,INTRA_PORT))
        sock.listen(5)

        hostname = socket.gethostname()
        container_ip = socket.gethostbyname(hostname)

        if container_ip in CLUSTER_A_CONTAINERS:
            print(f'Connected to master node at 192.168.100.2:{INTRA_PORT}')
        elif container_ip in CLUSTER_B_CONTAINERS:
            print(f'Connected to master node at 192.168.100.10:{INTRA_PORT}')

        while True:
            try:
                client_socket, addr = sock.accept()
                
                data = client_socket.recv(1024).decode()
                
                if addr[0] == CLUSTER_A_MASTER and container_ip in CLUSTER_A_CONTAINERS:
                    print(f'Received message from ClusterA_master: {data}', flush=True)
                    
                elif addr[0] == CLUSTER_B_MASTER and container_ip in CLUSTER_B_CONTAINERS:
                    print(f'Received message from ClusterB_master: {data}', flush=True)

                master_container = socket.gethostbyaddr(addr[0])[0]
                master_container = master_container.split('.')[0]

                container_name = get_container_name(container_ip)

                reply_message = f'Hello {master_container} from: {container_name}'

                client_socket.sendall(reply_message.encode())
                client_socket.close()
                
                
            except KeyboardInterrupt:
                print("\nShutting down...")
                break
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    start_listener()