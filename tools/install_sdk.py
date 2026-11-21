import os
import urllib.request
import zipfile

URL = "https://builds.dotnet.microsoft.com/dotnet/Sdk/8.0.404/dotnet-sdk-8.0.404-win-x64.zip"
ROOT = r"D:\DSH_workspace\mod-create\tools"
ZIP = os.path.join(ROOT, "dotnet-sdk.zip")
OUT = os.path.join(ROOT, "dotnet")

os.makedirs(ROOT, exist_ok=True)
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=120) as r, open(ZIP, "wb") as f:
    while True:
        chunk = r.read(1024 * 256)
        if not chunk:
            break
        f.write(chunk)

with zipfile.ZipFile(ZIP) as z:
    z.extractall(OUT)

os.remove(ZIP)
print("SDK extracted to", OUT)
