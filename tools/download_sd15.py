import os
import urllib.request

URL = "https://hf-mirror.com/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors"
DST = r"D:\sd-webui-aki-v4\sd-webui-forge-aki-v1.0\models\Stable-diffusion\v1-5-pruned-emaonly.safetensors"
PART = DST + ".part"

req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=120) as r, open(PART, "wb") as f:
    total = int(r.headers.get("Content-Length") or 0)
    done = 0
    while True:
        chunk = r.read(1024 * 1024)
        if not chunk:
            break
        f.write(chunk)
        done += len(chunk)
        if total and done % (200 * 1024 * 1024) < 1024 * 1024:
            print(f"{done/1024/1024:.0f} / {total/1024/1024:.0f} MB", flush=True)

os.replace(PART, DST)
print("done", DST, os.path.getsize(DST))
