#!/usr/bin/env python3
"""Render the 23 November 2026 world-news poster to artwork.png.

Deterministic, Pillow only, no network. Run: python3 render_artwork.py
"""
import textwrap
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 243, 234)
INK = (24, 24, 28)
NAVY = (18, 38, 66)
RED = (178, 34, 34)
ORANGE = (204, 85, 0)
TEAL = (0, 110, 110)
AMBER = (176, 112, 0)
PURPLE = (84, 48, 120)
STEEL = (52, 84, 120)
GREY = (90, 90, 90)
WHITE = (255, 255, 255)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_icon(d, kind, x, y, s, color):
    """Simple flat geometric icon inside a square of side s at (x, y)."""
    if kind == "flame":  # COP31 / climate fire
        d.polygon([(x + s * 0.5, y), (x + s * 0.85, y + s * 0.45),
                   (x + s * 0.95, y + s * 0.75), (x + s * 0.7, y + s),
                   (x + s * 0.3, y + s), (x + s * 0.05, y + s * 0.75),
                   (x + s * 0.15, y + s * 0.45)], fill=color)
        d.polygon([(x + s * 0.5, y + s * 0.45), (x + s * 0.68, y + s * 0.7),
                   (x + s * 0.5, y + s * 0.9), (x + s * 0.32, y + s * 0.7)],
                  fill=(255, 220, 120))
    elif kind == "ship":
        d.polygon([(x, y + s * 0.55), (x + s, y + s * 0.55),
                   (x + s * 0.85, y + s * 0.9), (x + s * 0.15, y + s * 0.9)],
                  fill=color)
        d.rectangle([x + s * 0.3, y + s * 0.2, x + s * 0.7, y + s * 0.55], fill=color)
        d.polygon([(x + s * 0.5, y), (x + s * 0.5, y + s * 0.25),
                   (x + s * 0.8, y + s * 0.25)], fill=RED)
    elif kind == "building":
        d.rectangle([x + s * 0.1, y + s * 0.25, x + s * 0.9, y + s], fill=color)
        for r in range(3):
            for c in range(3):
                d.rectangle([x + s * (0.2 + c * 0.24), y + s * (0.35 + r * 0.2),
                             x + s * (0.32 + c * 0.24), y + s * (0.47 + r * 0.2)],
                            fill=(255, 220, 120))
        d.polygon([(x + s * 0.5, y), (x + s * 0.95, y + s * 0.25),
                   (x + s * 0.05, y + s * 0.25)], fill=RED)
    elif kind == "factory":
        d.rectangle([x, y + s * 0.4, x + s * 0.7, y + s], fill=color)
        d.rectangle([x + s * 0.75, y + s * 0.1, x + s * 0.95, y + s], fill=color)
        d.polygon([(x, y + s * 0.4), (x + s * 0.18, y + s * 0.2),
                   (x + s * 0.36, y + s * 0.4)], fill=color)
        d.ellipse([x + s * 0.05, y, x + s * 0.35, y + s * 0.25], fill=GREY)
        d.ellipse([x + s * 0.4, y - s * 0.08, x + s * 0.6, y + s * 0.12], fill=GREY)
    elif kind == "badge":
        cx, cy, r = x + s * 0.5, y + s * 0.5, s * 0.48
        pts = []
        import math
        for i in range(10):
            ang = math.pi * i / 5 - math.pi / 2
            rr = r if i % 2 == 0 else r * 0.55
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        d.polygon(pts, fill=color)
        d.ellipse([cx - r * 0.35, cy - r * 0.35, cx + r * 0.35, cy + r * 0.35],
                  fill=(255, 220, 120))
    elif kind == "chip":
        d.rounded_rectangle([x + s * 0.15, y + s * 0.15, x + s * 0.85, y + s * 0.85],
                            radius=6, fill=color)
        d.rectangle([x + s * 0.35, y + s * 0.35, x + s * 0.65, y + s * 0.65],
                    fill=(255, 220, 120))
        for i in range(3):
            d.rectangle([x + s * (0.25 + i * 0.25), y, x + s * (0.33 + i * 0.25),
                         y + s * 0.15], fill=color)
            d.rectangle([x + s * (0.25 + i * 0.25), y + s * 0.85,
                         x + s * (0.33 + i * 0.25), y + s], fill=color)


STORIES = [
    ("CLIMATE", ORANGE, "flame",
     "COP31 COLLAPSES",
     "Climate talks in Antalya end with no deal after the EU rejects a pact that omits fossil fuels."),
    ("WAR IN EUROPE", STEEL, "ship",
     "SHIP ABLAZE OFF FINLAND",
     "A Russian cargo ship burns after a Ukrainian drone strike; the blaze is still raging."),
    ("UKRAINE", RED, "building",
     "14 MISSING IN KYIV REGION",
     "A Russian drone hits a residential building; rescuers search the rubble for survivors."),
    ("DISASTER", AMBER, "factory",
     "FACTORY FIRE IN INDONESIA",
     "Seven dead and 50 missing after a blaze sweeps a factory; the search goes on."),
    ("CRIME", PURPLE, "badge",
     "CARTEL KINGPIN CAPTURED",
     "Mexico seizes FBI most-wanted boss 'El Chapo Isidro' after gunfights leave 11 dead."),
    ("TECH", TEAL, "chip",
     "MINISTER QUITS OVER AI CHEATING",
     "South Korea's education minister resigns in an AI exam-cheating scandal."),
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # outer frame
    d.rectangle([10, 10, W - 11, H - 11], outline=INK, width=4)
    d.rectangle([22, 22, W - 23, H - 23], outline=INK, width=1)

    # masthead
    title_f = font(SERIF_B, 74)
    title = "THE WORLD IN A DAY"
    tw = d.textlength(title, font=title_f)
    d.text(((W - tw) / 2, 46), title, font=title_f, fill=NAVY)
    d.line([60, 140, W - 60, 140], fill=INK, width=3)
    date_f = font(SANS_B, 30)
    date = "MONDAY  •  23 NOVEMBER 2026"
    dw = d.textlength(date, font=date_f)
    d.text(((W - dw) / 2, 156), date, font=date_f, fill=RED)
    d.line([60, 200, W - 60, 200], fill=INK, width=3)

    # story grid: 2 cols x 3 rows
    gx, gy = 44, 222
    cw, ch = 460, 236
    gapx, gapy = 16, 14
    tag_f = font(SANS_B, 20)
    head_f = font(SANS_B, 31)
    body_f = font(SANS, 22)
    for i, (tag, color, icon, head, body) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x0 = gx + col * (cw + gapx)
        y0 = gy + row * (ch + gapy)
        d.rectangle([x0, y0, x0 + cw, y0 + ch], outline=INK, width=2, fill=WHITE)
        d.rectangle([x0, y0, x0 + cw, y0 + 34], fill=color)
        d.text((x0 + 12, y0 + 6), tag, font=tag_f, fill=WHITE)
        # icon
        draw_icon(d, icon, x0 + 14, y0 + 48, 72, color)
        # headline + body to the right of icon
        tx = x0 + 92
        twd = cw - 92 - 14
        lines = wrap(d, head, head_f, twd)
        yy = y0 + 48
        for ln in lines[:2]:
            d.text((tx, yy), ln, font=head_f, fill=INK)
            yy += 36
        blines = wrap(d, body, body_f, twd)
        yy += 4
        for ln in blines:
            if yy + 27 > y0 + ch - 8:
                break
            d.text((tx, yy), ln, font=body_f, fill=(60, 60, 60))
            yy += 27

    # footer
    foot_f = font(SANS, 20)
    foot = "Six stories that defined the day  •  Sources: Reuters, AP, Helsinki Times, Arab News"
    fw = d.textlength(foot, font=foot_f)
    d.text(((W - fw) / 2, H - 52), foot, font=foot_f, fill=GREY)

    img.save("artwork.png", optimize=True)
    print("wrote artwork.png", img.size)


if __name__ == "__main__":
    main()
