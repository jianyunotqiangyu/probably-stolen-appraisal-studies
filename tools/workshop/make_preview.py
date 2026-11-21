"""把封面压成 1280×720、<1 MB 的 preview.png（路径由环境变量传入）。"""
import os
import sys

from PIL import Image

src = os.environ["PREVIEW_SRC"]
dst = os.environ["PREVIEW_DST"]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    im = Image.open(src).convert("RGB")
    im = im.resize((1280, 720), Image.LANCZOS)
    im.save(dst, optimize=True)

    if os.path.getsize(dst) > 1000 * 1024:
        im.quantize(colors=256, method=Image.MEDIANCUT).save(dst, optimize=True)

    print(f"preview: {im.size} {round(os.path.getsize(dst) / 1024, 1)} KB")


if __name__ == "__main__":
    main()
