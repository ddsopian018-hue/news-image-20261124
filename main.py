#!/usr/bin/env python3
"""The World Today - one-image front page for Tuesday 24 November 2026.

A pure-standard-library Python program that draws a complete newspaper
front page (1024 x 1024 PNG) summing up the world's news of Tuesday
24 November 2026, and writes it to $MAKEFUN_OUTPUT_DIR/entry.png
(falling back to /output/entry.png).

The lead story is Nvidia's board reinstating co-founder Jensen Huang as
CEO eleven days after he resigned - shares leapt 31% and added about
$950bn in value.  Secondary stories cover the COP31 climate talks in
Antalya collapsing without a deal, Russian drones hitting the Kyiv
region, and a Russian missile corvette destroyed at Benghazi port.
Eighteen further briefs from every region and beat fill the grid.

Everything is drawn by hand in this file: a 5x7 bitmap font, simple
vector pictograms, and a hand-rolled PNG encoder (zlib + struct).
No network, no third-party code, fully deterministic.
"""

import binascii
import math
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
PAPER_BOX = (255, 253, 244)
INK = (20, 22, 26)
FAINT = (110, 104, 90)
RULE = (60, 56, 48)
RED = (179, 32, 42)
NAVY = (22, 50, 79)
NAVY_DARK = (13, 30, 48)
GREEN = (24, 122, 56)
GREEN_LT = (64, 190, 96)
GOLD = (201, 146, 14)
SKY = (120, 170, 220)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 pixels, written as strings of '1' and '0'.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "10001", "11001", "10101", "10011", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "01010", "00100", "00100", "00100", "01010", "10001"),
    "Y": ("10001", "01010", "00100", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
}

_SANITIZE = {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "·": "-", "…": ".",
}


def clean(text):
    out = []
    for ch in text.upper():
        ch = _SANITIZE.get(ch, ch)
        out.append(ch if ch in FONT else " ")
    return "".join(out)


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg) * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        row = bytes(color) * max(0, x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def frame(self, x, y, w, h, color, t=2):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.rect(x0 - t // 2, y0 - t // 2, t, t, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, t=1):
        steps = max(24, r * 4)
        for i in range(steps + 1):
            a = 2 * math.pi * i / steps
            self.rect(int(cx + r * math.cos(a)) - t // 2,
                      int(cy + r * math.sin(a)) - t // 2, t, t, color)

    def fill_circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            span = int(math.sqrt(max(0, r * r - (yy - cy) ** 2)))
            self.rect(cx - span, yy, 2 * span + 1, 1, color)

    def fill_poly(self, pts, color):
        ys = [p[1] for p in pts]
        for yy in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    xs.append(x0 + (yy - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), yy, int(xs[i + 1]) - int(xs[i]) + 1, 1,
                          color)

    # ------------------------------------------------------------ text
    def text_width(self, s, scale):
        return len(clean(s)) * 6 * scale - scale

    def text(self, x, y, s, scale, color, bold=False):
        s = clean(s)
        cx = x
        for ch in s:
            glyph = FONT[ch]
            passes = (0, max(1, scale // 2)) if bold else (0,)
            for off in passes:
                for gy, row in enumerate(glyph):
                    for gx, bit in enumerate(row):
                        if bit == "1":
                            self.rect(cx + off + gx * scale, y + gy * scale,
                                      scale, scale, color)
            cx += 6 * scale
        return cx - scale - x

    def text_centered(self, cx, y, s, scale, color, bold=False):
        w = self.text_width(s, scale)
        return self.text(cx - w // 2, y, s, scale, color, bold)

    def wrap(self, s, scale, max_px):
        """Wrap a string into lines that fit max_px at the given scale."""
        max_chars = max(1, (max_px + scale) // (6 * scale))
        words = clean(s).split()
        lines = []
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def paragraph(self, x, y, s, scale, color, max_px, leading=3,
                  bold=False):
        for line in self.wrap(s, scale, max_px):
            self.text(x, y, line, scale, color, bold)
            y += 7 * scale + leading
        return y


# ---------------------------------------------------------------- icons
# Each icon draws inside the box (x, y, s, s) in the given colour.

def icon_globe(c, x, y, s, col):
    cx, cy, r = x + s // 2, y + s // 2, s // 2 - 2
    c.circle(cx, cy, r, col, 2)
    c.line(cx - r, cy, cx + r, cy, col, 2)
    c.circle(cx, cy, r // 2, col, 1)
    c.line(cx, cy - r, cx, cy + r, col, 1)


def icon_drone(c, x, y, s, col):
    b = s // 4
    cx, cy = x + s // 2, y + s // 2
    c.frame(cx - b // 2, cy - b // 2, b, b, col, 2)
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        ex, ey = cx + dx * (s // 2 - 4), cy + dy * (s // 2 - 4)
        c.line(cx, cy, ex, ey, col, 2)
        c.circle(ex, ey, 4, col, 2)


def icon_flame(c, x, y, s, col):
    cx = x + s // 2
    pts = [(cx, y + 2), (cx + s // 3, y + s // 2), (cx + s // 4, y + s - 4),
           (cx - s // 4, y + s - 4), (cx - s // 3, y + s // 2)]
    c.fill_poly(pts, col)
    inner = [(cx, y + s // 2), (cx + s // 6, y + 3 * s // 4),
             (cx, y + s - 5), (cx - s // 6, y + 3 * s // 4)]
    c.fill_poly(inner, PAPER_BOX)


def icon_scales(c, x, y, s, col):
    cx = x + s // 2
    c.line(cx, y + 3, cx, y + s - 4, col, 2)
    c.line(x + 3, y + 6, x + s - 3, y + 6, col, 2)
    for side in (-1, 1):
        px = cx + side * (s // 2 - 5)
        c.line(px, y + 6, px - 5, y + s // 2, col, 1)
        c.line(px, y + 6, px + 5, y + s // 2, col, 1)
        c.line(px - 7, y + s // 2, px + 7, y + s // 2, col, 2)
    c.rect(cx - s // 4, y + s - 4, s // 2, 3, col)


def icon_note(c, x, y, s, col):
    c.rect(x + 2 * s // 3, y + 2, 3, 2 * s // 3, col)
    c.line(x + 2 * s // 3, y + 2, x + s - 2, y + s // 4, col, 3)
    c.fill_circle(x + s // 3, y + 3 * s // 4, s // 6, col)


def icon_factory(c, x, y, s, col):
    c.rect(x + 2, y + s // 2, s - 4, s // 2 - 2, col)
    c.rect(x + 4, y + s // 5, s // 5, s // 3, col)
    c.fill_circle(x + 4 + s // 10, y + s // 8, 3, col)
    c.fill_circle(x + 9 + s // 10, y + s // 10, 4, col)
    for i in range(3):
        c.rect(x + 6 + i * s // 4, y + 2 * s // 3, 4, 4, PAPER_BOX)


def icon_warn(c, x, y, s, col):
    cx = x + s // 2
    c.fill_poly([(cx, y + 2), (x + s - 2, y + s - 3), (x + 2, y + s - 3)], col)
    c.text(cx - 3, y + s // 2, "!", 1, PAPER_BOX, bold=True)


def icon_doc(c, x, y, s, col):
    c.frame(x + s // 5, y + 2, 3 * s // 5, s - 4, col, 2)
    for i in range(3):
        c.line(x + s // 5 + 5, y + 9 + i * 6, x + 4 * s // 5 - 5,
               y + 9 + i * 6, col, 1)


def icon_chat(c, x, y, s, col):
    c.frame(x + 2, y + 3, s - 4, s // 2 + 4, col, 2)
    c.fill_poly([(x + s // 4, y + s // 2 + 7), (x + s // 2, y + s // 2 + 7),
                 (x + s // 4, y + s - 3)], col)
    for i in range(3):
        c.fill_circle(x + 8 + i * (s // 4), y + s // 4 + 3, 2, col)


def icon_chip(c, x, y, s, col):
    m = s // 5
    c.frame(x + m, y + m, s - 2 * m, s - 2 * m, col, 2)
    c.frame(x + s // 3, y + s // 3, s // 3, s // 3, col, 2)
    for i in range(3):
        p = y + m + 4 + i * (s - 2 * m - 8) // 2
        c.line(x + 2, p, x + m, p, col, 2)
        c.line(x + s - m, p, x + s - 2, p, col, 2)
        q = x + m + 4 + i * (s - 2 * m - 8) // 2
        c.line(q, y + 2, q, y + m, col, 2)
        c.line(q, y + s - m, q, y + s - 2, col, 2)


def icon_book(c, x, y, s, col):
    cx = x + s // 2
    c.line(cx, y + 4, cx, y + s - 4, col, 2)
    c.frame(x + 3, y + 4, s // 2 - 3, s - 8, col, 2)
    c.frame(cx, y + 4, s // 2 - 3, s - 8, col, 2)
    for i in range(2):
        c.line(x + 7, y + 11 + i * 7, cx - 4, y + 11 + i * 7, col, 1)
        c.line(cx + 4, y + 11 + i * 7, x + s - 7, y + 11 + i * 7, col, 1)


def icon_shield(c, x, y, s, col):
    cx = x + s // 2
    pts = [(x + 3, y + 3), (x + s - 3, y + 3), (x + s - 3, y + s // 2),
           (cx, y + s - 2), (x + 3, y + s // 2)]
    c.fill_poly(pts, col)
    star = []
    for i in range(10):
        r = (s // 5) if i % 2 == 0 else (s // 10)
        a = -math.pi / 2 + i * math.pi / 5
        star.append((int(cx + r * math.cos(a)),
                     int(y + s // 3 + r * math.sin(a))))
    c.fill_poly(star, PAPER_BOX)


def icon_bank(c, x, y, s, col):
    cx = x + s // 2
    c.fill_poly([(cx, y + 2), (x + s - 2, y + s // 4), (x + 2, y + s // 4)],
                col)
    for i in range(4):
        px = x + 5 + i * (s - 10) // 3
        c.rect(px - 1, y + s // 4 + 3, 3, s // 2, col)
    c.rect(x + 2, y + 3 * s // 4 + 2, s - 4, 3, col)


def icon_train(c, x, y, s, col):
    c.rect(x + 3, y + 4, s - 6, s // 2, col)
    c.rect(x + 6, y + 8, s // 4, 6, PAPER_BOX)
    c.rect(x + s // 2 + 2, y + 8, s // 4, 6, PAPER_BOX)
    c.fill_circle(x + s // 4, y + 3 * s // 4, 4, col)
    c.fill_circle(x + 3 * s // 4, y + 3 * s // 4, 4, col)
    c.line(x + 2, y + s - 3, x + s - 2, y + s - 3, col, 2)


def icon_bat(c, x, y, s, col):
    c.line(x + s // 4, y + s - 4, x + 3 * s // 4, y + 4, col, 5)
    c.fill_circle(x + 3 * s // 4 + 3, y + s - 7, s // 7, col)
    c.circle(x + 3 * s // 4 + 3, y + s - 7, s // 7, col, 1)


def icon_flag(c, x, y, s, col):
    c.rect(x + 4, y + 2, 3, s - 4, col)
    c.fill_poly([(x + 7, y + 3), (x + s - 2, y + 8), (x + 7, y + s // 2)],
                col)


def icon_crowd(c, x, y, s, col):
    for i, dx in enumerate((s // 5, s // 2, 4 * s // 5)):
        cy = y + s // 3 + (4 if i == 1 else 0)
        c.fill_circle(x + dx, cy, s // 8, col)
        c.fill_poly([(x + dx - s // 7, y + s - 2), (x + dx + s // 7,
                      y + s - 2), (x + dx, y + s // 2)], col)


ICONS = {
    "globe": icon_globe, "drone": icon_drone, "flame": icon_flame,
    "scales": icon_scales, "note": icon_note, "factory": icon_factory,
    "warn": icon_warn, "doc": icon_doc, "chat": icon_chat,
    "chip": icon_chip, "book": icon_book, "shield": icon_shield,
    "bank": icon_bank, "train": icon_train, "bat": icon_bat,
    "flag": icon_flag, "crowd": icon_crowd,
}

# ---------------------------------------------------------------- content
SECONDARY = [
    ("CLIMATE", "globe", RED,
     "CLIMATE TALKS COLLAPSE WITHOUT A DEAL",
     "The UN summit in Antalya ends as the EU and others reject the "
     "final text from COP31 presidents Turkiye and Australia. The "
     "fossil-fuel fight stays unresolved."),
    ("UKRAINE WAR", "drone", NAVY,
     "RUSSIAN DRONES HIT THE KYIV REGION",
     "President Zelenskyy says several people are missing after a "
     "Russian drone strike in the Kyiv region. A Russian cargo ship "
     "burns off Finland."),
    ("LIBYA", "flame", GOLD,
     "RUSSIAN CORVETTE DESTROYED AT BENGHAZI",
     "An explosion and fire destroy a Russian Navy missile corvette "
     "at Benghazi port in eastern Libya. Russian and Libyan nationals "
     "are among the dead."),
]

BRIEFS = [
    ("scales", "ROHINGYA: 14 BACK ICJ", "GENOCIDE RULING"),
    ("note", "AHMADI GETS 74 LASHES", "OVER HIJAB-FREE GIG"),
    ("factory", "BANTEN FACTORY FIRE:", "RESCUE ON, MANY MISSING"),
    ("drone", "DRONE HITS COLOMBIA", "POLICE BASE; BABY HURT"),
    ("flame", "FIRE GUTS ZANZIBAR", "BEACHFRONT HOTELS"),
    ("crowd", "LISBON MARCHES OVER", "COST OF LIVING"),
    ("warn", "GAZA TOXIC FOR DECADES", "OXFAM WAR-WASTE REPORT"),
    ("doc", "TALIBAN ERASE WOMEN'S", "NAMES IN BALKH FILES"),
    ("chat", "KIM SNUBS TRUMP'S", "BIDS FOR TALKS - WSJ"),
    ("chip", "UN CHIEF: AI SAFETY", "PACT WITHIN A YEAR"),
    ("book", "SEOUL MINISTER QUITS", "OVER AI CHEATING RULES"),
    ("shield", "TRUMP HALTS ARMY PLAN", "TO DETONATE TOXICS"),
    ("bank", "US HITS IRAN SHADOW", "BANKING IN SANCTIONS"),
    ("shield", "NATO: PUTIN MAY STRIKE", "BEFORE EUROPE READY"),
    ("train", "MODI, SHAH LAUNCH", "AYODHYA-JANAKPUR TRAIN"),
    ("crowd", "12,000 FLEE CONCERT", "IN MANCHESTER GAS SCARE"),
    ("bat", "PANT 128 AT WELLINGTON", "RECORD FOR ASIAN KEEPER"),
    ("flag", "VERSTAPPEN WINS IN", "LAS VEGAS GRAND PRIX"),
]


# ---------------------------------------------------------------- drawing
def draw_lead_scene(c, x, y, w, h):
    """Navy panel: a steep green share chart and a glowing chip."""
    c.rect(x, y, w, h, NAVY_DARK)
    # faint grid
    for gy in range(y + 24, y + h - 30, 24):
        c.line(x + 10, gy, x + w - 10, gy, NAVY, 1)
    # chart polyline, flat then rocketing
    pts = [(x + 18, y + h - 46), (x + 90, y + h - 42),
           (x + 150, y + h - 58), (x + 205, y + h - 52),
           (x + 255, y + h - 96), (x + 305, y + h - 140),
           (x + w - 26, y + 34)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        c.line(ax, ay, bx, by, GREEN_LT, 4)
    hx, hy = pts[-1]
    c.line(hx, hy, hx - 16, hy + 2, GREEN_LT, 4)
    c.line(hx, hy, hx - 4, hy + 15, GREEN_LT, 4)
    c.fill_circle(pts[3][0], pts[3][1], 5, RED)
    # chip, lower left of the panel
    icon_chip(c, x + 24, y + 26, 74, SKY)
    c.text(x + 112, y + 40, "NVIDIA", 3, WHITE, bold=True)
    c.text(x + 112, y + 66, "AI CHIP GIANT", 2, SKY)
    # the big number
    c.text(x + 20, y + h - 34, "+31%", 4, GREEN_LT, bold=True)
    c.text(x + 150, y + h - 26, "ONE DAY", 2, WHITE)


def draw_front_page():
    c = Canvas(W, H, PAPER)
    mx = 18                      # left/right margin
    cw = W - 2 * mx              # content width

    # ---------------- masthead ----------------
    c.rect(mx, 12, cw, 3, INK)
    c.text_centered(W // 2, 22, "THE WORLD TODAY", 7, INK, bold=True)
    c.rect(mx, 82, cw, 2, INK)
    c.rect(mx, 88, cw, 34, NAVY)
    c.text_centered(W // 2, 95, "TUESDAY 24 NOVEMBER 2026", 3, WHITE,
                    bold=True)
    c.text(mx + 8, 98, "VOL. I", 2, SKY)
    c.text(mx + cw - 8 - c.text_width("ONE IMAGE", 2), 98, "ONE IMAGE", 2,
           SKY)
    c.rect(mx, 126, cw, 3, INK)

    # ---------------- lead story ----------------
    ly = 140
    c.text(mx, ly, "BUSINESS - MARKETS - THE DAY'S BIGGEST STORY", 2, RED,
           bold=True)
    c.text(mx, ly + 22, "HUANG IS BACK", 6, INK, bold=True)
    c.text(mx, ly + 76, "NVIDIA SOARS 31%", 6, INK, bold=True)
    draw_lead_scene(c, 648, ly + 20, 358, 196)
    c.paragraph(mx, ly + 134,
                "Nvidia's board reinstates co-founder Jensen Huang as "
                "CEO, 11 days after he quit. Trump says he pressed for "
                "the return. Shares leap 31% and add about $950bn in "
                "value; Huang's fortune jumps nearly $34bn in a day.",
                2, INK, 600)
    # stat strip
    sy = ly + 228
    stats = [("NVDA", "+31%"), ("NASDAQ", "+6.5%"),
             ("S&P 500", "+4.7%"), ("DOW", "+1,450 PTS")]
    sw = (cw - 3 * 10) // 4
    for i, (name, val) in enumerate(stats):
        bx = mx + i * (sw + 10)
        c.rect(bx, sy, sw, 40, PAPER_BOX)
        c.frame(bx, sy, sw, 40, RULE, 1)
        c.text(bx + 10, sy + 7, name, 2, FAINT, bold=True)
        tw = c.text_width(val, 2)
        c.text(bx + sw - 10 - tw, sy + 7, val, 2, GREEN, bold=True)
    c.rect(mx, sy + 52, cw, 2, INK)

    # ---------------- secondary stories ----------------
    by = sy + 62
    bw = (cw - 2 * 12) // 3
    bh = 218
    for i, (section, icon, accent, head, body) in enumerate(SECONDARY):
        bx = mx + i * (bw + 12)
        c.rect(bx, by, bw, bh, PAPER_BOX)
        c.frame(bx, by, bw, bh, RULE, 1)
        c.rect(bx, by, bw, 4, accent)
        ICONS[icon](c, bx + 10, by + 12, 30, accent)
        c.text(bx + 48, by + 16, section, 2, accent, bold=True)
        c.paragraph(bx + 12, by + 50, head, 2, INK, bw - 24, bold=True)
        c.paragraph(bx + 12, by + 90, body, 2, INK, bw - 24)
    c.rect(mx, by + bh + 10, cw, 2, INK)

    # ---------------- briefs ----------------
    gy = by + bh + 24
    c.text(mx, gy, "AROUND THE WORLD IN BRIEF", 2, NAVY, bold=True)
    c.text(mx + cw - c.text_width("18 MORE STORIES OF THE DAY", 2), gy,
           "18 MORE STORIES OF THE DAY", 2, FAINT)
    gy += 24
    cell_w = (cw - 2 * 12) // 3
    cell_h = 48
    for idx, (icon, line1, line2) in enumerate(BRIEFS):
        col = idx % 3
        row = idx // 3
        bx = mx + col * (cell_w + 12)
        yy = gy + row * (cell_h + 2)
        if idx % 2 == 0:
            c.rect(bx, yy, cell_w, cell_h, PAPER_BOX)
        ICONS[icon](c, bx + 6, yy + 7, 34, NAVY if idx % 3 else RED)
        c.text(bx + 48, yy + 6, line1, 2, INK, bold=True)
        c.text(bx + 48, yy + 25, line2, 2, FAINT)

    # ---------------- footer ----------------
    fy = gy + 6 * (cell_h + 2) + 6
    c.rect(mx, fy, cw, 2, INK)
    c.text_centered(W // 2, fy + 8,
                    "DRAWN BY CODE - EVERY STORY REPORTED ON 24 NOV 2026",
                    2, FAINT)
    return c


# ---------------------------------------------------------------- PNG out
def encode_png(canvas):
    raw = bytearray()
    row_bytes = canvas.w * 3
    for yy in range(canvas.h):
        raw.append(0)
        start = yy * row_bytes
        raw += canvas.px[start:start + row_bytes]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    canvas = draw_front_page()
    png = encode_png(canvas)
    assert len(png) <= 1048576, "entry.png exceeds 1 MiB"
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(png)
    print("wrote %s (%d bytes)" % (path, len(png)))


if __name__ == "__main__":
    main()
