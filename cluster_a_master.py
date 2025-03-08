import socket
from datetime import datetime
import threading
import time


# || PORTS TO COMMUNICATE
INTER_PORT = 5003 #between clusters
INTRA_PORT = 5004 #between containers

# || MULTICAST
MULTICAST_PORT = 8080
MULTICAST_GROUP_LABEL = "JS"
MULTICAST_IPS = ['192.168.100.3', '192.168.100.4', '192.168.100.5']

HOST = "0.0.0.0"


# || CLUSTER A WORKERS
WORKER_IPS = [
    "192.168.100.3", "192.168.100.4", 
    "192.168.100.5", "192.168.100.6", "192.168.100.7", 
    "192.168.100.8", "192.168.100.9"
]

# || OTHER CLUSTER MASTER
CLUSTER_B_MASTER = "clusterB_master"
OTHER_MASTER_IP = "192.168.100.10"



#Communicate between clusters
def inter_TCPlisten():
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
        print(f"Received TCP message on port {INTER_PORT} from {other_ip}: {data}")

        other_socket.close()

def inter_UDPlisten():
    try:
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock2.bind((HOST, INTER_PORT))

        while True:
            try: 
                data, addr = sock2.recvfrom(1024)

                print('')
                print(f'Received UDP message from {addr[0]}: {data.decode()}')

                print('Sending message to Group JS')
                send_intra_multicastmessage(data.decode())


            except socket.error as e:
                print(f"UDP socket error: {e}")
                continue
            finally:
                break
    finally:
        sock2.close()
        



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
    print('')
    print('Sending Inter Broadcast Message to ClusterB', flush=True)
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
    print('')
    print('Sending intra-cluster broadcast message:', flush=True)

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

def send_intra_multicastmessage(message):
    
    for container_ip in MULTICAST_IPS:
        while True:
            try:
                msock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                msock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                msock.connect((container_ip, INTRA_PORT))
            except Exception as e:
                print(f"Error sending multicast message: {e}")
            finally:

                msock.sendall(message.encode())
                data = msock.recv(1024).decode()
                print(f"Received multicast reply from {container_ip}: {data}")
                msock.close()
                break

def main():
    #separate the listening to different ports
    print('Starting Cluster A with 8 containers', flush=True)
    threading.Thread(target=inter_TCPlisten).start()
    threading.Thread(target=inter_UDPlisten).start()
    # threading.Thread(target=intra_listen).start()
    time.sleep(3)

    send_intra_broadcastmessage('Hello, Cluster A Workers')

    time.sleep(20)

    print('')
    print('Sending Intra Multicast Message', flush=True)
    send_intra_multicastmessage('Hello Multicast Group in Cluster A')

    time.sleep(20)

    send_message('Hello, Cluster B!')

    

main()