# 💀 DDOS Telegram Bot

Telegram bot with 4 attack methods. Runs on GitHub Codespaces.

## 🔥 Commands

- `/udp <target> <port> <time>` - UDP Flood
- `/syn <target> <port> <time>` - SYN Flood
- `/http <target> <port> <time>` - HTTP Flood
- `/mixed <target> <port> <time>` - Mixed Attack
- `/stopall` - Stop attacks
- `/status` - Check status
- `/id` - Get your ID

## 👑 Admin

- `/add <userid>` - Add user
- `/remove <userid>` - Remove user
- `/allusers` - List users
- `/globalstop` - Stop ALL

## 🚀 Run on Codespaces

1. Open repo in Codespaces
2. `pip install -r requirements.txt`
3. `export BOT_TOKEN="your_token"`
4. `export ADMIN_IDS="your_id"`
5. `python bot.py`
