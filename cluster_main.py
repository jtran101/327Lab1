#!/usr/bin/env python3
import socket
import sys
import time
import csv
from datetime import datetime

# Configuration
CLUSTER_A_MASTER_IP = "192.168.100.2"
CLUSTER_B_MASTER_IP = "192.168.100.10"
INTRA_PORT = 5004
INTER_PORT = 5003


def log_communication(comm_type, source_cluster, dest_cluster, source_ip, dest_ip, protocol, length, flags):
    with open('network_log.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        timestamp = time.time()
        writer.writerow([
            comm_type,
            f"{timestamp:.7f}",
            source_cluster,
            dest_cluster,
            source_ip,
            dest_ip,
            protocol,
            length,
            flags
        ])

def broadcast_message(message):
    """Broadcast to all nodes in Cluster A"""
    for last_octet in range(3, 10):
        dest_ip = f"192.168.100.{last_octet}"
        send_tcp(dest_ip, INTRA_PORT, message)
        log_communication(
            "Intra-Broadcast",
            "Cluster A",
            "Cluster A",
            CLUSTER_A_MASTER_IP,
            dest_ip,
            "UDP",
            len(message),
            "0x010"
        )
    print("Broadcast completed")

def multicast_message(message, group):
    """Send to specific group of nodes"""
    for node_id in group:
        if 2 <= node_id <= 9:  # Cluster A range
            dest_ip = f"192.168.100.{node_id}"
            send_tcp(dest_ip, INTRA_PORT, message)
            log_communication(
                "Intra-Multicast",
                "Cluster A",
                "Cluster A",
                CLUSTER_A_MASTER_IP,
                dest_ip,
                "UDP",
                len(message),
                "0x012"
            )
    print("Multicast completed")

def forward_to_cluster_b(message, target_ip):
    """Forward message to Cluster B master"""
    send_tcp(CLUSTER_B_MASTER_IP, INTER_PORT, f"{target_ip}:{message}")
    log_communication(
        "Inter-Cluster",
        "Cluster A",
        "Cluster B",
        CLUSTER_A_MASTER_IP,
        CLUSTER_B_MASTER_IP,
        "UDP",
        len(message),
        "0x011"
    )
    print(f"Forwarded to Cluster B: {message}")

def send_tcp(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", INTER_PORT))


    sock.sendto(message.encode(), (ip, port))
    sock.close()


def start_listener():
    print(f"Cluster A Master listening on {CLUSTER_A_MASTER_IP}:{INTER_PORT}")
    sock = socket.socket(socket.AF_INET ,socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET ,socket.SO_REUSEADDR ,1)
    sock.setsockopt(socket.SOL_SOCKET ,socket.SO_REUSEPORT ,1)

    try:
        sock.bind((CLUSTER_A_MASTER_IP ,INTER_PORT))
        while True:
            try:
                data ,addr = sock.recvfrom(1024)
                message = data.decode()
                print(f"Received from {addr}: {message}")

                if addr[0].startswith("192.168.100."):
                    if int(addr[0].split('.')[-1]) <= 9:
                        forward_to_cluster_b(message ,addr[0])
            except KeyboardInterrupt:
                print("\nShutting down...")
                break
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()
def main():
    if len(sys.argv) < 2:
        start_listener()
        return

    command = sys.argv[1]
    if command == "broadcast" and len(sys.argv) >= 3:
        broadcast_message(sys.argv[2])
    elif command == "multicast" and len(sys.argv) >= 4:
        group = [int(x) for x in sys.argv[3].split(',')]
        multicast_message(sys.argv[2], group)
    else:
        print("Usage:")
        print("broadcast <message>")
        print("multicast <message> <node_ids>")

if __name__ == "__main__":
    # Create/initialize log file
    with open('network_log.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "Type", "Time (s)", "Source Cluster", "Destination Cluster",
            "Source IP", "Destination IP", "Protocol", "Length", "Flags"
        ])
    main()