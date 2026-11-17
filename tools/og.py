"""Generate 1200x630 share images into og/. Run: python tools/og.py
Text is English only so one image serves all 11 languages."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "og"
W, H = 1200, 630
FONTS = ["/usr/share/fonts/opentype/inter/Inter-Bold.otf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
FONTS_R = ["/usr/share/fonts/opentype/inter/Inter-Regular.otf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]


def font(paths, size):
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)


def hexagram(d, x, y, fg):  # Qian (15): mountain below earth, drawn top to bottom
    for i, yang in enumerate([0, 0, 0, 1, 0, 0]):
        yy = y + i * 46
        if yang:
            d.rounded_rectangle([x, yy, x + 240, yy + 26], 6, fill=fg)
        else:
            d.rounded_rectangle([x, yy, x + 105, yy + 26], 6, fill=fg)
            d.rounded_rectangle([x + 135, yy, x + 240, yy + 26], 6, fill=fg)


def star(d, cx, cy, fg):
    pts = [(cx + (150 if i % 2 == 0 else 52) * math.sin(i * math.pi / 4),
            cy - (150 if i % 2 == 0 else 52) * math.cos(i * math.pi / 4)) for i in range(8)]
    d.polygon(pts, fill=fg)
    d.ellipse([cx - 175, cy - 175, cx + 175, cy + 175], outline=fg, width=6)


def waves(d, x, cy, fg):
    for i, h in enumerate([60, 130, 210, 270, 190, 120, 230, 150, 80]):
        d.rounded_rectangle([x + i * 30, cy - h // 2, x + i * 30 + 16, cy + h // 2], 8, fill=fg)


def dots(d, x, cy, fg):
    for i in range(3):
        d.ellipse([x + i * 90, cy - 30, x + i * 90 + 60, cy + 30], fill=fg)


IMAGES = {
    "home": ("#3F7A5E", "LC Lab", "Qiangua · AuraSpica Tarot · Audio Cruise", "Free guides in 11 languages", dots, (880, 555)),
    "iching": ("#5B4A32", "Qiangua · I Ching", "64 hexagram cards for daily reflection", "Guides · Coins · Plum Blossom", hexagram, (850, 175)),
    "tarot": ("#3B2F5C", "AuraSpica Tarot", "Tarot · Lenormand · Runes", "Guides for beginners", star, (960, 315)),
    "english": ("#1F5A7A", "Audio Cruise", "Learn English words by listening", "Plays on the lock screen", waves, (860, 315)),
}


def main():
    OUT.mkdir(exist_ok=True)
    big, mid, small = font(FONTS, 76), font(FONTS_R, 38), font(FONTS_R, 30)
    for name, (bg, title, sub, tag, art, pos) in IMAGES.items():
        im = Image.new("RGB", (W, H), bg)
        d = ImageDraw.Draw(im)
        art(d, *pos, "#F6F5F1")
        d.text((80, 200), title, font=big, fill="#FFFFFF")
        d.text((80, 310), sub, font=mid, fill="#E8E6DF")
        d.text((80, 370), tag, font=small, fill="#C9C6BC")
        d.text((80, 540), "lawrence124875.github.io", font=small, fill="#C9C6BC")
        im = im.quantize(64)
        im.save(OUT / f"{name}.png", optimize=True)
        print(name, (OUT / f"{name}.png").stat().st_size)


if __name__ == "__main__":
    main()
