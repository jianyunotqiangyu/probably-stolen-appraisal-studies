import os
import time
import urllib.request

URL = "https://hf-mirror.com/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors"
DST = r"D:\sd-webui-aki-v4\sd-webui-forge-aki-v1.0\models\Stable-diffusion\v1-5-pruned-emaonly.safetensors"
PART = DST + ".part"

TOTAL = 4265146304

for attempt in range(1, 80):
    pos = os.path.getsize(PART) if os.path.exists(PART) else 0
    if pos >= TOTAL:
        break
    headers = {"User-Agent": "Mozilla/5.0"}
    if pos:
        headers["Range"] = f"bytes={pos}-"
    try:
        req = urllib.request.Request(URL, headers=headers)
        with urllib.request.urlopen(req, timeout=60) as r, open(PART, "ab" if pos else "wb") as f:
            if pos and r.status != 206:
                # 服务器不支持断点，从头来
                f.close()
                os.remove(PART)
                pos = 0
                f = open(PART, "wb")
            done = pos
            last = done
            while True:
                chunk = r.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                done += len(chunk)
                if done - last >= 200 * 1024 * 1024:
                    print(f"attempt {attempt}: {done/1024/1024:.0f} / {TOTAL/1024/1024:.0f} MB", flush=True)
                    last = done
        print(f"attempt {attempt} ended at {os.path.getsize(PART)/1024/1024:.0f} MB", flush=True)
    except Exception as e:
        print(f"attempt {attempt} error: {e!r}", flush=True)
        time.sleep(3)

size = os.path.getsize(PART) if os.path.exists(PART) else 0
print("final size", size, "expected", TOTAL, flush=True)
if size >= TOTAL:
    os.replace(PART, DST)
    print("done", DST, flush=True)
else:
    print("incomplete", flush=True)
