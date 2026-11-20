"""One-day world news image for Friday 20 November 2026 (news-image-20261120).

Draws a newspaper front page in pure Python 3.13 standard library only:
a hand-written PNG encoder (zlib/struct/binascii), an embedded 5x7 bitmap
font stored as integer bitmasks, and canvas drawing primitives. No network,
no files read, no clock, no randomness -- two runs write byte-identical PNGs.

Composition: a dark masthead band naming the day, a hero on Cyclone Akvan
bearing down on India's east coast, then four stories -- Trump pushing any
Iran decision past 1 January, Europe ready for Ukraine peace talks with
Russia, Voyager 1 a light-day from Earth, GTA VI's record launch -- plus a
ticker of the day's other stories and a footer naming the sources.

Local run:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import binascii
import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 232)
INK = (22, 22, 22)
NAVY = (18, 38, 66)
TEAL = (14, 110, 120)
RED = (178, 34, 44)
GOLD = (198, 154, 38)
GREEN = (38, 102, 66)
SKY = (52, 130, 178)
GREY = (110, 106, 96)
LIGHT = (231, 225, 206)
WHITE = (250, 248, 242)

# 5x7 bitmap font. Each glyph is 7 rows; each row is a 5-bit integer,
# most significant bit on the left. Written by hand for this entry.
GLYPHS = {
    'A': (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    'B': (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    'C': (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    'D': (0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110),
    'E': (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    'F': (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    'G': (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    'H': (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    'I': (0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    'J': (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    'K': (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    'L': (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    'M': (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    'N': (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    'O': (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    'P': (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    'Q': (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    'R': (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    'S': (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    'T': (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    'U': (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    'V': (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    'W': (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001),
    'X': (0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    'Y': (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    'Z': (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    '0': (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    '1': (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    '2': (0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111),
    '3': (0b11110, 0b00001, 0b00001, 0b01110, 0b00001, 0b00001, 0b11110),
    '4': (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    '5': (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    '6': (0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    '7': (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    '8': (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    '9': (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 0b01100, 0b01100),
    ',': (0, 0, 0, 0, 0b01100, 0b00100, 0b01000),
    '-': (0, 0, 0, 0b01110, 0, 0, 0),
    "'": (0b00100, 0b00100, 0b01000, 0, 0, 0, 0),
    '$': (0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100),
    '%': (0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    '&': (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
    '/': (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    '(': (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ')': (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    '!': (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0, 0b00100),
    '?': (0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0, 0b00100),
    '+': (0, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0),
    '=': (0, 0, 0b11111, 0, 0b11111, 0, 0),
    ':': (0, 0b01100, 0b01100, 0, 0b01100, 0b01100, 0),
    ';': (0, 0b01100, 0b01100, 0, 0b01100, 0b00100, 0b01000),
    '"': (0b01010, 0b01010, 0b01010, 0, 0, 0, 0),
    '*': (0, 0b00100, 0b10101, 0b01110, 0b10101, 0b00100, 0),
}


class Page:
    """An RGB canvas with drawing primitives."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.pxbuf = bytearray(w * h * 3)
        self.paint(bg)

    def paint(self, rgb):
        self.pxbuf[:] = bytes(rgb) * (self.w * self.h)

    def set(self, x, y, rgb):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.pxbuf[i:i + 3] = bytes(rgb)

    def box(self, x0, y0, x1, y1, rgb):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w, x1)
        y1 = min(self.h, y1)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            self.pxbuf[i:i + (x1 - x0) * 3] = bytes(rgb) * (x1 - x0)

    def hbar(self, x0, x1, y, rgb, t=1):
        for k in range(t):
            self.box(x0, y + k, x1, y + k + 1, rgb)

    def vbar(self, x, y0, y1, rgb, t=1):
        for k in range(t):
            self.box(x + k, y0, x + k + 1, y1, rgb)

    def frame(self, x0, y0, x1, y1, rgb, t=2):
        self.hbar(x0, x1, y0, rgb, t)
        self.hbar(x0, x1, y1 - t, rgb, t)
        self.vbar(x0, y0, y1, rgb, t)
        self.vbar(x1 - t, y0, y1, rgb, t)

    def segment(self, x0, y0, x1, y1, rgb, t=1):
        """Bresenham line with square brush of thickness t."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.box(x - t // 2, y - t // 2, x + t // 2 + 1, y + t // 2 + 1, rgb)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def filled_circle(self, cx, cy, r, rgb):
        for y in range(cy - r, cy + r + 1):
            dy = y - cy
            dx = int((r * r - dy * dy) ** 0.5)
            self.box(cx - dx, y, cx + dx + 1, y + 1, rgb)

    def circle(self, cx, cy, r, rgb, t=2):
        for y in range(cy - r - t, cy + r + t + 1):
            for x in range(cx - r - t, cx + r + t + 1):
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if abs(d - r) <= t / 2:
                    self.set(x, y, rgb)

    def triangle(self, x0, y0, x1, y1, x2, y2, rgb):
        pts = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        for y in range(ay, cy + 1):
            if y < by:
                xa = ax + (bx - ax) * (y - ay) / max(1, by - ay)
            else:
                xa = bx + (cx - bx) * (y - by) / max(1, cy - by)
            xb = ax + (cx - ax) * (y - ay) / max(1, cy - ay)
            lo, hi = int(min(xa, xb)), int(max(xa, xb))
            self.box(lo, y, hi + 1, y + 1, rgb)

    def glyph(self, x, y, s, rgb, ch):
        rows = GLYPHS.get(ch, GLYPHS[' '])
        for row in range(7):
            bits = rows[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    self.box(x + col * s, y + row * s,
                             x + col * s + s, y + row * s + s, rgb)

    def text(self, x, y, s, rgb, string):
        cx = x
        for ch in string.upper():
            self.glyph(cx, y, s, rgb, ch)
            cx += 6 * s
        return cx

    def text_width(self, s, string):
        return len(string) * 6 * s - s

    def centred(self, cx, y, s, rgb, string):
        self.text(cx - self.text_width(s, string) // 2, y, s, rgb, string)

    def wrapped(self, string, max_w, s):
        lines = []
        cur = ''
        for word in string.upper().split(' '):
            trial = (cur + ' ' + word).strip()
            if self.text_width(s, trial) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


def write_png(page, path):
    raw = bytearray()
    stride = page.w * 3
    for y in range(page.h):
        raw.append(0)  # filter: none
        raw += page.pxbuf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        body = struct.pack('>I', len(data)) + tag + data
        return body + struct.pack('>I', binascii.crc32(tag + data) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', page.w, page.h, 8, 2, 0, 0, 0)
    png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', comp) + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


# ---- pictograms ----

def spiral_storm(p, cx, cy):
    """A cyclone seen from above: concentric arcs spiralling inward."""
    for k in range(6):
        r = 108 - k * 17
        start = k * 0.9
        end = start + 4.6
        steps = 60
        prev = None
        for i in range(steps + 1):
            a = start + (end - start) * i / steps
            x = cx + int(r * math.cos(a))
            y = cy + int(r * math.sin(a) * 0.92)
            if prev is not None:
                p.segment(prev[0], prev[1], x, y, TEAL if k % 2 else NAVY, 4)
            prev = (x, y)
    p.filled_circle(cx, cy, 13, PAPER)
    p.circle(cx, cy, 13, RED, 3)
    # rain streaks falling from the storm
    for dx in (-118, -96, 96, 118):
        p.segment(cx + dx, cy + 74, cx + dx - 8, cy + 96, SKY, 3)


def clock_icon(p, cx, cy):
    p.circle(cx, cy, 34, NAVY, 4)
    p.filled_circle(cx, cy, 34, WHITE)
    p.circle(cx, cy, 34, NAVY, 3)
    p.segment(cx, cy, cx, cy - 22, NAVY, 3)
    p.segment(cx, cy, cx + 16, cy + 8, NAVY, 3)
    p.filled_circle(cx, cy, 4, RED)


def talks_icon(p, cx, cy):
    # two speech bubbles facing each other
    p.box(cx - 44, cy - 30, cx - 2, cy + 2, TEAL)
    p.triangle(cx - 34, cy + 2, cx - 22, cy + 2, cx - 30, cy + 16, TEAL)
    p.box(cx + 2, cy - 6, cx + 44, cy + 26, GOLD)
    p.triangle(cx + 22, cy + 26, cx + 34, cy + 26, cx + 30, cy + 40, GOLD)
    p.box(cx - 36, cy - 22, cx - 10, cy - 14, WHITE)
    p.box(cx - 36, cy - 10, cx - 18, cy - 2, WHITE)
    p.box(cx + 10, cy + 2, cx + 36, cy + 10, WHITE)
    p.box(cx + 10, cy + 14, cx + 28, cy + 22, WHITE)


def probe_icon(p, cx, cy):
    # Voyager-style probe: dish, body, boom, panels
    p.filled_circle(cx, cy, 12, GOLD)
    p.circle(cx, cy, 12, INK, 2)
    p.box(cx - 6, cy + 8, cx + 6, cy + 26, NAVY)
    p.segment(cx + 6, cy + 18, cx + 34, cy + 4, NAVY, 3)
    p.filled_circle(cx + 36, cy + 2, 4, RED)
    p.segment(cx - 6, cy + 18, cx - 40, cy + 30, NAVY, 3)
    p.box(cx - 52, cy + 24, cx - 36, cy + 40, TEAL)
    p.box(cx + 8, cy + 30, cx + 40, cy + 38, TEAL)
    # a few stars around the probe
    for dx, dy in ((-48, -34), (30, -30), (44, -14)):
        p.filled_circle(cx + dx, cy + dy, 2, GOLD)


def pad_icon(p, cx, cy):
    # game controller
    p.box(cx - 44, cy - 18, cx + 44, cy + 22, NAVY)
    p.filled_circle(cx - 44, cy + 14, 12, NAVY)
    p.filled_circle(cx + 44, cy + 14, 12, NAVY)
    p.box(cx - 26, cy - 6, cx - 14, cy + 6, WHITE)
    p.box(cx - 22, cy - 10, cx - 18, cy + 10, WHITE)
    p.box(cx - 2, cy - 2, cx + 2, cy + 2, WHITE)
    for dx, dy in ((16, -8), (26, 2), (16, 10), (6, 2)):
        p.filled_circle(cx + dx, cy + dy, 3, GOLD)


# ---- layout ----

def story(p, x0, y0, x1, y1, kicker, headline, body, icon, accent):
    p.frame(x0, y0, x1, y1, INK, 2)
    p.box(x0 + 2, y0 + 2, x1 - 2, y0 + 34, accent)
    p.text(x0 + 14, y0 + 10, 2, WHITE, kicker)
    icon(p, x1 - 62, y0 + 78)
    lines = p.wrapped(headline, (x1 - x0) - 120, 4)
    y = y0 + 48
    for ln in lines:
        p.text(x0 + 14, y, 4, INK, ln)
        y += 34
    y += 4
    for ln in p.wrapped(body, (x1 - x0) - 28, 2):
        p.text(x0 + 14, y, 2, INK, ln)
        y += 18


def draw():
    p = Page(W, H, PAPER)

    # ---- masthead: dark band naming the day ----
    p.box(0, 0, W, 118, NAVY)
    p.hbar(0, W, 118, RED, 6)
    p.centred(512, 16, 7, WHITE, "THE WORLD TODAY")
    p.centred(512, 66, 3, GOLD, "FRIDAY 20 NOVEMBER 2026")
    p.text(24, 92, 1, WHITE, "DAY 324 OF 2026")
    right = "ONE DAY - ONE PAGE - ALL THE NEWS"
    p.text(W - 24 - p.text_width(1, right), 92, 1, WHITE, right)

    # ---- hero: Cyclone Akvan ----
    p.frame(24, 132, 1000, 436, INK, 3)
    p.box(26, 134, 396, 434, LIGHT)
    p.vbar(396, 134, 434, INK, 2)
    spiral_storm(p, 210, 284)
    p.centred(210, 404, 1, GREY, "SEVERE CYCLONIC STORM AKVAN")
    p.text(420, 152, 2, RED, "BAY OF BENGAL - WEATHER")
    y = 182
    for ln in ("CYCLONE AKVAN", "BEARS DOWN", "ON INDIA"):
        p.text(420, y, 5, INK, ln)
        y += 42
    y += 4
    for ln in p.wrapped("SEVERE STORM DUE TO CROSS THE ODISHA AND "
                        "ANDHRA COASTS BY NOON TODAY. MORE THAN "
                        "300,000 PEOPLE MOVED TO SAFETY, 423 RESCUE "
                        "TEAMS ON STANDBY, 69 TRAINS CANCELLED.",
                        560, 2):
        p.text(420, y, 2, INK, ln)
        y += 18
    # stat chips
    stats = [("300,000+", "EVACUATED"), ("90-100 KM/H", "LANDFALL WINDS"),
             ("BY NOON", "LANDFALL TODAY")]
    bx = 420
    for num, lab in stats:
        p.frame(bx, 392, bx + 178, 424, NAVY, 2)
        p.centred(bx + 89, 398, 2, NAVY, num)
        p.centred(bx + 89, 414, 1, GREY, lab)
        bx += 192

    # ---- middle row: Trump / Iran, Europe / Ukraine ----
    story(p, 24, 452, 500, 692, "WASHINGTON - IRAN",
          "TRUMP: NO RUSH ON IRAN",
          "THE PRESIDENT SAYS THE US WILL \"SEE WHAT HAPPENS\" "
          "AFTER 1 JANUARY, PUSHING ANY WAR DECISION INTO 2027.",
          clock_icon, RED)
    story(p, 524, 452, 1000, 692, "BERLIN - UKRAINE",
          "EUROPE READY FOR PEACE TALKS",
          "LEADERS SAY THEY WILL NEGOTIATE WITH RUSSIA, BUT ANY "
          "DEAL MUST BE ACCEPTABLE TO KYIV AND TO EUROPE.",
          talks_icon, TEAL)

    # ---- bottom row: Voyager, GTA VI ----
    story(p, 24, 708, 500, 930, "DEEP SPACE - NASA",
          "VOYAGER 1 A LIGHT-DAY AWAY",
          "NASA CONFIRMS THE 1977 PROBE IS THE FIRST CRAFT A "
          "LIGHT-DAY FROM EARTH, 26 BILLION KM OUT. ITS SIGNAL "
          "TAKES A DAY TO ARRIVE.",
          probe_icon, NAVY)
    story(p, 524, 708, 1000, 930, "VICE CITY - CULTURE",
          "GTA VI TOPS $1.84BN",
          "SENSOR TOWER ESTIMATES THE GAME BEAT THE ODYSSEY'S "
          "$1.805BN BOX OFFICE - THE BIGGEST LAUNCH EVER.",
          pad_icon, GREEN)

    # ---- ticker: two centred lines, no label ----
    p.box(24, 946, 1000, 988, RED)
    p.centred(512, 952, 1, WHITE,
              "ALSO TODAY: HOUTHI MISSILE THREAT AT RIYADH, SAUDI "
              "COALITION SAYS - NICHOLLS 113 NOT OUT AS NZ REACH 243/5 VS INDIA")
    p.centred(512, 968, 1, WHITE,
              "WORLD CHILDREN'S DAY MARKED TODAY - SENSEX AT 83,022 "
              "AFTER THURSDAY RALLY")

    # ---- footer ----
    p.hbar(24, 1000, 998, INK, 2)
    p.centred(512, 1006, 1, GREY,
              "EVERY STORY HAPPENED OR WAS FIRST REPORTED ON FRIDAY "
              "20 NOVEMBER 2026 - SOURCES: REUTERS, BBC, IMD, SENSOR TOWER")
    return p


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(draw(), path)
    print("wrote %s (%d bytes, 1024x1024)" % (path, size))


if __name__ == "__main__":
    main()
