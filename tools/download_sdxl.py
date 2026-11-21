import os
import time
import urllib.request

TARGETS = [
    ("https://hf-mirror.com/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors",
     r"D:\sd-webui-aki-v4\sd-webui-forge-aki-v1.0\models\Stable-diffusion\sd_xl_base_1.0.safetensors",
     6938078334),
    ("https://hf-mirror.com/nerijs/pixel-art-xl/resolve/main/pixel-art-xl.safetensors",
     r"D:\sd-webui-aki-v4\sd-webui-forge-aki-v1.0\models\Lora\pixel-art-xl.safetensors",
     170543052),
]

def fetch(url, dst, total):
    part = dst + ".part"
    for attempt in range(1, 60):
        pos = os.path.getsize(part) if os.path.exists(part) else 0
        if pos >= total:
            break
        headers = {"User-Agent": "Mozilla/5.0"}
        if pos:
            headers["Range"] = f"bytes={pos}-"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as r, open(part, "ab" if pos else "wb") as f:
                done = pos
                last = done
                while True:
                    chunk = r.read(1024 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    done += len(chunk)
                    if done - last >= 300 * 1024 * 1024:
                        print(f"{os.path.basename(dst)}: {done/1024/1024:.0f}/{total/1024/1024:.0f} MB", flush=True)
                        last = done
        except Exception as e:
            print(f"{os.path.basename(dst)} attempt {attempt}: {e!r}", flush=True)
            time.sleep(3)
    size = os.path.getsize(part) if os.path.exists(part) else 0
    if size >= total:
        os.replace(part, dst)
        print("done", dst, size, flush=True)
    else:
        print("incomplete", dst, size, flush=True)

for url, dst, total in TARGETS:
    fetch(url, dst, total)
