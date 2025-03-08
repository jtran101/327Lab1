import socket
from datetime import datetime
import threading
import time

INTER_PORT = 5003 #between clusters
INTRA_PORT = 5004 #between containers
HOST = "0.0.0.0"
CLUSTER_B_MASTER = "clusterB_master"

WORKER_IPS = [
    "192.168.100.11", "192.168.100.12", 
    "192.168.100.13", "192.168.100.14", "192.168.100.15", 
    "192.168.100.16", "192.168.100.17"
]

OTHER_MASTER_IP = "192.168.100.2"

#Communicate between clusters
def inter_listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((HOST, INTER_PORT))
        sock.listen(5)
    except Exception as e:
        print(f'Error binding and listening to {INTER_PORT}: {e}')

    while True:
        other_socket, addr = sock.accept()
        other_ip = addr[0]

        if other_ip != OTHER_MASTER_IP:
            print("unauthorized access from: ", other_ip)
            other_socket.close()
            continue

        data = other_socket.recv(1024).decode()
        if not data:
            print(f"Received empty message from {other_ip}")
        print(f"Received TCP message on port {INTER_PORT} from {CLUSTER_B_MASTER}: {data}")  
        print('') 
        other_socket.close()
        send_broadcastmessage(data)

#listen between worker containers and the master container
def intra_listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, INTRA_PORT))
    sock.listen(5)

    print(f"Cluster B Master listening to {HOST}:{INTER_PORT}")

    while True:
        other_socket, addr = sock.accept()
        other_ip = addr[0]

        if other_ip not in WORKER_IPS:
            other_socket.close()
            continue

        data = other_socket.recv(1024).decode()
        print(f"Received on port {INTER_PORT} from {other_ip}: {data}")
        print('')

        other_socket.send(f"Message received on port {sock.getsockname()[1]}: \nThe message that got sent was {data}")
        other_socket.close()

def send_broadcastmessage(message):
    # TCP communication
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
                bsock.close()
                break

def inter_multicast_message(message):
    # UDP communication

    print('')
    print('Sending Group JS a message')
    while True:
        try:
            sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock2.connect((OTHER_MASTER_IP,INTER_PORT))
            sock2.sendall(message.encode())
        except Exception as e:
            print(f"Error sending message to clusterA: {e}")
        finally:
            sock2.close()



def main():
    print('Starting Cluster B with 8 containers', flush=True)
    #separate the listening to different ports
    threading.Thread(target=inter_listen).start()
    # threading.Thread(target=intra_listen).start()

    time.sleep(60)

    inter_multicast_message('Hello Group JS: This is ClusterB Master')

    

    

main()