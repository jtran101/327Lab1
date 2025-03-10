from scapy import sniff, IP, TCP, UDP, Ether
import csv
import time 
import socket 
import threading

FILE = "/app/network_traffic.csv"
WRITE_LOCK = threading.Lock()

CLUSTERA_RANGE = range(2,10)
CLUSTERB_RANGE = range(10,18)

COLUMNS = ["Type", "Time (s)", "Source Cluster", "Destination Cluster", "Source IP",
           "Destination IP", "Protocol", "Length (bytpes)", "Flags (hex)"]

with WRITE_LOCK:
    try:
        with open(FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(COLUMNS)
    except FileExistsError:
        pass

def classify_packet(packet):
    if IP in packet:
        sourceIP = packet[IP].src
        destinationIP = packet[IP].dst
        length = len(packet)
        flags = "N/A"

        #Look at the last numbers to determine which cluster it belongs to
        src_octet = int(sourceIP.split(".")[-1])
        dst_octet = int(destinationIP.split(".")[-1])

        if TCP in packet:
            protocol = "TCP"
            flags = hex(packet[TCP].flags)
        else:
            protocol = "UDP"
        
        if src_octet in CLUSTERA_RANGE and dst_octet in CLUSTERA_RANGE:
            comm_type = "Intra-Broadcast"

sniff(prn=classify_packet, store=False)