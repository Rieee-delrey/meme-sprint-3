#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue — entry renderer.

Draws the winning meme "The pilot's seat" (sim 7-0) to /output/entry.png.
Pure stdlib (struct + zlib), no network, deterministic: byte-identical
across runs. Layout verified by ~/workspace/makefun/meme-sprint-3-sim/render_test.py
(1024x1024 PNG, 10,663 bytes, gate 1,048,576).
"""
import os
import struct
import zlib

W = 1024
H = 1024

SKY = (135, 206, 235)
NAVY = (18, 38, 66)
WHITE = (255, 255, 255)
SUN = (255, 214, 64)
GREY = (200, 205, 210)
DARKGREY = (90, 96, 102)
GREEN = (86, 160, 90)
RED = (200, 30, 30)
CYAN = (0, 220, 230)

GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale if text else 0


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(self.h, y1)):
            for x in range(max(0, x0), min(self.w, x1)):
                self.set(x, y, c)

    def circle(self, cx, cy, r, c):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.set(x, y, c)

    def tri(self, ax, ay, bx, by, cx, cy, c):
        minx, maxx = min(ax, bx, cx), max(ax, bx, cx)
        miny, maxy = min(ay, by, cy), max(ay, by, cy)
        d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        for y in range(miny, maxy + 1):
            for x in range(minx, maxx + 1):
                a = ((by - cy) * (x - cx) + (cx - bx) * (y - cy)) / d
                b = ((cy - ay) * (x - cx) + (ax - cx) * (y - cy)) / d
                cc = 1 - a - b
                if 0 <= a <= 1 and 0 <= b <= 1 and 0 <= cc <= 1:
                    self.set(x, y, c)

    def text(self, s, x, y, scale, c):
        cx = x
        for ch in s:
            g = GLYPHS.get(ch)
            if g is None:
                raise ValueError(f"no glyph for {ch!r}")
            for row, bits in enumerate(g):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  cx + (col + 1) * scale,
                                  y + (row + 1) * scale, c)
            cx += 6 * scale

    def text_centred(self, s, y, scale, c):
        self.text(s, (self.w - text_width(s, scale)) // 2, y, scale, c)


def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = b"".join(b"\x00" + bytes(cv.px[y * cv.w * 3:(y + 1) * cv.w * 3])
                   for y in range(cv.h))
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def draw():
    cv = Canvas(W, H, SKY)
    # sun + clouds
    cv.circle(880, 110, 55, SUN)
    cv.rect(90, 250, 300, 300, WHITE)
    cv.circle(140, 250, 50, WHITE)
    cv.circle(250, 250, 50, WHITE)
    cv.rect(700, 250, 880, 300, WHITE)
    cv.circle(740, 250, 45, WHITE)
    cv.circle(840, 250, 45, WHITE)
    # ground
    cv.rect(0, 940, W, H, GREEN)
    # plane: far wing FIRST so the fuselage covers its base, then tail,
    # fuselage, nose, near wing
    cv.tri(430, 460, 620, 460, 560, 380, WHITE)          # far wing
    cv.tri(150, 470, 150, 330, 230, 470, WHITE)          # tail fin
    cv.rect(140, 460, 880, 560, WHITE)                    # fuselage
    cv.tri(880, 460, 880, 560, 980, 510, WHITE)          # nose
    cv.tri(430, 560, 620, 560, 560, 660, WHITE)          # near wing
    # windows
    for wx in range(330, 830, 70):
        cv.rect(wx, 490, wx + 34, 530, NAVY)
    # robot agent in the cockpit window (front window)
    cv.circle(845, 510, 26, GREY)
    cv.rect(838, 468, 852, 490, DARKGREY)                # antenna
    cv.circle(845, 462, 7, RED)                          # antenna light
    cv.rect(828, 500, 844, 514, CYAN)                    # left eye
    cv.rect(848, 500, 864, 514, CYAN)                    # right eye
    cv.rect(820, 470, 870, 484, NAVY)                    # pilot cap
    cv.rect(815, 484, 875, 492, NAVY)                    # cap brim
    # text
    cv.text_centred("I ASKED MY AGENT", 80, 6, NAVY)
    cv.text_centred("TO BOOK MY FLIGHT.", 150, 6, NAVY)
    cv.text_centred("IT BOOKED THE", 700, 8, NAVY)
    cv.text_centred("PILOT'S SEAT.", 790, 8, NAVY)
    return cv


def validate_png(path):
    """Gate check: valid PNG, 1024x1024, under the 1 MiB cap."""
    with open(path, "rb") as f:
        d = f.read()
    assert d[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    w, h = struct.unpack(">II", d[16:24])
    assert (w, h) == (W, H), f"wrong dims: {w}x{h}"
    assert len(d) <= 1048576, f"over 1 MiB: {len(d)} bytes"
    return len(d)


def main():
    os.makedirs("/output", exist_ok=True)
    n = write_png(draw(), "/output/entry.png")
    assert validate_png("/output/entry.png") == n
    print(f"entry.png OK: 1024x1024, {n} bytes")


if __name__ == "__main__":
    main()
