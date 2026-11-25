#!/usr/bin/env python3
"""THE WORLD TODAY -- Wednesday 25 November 2026.

A one-page newspaper front page that sums up the day's world news.
Pure Python 3.13 standard library: no third-party packages, no network,
no fonts on disk. The page is drawn pixel by pixel with a small built-in
5x7 bitmap face, then encoded as a PNG by hand (zlib + struct only).

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py
Writes exactly one file: <output>/entry.png (1024x1024, well under 1 MiB).
The program is fully deterministic: two runs write byte-identical files.

Stories were verified against live reporting on 25 November 2026
(Reuters, AP, CNN, Xinhua, WHO, UN). Every headline below names an event
that happened, or was first reported, on that day.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)   # newsprint cream
INK = (22, 22, 22)        # headline black
RED = (164, 22, 33)       # kicker red
NAVY = (15, 34, 62)       # lead-art night sky
SKY = (31, 82, 140)       # earth blue
TEAL = (24, 96, 104)      # earth sea
GREEN = (74, 140, 82)     # earth land
GREY = (96, 91, 80)       # captions, rules
FAINT = (228, 222, 206)   # hairlines on paper
WHITE = (255, 255, 255)
FLAME = (232, 116, 30)
EMBER = (248, 196, 66)
SMOKE = (196, 192, 182)

# ------------------------------------------------------- 5x7 bitmap face
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is blank. Uppercase,
# lowercase, digits and the punctuation the page needs. Anything unknown
# renders as '?'.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    'a': ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    'b': ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    'c': ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    'd': ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    'e': ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    'f': ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    'g': ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    'h': ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    'i': ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    'j': ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    'k': ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    'l': ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    'm': ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    'n': ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    'o': ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    'p': ("00000", "11110", "10001", "10001", "11110", "10000", "10000"),
    'q': ("00000", "01111", "10001", "10001", "01111", "00001", "00001"),
    'r': ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    's': ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    't': ("01000", "01000", "11110", "01000", "01000", "01000", "00110"),
    'u': ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    'v': ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    'w': ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    'x': ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    'y': ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    'z': ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '\u2014': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '\u2019': ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '\u2018': ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '\u201c': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '\u201d': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '|': ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '\u00b7': ("00000", "00000", "00000", "01100", "01100", "00000", "00000"),
    '\u2022': ("00000", "00000", "01110", "01110", "01110", "00000", "00000"),
}

GLYPH_W, GLYPH_H, GLYPH_GAP = 5, 7, 1


def text_width(text, scale):
    """Pixel width of text drawn at the given scale (no trailing gap)."""
    if not text:
        return 0
    return len(text) * (GLYPH_W + GLYPH_GAP) * scale - GLYPH_GAP * scale


# ------------------------------------------------------------------ canvas
class Canvas:
    """A plain RGB frame buffer with tiny vector helpers."""

    def __init__(self, width, height, background):
        self.w, self.h = width, height
        self.px = bytearray(background * (width * height))

    def set(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = colour

    def rect(self, x, y, w, h, colour):
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = colour

    def hline(self, x, y, w, colour, thick=1):
        self.rect(x, y, w, thick, colour)

    def vline(self, x, y, h, colour, thick=1):
        self.rect(x, y, thick, h, colour)

    def line(self, x0, y0, x1, y1, colour, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.rect(x0, y0, thick, thick, colour)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            span = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - span, yy, span * 2 + 1, 1, colour)

    def ring(self, cx, cy, r, colour, thick=2):
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - thick) ** 2 <= d2 <= (r + thick) ** 2:
                    self.set(xx, yy, colour)

    def polygon(self, points, colour):
        """Scanline fill for a simple polygon (even-odd rule)."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for yy in range(min(ys), max(ys) + 1):
            nodes = []
            n = len(points)
            for k in range(n):
                x0, y0 = points[k]
                x1, y1 = points[(k + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    nodes.append(x0 + (yy - y0) * (x1 - x0) / (y1 - y0))
            nodes.sort()
            for k in range(0, len(nodes) - 1, 2):
                self.rect(int(nodes[k]), yy, int(nodes[k + 1]) - int(nodes[k]) + 1, 1, colour)

    # ------------------------------------------------------------ typography
    def glyph(self, x, y, ch, scale, colour):
        rows = FONT.get(ch, FONT['?'])
        for ry, row in enumerate(rows):
            for rx, cell in enumerate(row):
                if cell == '1':
                    self.rect(x + rx * scale, y + ry * scale, scale, scale, colour)

    def text(self, x, y, s, scale, colour, align='left'):
        """Draw one line; returns the x of its right edge."""
        if align == 'center':
            x -= text_width(s, scale) // 2
        elif align == 'right':
            x -= text_width(s, scale)
        cx = x
        for ch in s:
            self.glyph(cx, y, ch, scale, colour)
            cx += (GLYPH_W + GLYPH_GAP) * scale
        return cx - GLYPH_GAP * scale

    def wrap(self, s, scale, max_w):
        """Greedy word wrap; returns a list of lines that fit max_w."""
        words = s.split(' ')
        lines, cur = [], ''
        for word in words:
            trial = word if not cur else cur + ' ' + word
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, scale, colour, max_w, leading=4):
        """Draw a wrapped paragraph; returns the y just below it."""
        for line in self.wrap(s, scale, max_w):
            self.text(x, y, line, scale, colour)
            y += GLYPH_H * scale + leading
        return y


# --------------------------------------------------------------------- png
def encode_png(width, height, rgb):
    def chunk(tag, data):
        out = struct.pack('>I', len(data)) + tag + data
        return out + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = bytearray()
    stride = width * 3
    for yy in range(height):
        raw.append(0)
        raw += rgb[yy * stride:(yy + 1) * stride]
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + chunk(b'IEND', b''))


# ------------------------------------------------------------------- layout
MX = 28                      # page margin
CW = W - 2 * MX              # content width: 968


def draw_rocket_panel(cv, x, y, w, h):
    """Night-sky panel: Shenzhou-24 climbing past the Earth."""
    cv.rect(x, y, w, h, NAVY)
    cx = x + w // 2
    # Fixed stars, so the picture never changes between runs.
    stars = [(18, 22), (52, 58), (96, 18), (150, 44), (210, 26), (268, 62),
             (330, 30), (352, 96), (36, 128), (120, 108), (196, 132),
             (300, 150), (344, 178), (66, 196), (150, 214), (240, 196),
             (318, 232), (24, 262), (180, 258), (286, 282)]
    for sx, sy in stars:
        cv.rect(x + sx - 1, y + sy, 3, 1, WHITE)
        cv.rect(x + sx, y + sy - 1, 1, 3, WHITE)
    # Earth rising along the bottom of the panel.
    earth_cy = y + h + 96
    cv.disc(cx, earth_cy, 168, SKY)
    cv.disc(cx - 62, earth_cy - 118, 34, GREEN)
    cv.disc(cx + 48, earth_cy - 132, 26, GREEN)
    cv.disc(cx + 96, earth_cy - 96, 16, GREEN)
    cv.disc(cx - 108, earth_cy - 84, 12, GREEN)
    # The disc spills past the panel's foot: repaint that strip as paper
    # before anything below the panel is drawn.
    cv.rect(x, y + h, w, 264, PAPER)
    # Rocket: nose, body, window, fins, flame, smoke.
    nose_y, body_y, body_h, half = y + 26, y + 58, 108, 27
    cv.polygon([(cx - half, body_y), (cx + half, body_y), (cx, nose_y)], WHITE)
    cv.rect(cx - half, body_y, half * 2, body_h, WHITE)
    cv.hline(cx - half, body_y, half * 2, (210, 214, 220), 3)
    cv.ring(cx, body_y + 42, 13, SKY, 3)
    cv.disc(cx, body_y + 42, 10, SKY)
    cv.polygon([(cx - half, body_y + 72), (cx - half - 26, body_y + 128),
                (cx - half, body_y + 112)], RED)
    cv.polygon([(cx + half, body_y + 72), (cx + half + 26, body_y + 128),
                (cx + half, body_y + 112)], RED)
    flame_y = body_y + body_h
    cv.polygon([(cx - 15, flame_y), (cx + 15, flame_y), (cx, flame_y + 52)], FLAME)
    cv.polygon([(cx - 8, flame_y), (cx + 8, flame_y), (cx, flame_y + 30)], EMBER)
    for sx, sy, sr in [(cx - 44, flame_y + 44, 9), (cx + 40, flame_y + 52, 11),
                       (cx - 8, flame_y + 62, 8), (cx + 18, flame_y + 66, 7)]:
        cv.disc(sx, sy, sr, SMOKE)
    cv.rect(x, y, w, 2, (52, 84, 130))
    cv.rect(x, y + h - 2, w, 2, (52, 84, 130))
    # Solid caption bar so the white text never fights the Earth below it.
    cv.rect(x, y + h - 40, w, 38, NAVY)
    cv.text(x + 14, y + h - 30, 'SHENZHOU-24 LIFTS OFF', 2, WHITE)
    cv.text(x + 14, y + h - 12, 'FROM JIUQUAN - 00:18 UTC', 2, (196, 210, 228))


def draw_masthead(cv):
    cv.text(W // 2, 22, 'THE WORLD TODAY', 10, INK, align='center')
    cv.hline(MX, 100, CW, RED, 3)
    cv.hline(MX, 106, CW, INK, 1)
    cv.text(MX, 116, 'WEDNESDAY 25 NOVEMBER 2026', 3, RED)
    cv.text(W - MX, 116, 'ONE DAY - ONE PAGE', 3, GREY, align='right')
    cv.hline(MX, 142, CW, INK, 2)


def draw_lead(cv, y):
    """Lead story, left; rocket art, right. Returns the y below the block."""
    lx, lw = MX, 560
    rx, rw = MX + 588, 380
    cv.text(lx, y, 'SPACE - CHINA  |  LEAD STORY', 2, RED)
    hy = y + 26
    cv.text(lx, hy, 'PAKISTAN', 6, INK)
    cv.text(lx, hy + 48, 'REACHES ORBIT', 6, INK)
    sy = hy + 102
    sub = ('First Pakistani in orbit boards China\u2019s Tiangong station.')
    sy = cv.para(lx, sy, sub, 3, INK, lw, leading=6)
    body = ('Muhammad Zeeshan Ali, 40, a Pakistan Air Force pilot, rode a '
            'Long March-2F rocket from Jiuquan at 00:18 UTC with Tang '
            'Hongbo and Wu Yi. He will spend a week aboard Tiangong '
            'running biotech tests.')
    by = sy + 12
    cv.para(lx, by, body, 2, INK, lw, leading=5)
    draw_rocket_panel(cv, rx, y, rw, 294)
    return y + 294


def draw_card(cv, x, y, w, h, kicker, headline_lines, body, accent):
    cv.rect(x, y, w, 6, accent)
    cv.rect(x, y + 6, w, h - 6, (252, 249, 240))
    cv.hline(x, y + h - 1, w, FAINT, 1)
    cv.text(x + 14, y + 18, kicker, 2, RED)
    hy = y + 44
    for line in headline_lines:
        cv.text(x + 14, hy, line, 3, INK)
        hy += 25
    cv.para(x + 14, hy + 4, body, 2, (44, 42, 38), w - 28, leading=5)


def draw_cards(cv, y):
    """Two rows of three stories. Returns the y below the grid."""
    cw, gap, ch = 316, 10, 184
    row1 = [
        ('UNITED STATES - CYBER', ['U.S. SPY', 'AGENCIES HIT', 'BY HACKERS'],
         'The CIA and the spy chief\u2019s office were hit by hackers.',
         RED),
        ('MARKETS - TARIFFS', ['MARKETS SLIDE', 'AS TARIFFS LOOM'],
         'Asian shares slid on tariff threats. Seoul -5.3%, Taiwan -5.1%, '
         'Nikkei -2.9%.',
         (29, 78, 137)),
        ('MIDDLE EAST - RIYADH', ['DRONE HITS', 'RIYADH TOWER'],
         'A Houthi drone hit the capital\u2019s tallest tower, wounding 11, '
         'Saudi civil defence said.',
         RED),
    ]
    row2 = [
        ('EUROPE - UKRAINE', ['KYIV: WE HIT', 'A RUSSIAN SHIP'],
         'Zelenskiy confirmed Ukraine hit a Russian cargo ship in the Gulf '
         'of Finland.',
         (29, 78, 137)),
        ('AMERICAS - COLOMBIA', ['30 HELD HOSTAGE', 'IN CARTAGENA'],
         'Gunmen seized a supermarket after a failed cash-truck robbery. '
         'Five women freed.',
         RED),
        ('TECH - COURTS', ['HUAWEI FOUND', 'GUILTY'],
         'A New York jury convicted Huawei on 10 of 12 counts, including '
         'trade-secret theft.',
         (29, 78, 137)),
    ]
    for row in (row1, row2):
        for k, (kicker, head, body, accent) in enumerate(row):
            draw_card(cv, MX + k * (cw + gap), y, cw, ch,
                      kicker, head, body, accent)
        y += ch + gap
    return y - gap


def draw_also_today(cv, y):
    cv.hline(MX, y, CW, INK, 2)
    cv.text(MX, y + 12, 'ALSO TODAY', 3, RED)
    line1 = ('WHO evacuates Ebola staff in DR Congo  \u00b7  NATO vows to defend '
             'space')
    line2 = ('Seoul minister quits in exam scandal  \u00b7  Sarkozy case sent '
             'to trial')
    line3 = ('O\u2019Hare radar outage delays flights  \u00b7  Trump pardons two '
             'Thanksgiving turkeys')
    cv.text(MX, y + 40, line1, 2, INK)
    cv.text(MX, y + 62, line2, 2, INK)
    cv.text(MX, y + 84, line3, 2, INK)
    return y + 106


def draw_footer(cv, y):
    cv.hline(MX, y, CW, FAINT, 1)
    cv.text(MX, y + 10,
            'Sources: Reuters - AP - CNN - Xinhua - WHO - UN', 2, GREY)
    cv.text(W - MX, y + 10, 'THE WORLD TODAY', 2, GREY, align='right')


def build_page():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    y = draw_lead(cv, 158)
    cv.hline(MX, y + 12, CW, INK, 2)
    cv.text(MX, y + 24, 'AROUND THE WORLD', 3, INK)
    y = draw_cards(cv, y + 52)
    y = draw_also_today(cv, y + 4)
    draw_footer(cv, y + 6)
    return encode_png(W, H, cv.px)


def main():
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(out_dir, exist_ok=True)
    data = build_page()
    with open(os.path.join(out_dir, 'entry.png'), 'wb') as fh:
        fh.write(data)


if __name__ == '__main__':
    main()
