import socket
from datetime import datetime
import threading
import time

INTER_PORT = 5003 #between clusters
INTRA_PORT = 5004 #between containers
MULTICAST_PORT = 8080

HOST = "0.0.0.0"
CLUSTER_B_MASTER = "clusterB_master"

WORKER_IPS = [
    "192.168.100.3", "192.168.100.4", 
    "192.168.100.5", "192.168.100.6", "192.168.100.7", 
    "192.168.100.8", "192.168.100.9"
]

OTHER_MASTER_IP = "192.168.100.10"

MULTICAST_IPS = ['192.168.100.3', '192.168.100.4', '192.168.100.5']


#Communicate between clusters
def inter_listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, INTER_PORT))
    sock.listen(5)

    while True:
        other_socket, addr = sock.accept()
        other_ip = addr[0]

        if other_ip != OTHER_MASTER_IP:
            print("unauthorized access from: ", other_ip)
            other_socket.close()
            continue

        data = other_socket.recv(1024).decode()
        print(f"Received on port {INTER_PORT} from {other_ip}: {data}")

        other_socket.close()

#listen between worker containers and the master container
def intra_listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, INTRA_PORT))
    sock.listen(5)


    while True:
        other_socket, addr = sock.accept()
        other_ip = addr[0]

        if other_ip not in WORKER_IPS:
            other_socket.close()
            continue

        data = other_socket.recv(1024).decode()
        print(f"Received on port {INTER_PORT} from {other_ip}: {data}")

        other_socket.send(f"Message received on port {sock.getsockname()[1]}: \nThe message that got sent was {data}")
        other_socket.close()

def send_message(message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            print(f"Connecting to {OTHER_MASTER_IP}:{INTER_PORT}")
            sock.connect((CLUSTER_B_MASTER, INTER_PORT))
        except Exception as e:
            print(f"Error sending message: {e}")
        finally:
            print('Sending message to Cluster B', flush=True)
            sock.sendall(message.encode())
            sock.close()
            break

def send_intra_broadcastmessage(message):
    print('Sending intra-cluster broadcast message')

    for container_ip in WORKER_IPS:
        while True:
            try:
                bsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                bsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                bsock.connect((container_ip, INTRA_PORT))
            except Exception as e:
                print(f"Error sending message: {e}")
            finally:
                bsock.sendall(message.encode())
                data = bsock.recv(1024).decode()
                print('Received Reply Message: ', data)
                bsock.close()
                break

def main():
    #separate the listening to different ports
    print('Starting Cluster A with 8 containers', flush=True)
    threading.Thread(target=inter_listen).start()
    # threading.Thread(target=intra_listen).start()

    send_intra_broadcastmessage('Hello, Cluster A Workers')

    time.sleep(10)

    send_message('Hello, Cluster B!')

    

main()