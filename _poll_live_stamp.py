import json, time, urllib.request
LOCAL = "2026-08-10T11:43:29+0200"
URL = "https://sunradiance.github.io/lira-mark/thread_snapshot.json"
max_wait = 180
interval = 15
start = time.time()
attempt = 0
while True:
    attempt += 1
    bust = int(time.time() * 1000)
    url = f"{URL}?t={bust}"
    try:
        req = urllib.request.Request(url, headers={"Cache-Control": "no-cache", "Pragma": "no-cache"})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode("utf-8"))
        stamp = d.get("stamp")
        cont = d.get("continuity", {})
        elapsed = time.time() - start
        valid = cont.get("valid")
        match = stamp == LOCAL
        print(f"[{attempt}] elapsed={elapsed:.0f}s stamp={stamp} continuity.valid={valid} match={match}")
        if match:
            print("MATCH_OK")
            break
    except Exception as e:
        print(f"[{attempt}] error: {e}")
    if time.time() - start >= max_wait:
        print("TIMEOUT_NO_MATCH")
        break
    time.sleep(interval)
