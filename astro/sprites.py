import math


ORANGE = "#F26B1D"
ORANGE_DK = "#C4520F"
NAVY = "#22344F"
OUTLINE = "#141F31"
CREAM = "#F4EFE8"
KEY = "#010203"  # becomes see-through / click-through
COL = {"O": ORANGE, "D": ORANGE_DK, "V": NAVY, "W": CREAM, "S": CREAM, "N": OUTLINE}

# ───────────────────────── sprite data (12 px wide, no outline - added automatically) ───
HEAD = [
    "..OOOOOOOO..",
    ".OWOOOOOOOD.",
    ".OVVVVVVVVD.",
    ".OVVVVVVVVD.",
    ".OVVVVVVVVD.",
    ".OVVVVVVVVD.",
    ".OOOOOOOOOD.",
    "..DDDDDDDD..",
]
TORSO = [  # starts at y = 8
    ".OOOOOOOOOD.",
    "OODOOOOOODOO",
    "OODOVVVVODOO",
    "WWDOVOWVODWW",
    "..OOOOOOOD..",
    "..OOOOOOOD..",
]
LEGS = {  # starts at y = 14
    "stand": ["..OOO..OOD..", "..OOO..OOD..", ".WWWW..WWWW."],
    "walkA": ["..OOO...OOD.", "..OOO...OOD.", ".WWWW...WWWW"],
    "walkB": ["..OOO..OOD..", "..OOO..WWWW.", ".WWWW......."],
    "walkC": ["..OOO..OOD..", ".WWWW..OOD..", ".......WWWW."],
    "sit": ["..OOOOOOOD..", ".OOOOOOOOOD.", ".WWWWWWWWWW."],  # lowered body, feet out front
    "tuck": ["..OOOOOOOD..", ".WWWWWWWWWW."],
    "dangleA": [".OOO....OOD.", ".OOO....OOD.", "WWWW....WWWW"],
    "dangleB": ["...OOOOOD...", "...OOOOOD...", "..WWWWWWW..."],
}

def _mirror(parts):
    return [(11 - x, y, c) for x, y, c in parts]

_UP_R = (
    [(12, 4, "W"), (13, 4, "W"), (12, 5, "W"), (13, 5, "W")]
    + [(12, y, "O") for y in (6, 7, 8)]
    + [(13, y, "D") for y in (6, 7, 8)]
    + [(x, 9, "O") for x in (10, 11, 12, 13)]
)
_WAVE_B = (
    [(13, 4, "W"), (14, 4, "W"), (13, 5, "W"), (14, 5, "W")]
    + [(12, y, "O") for y in (6, 7, 8)]
    + [(13, y, "D") for y in (6, 7, 8)]
    + [(x, 9, "O") for x in (10, 11, 12, 13)]
)
ARMS = {"waveA": _UP_R, "waveB": _WAVE_B, "up": _UP_R + _mirror(_UP_R)}

EYES = {
    "open": [(3, 3), (3, 4), (8, 3), (8, 4)],
    "blink": [(3, 4), (8, 4)],
    "wide": [(3, 3), (3, 4), (3, 5), (8, 3), (8, 4), (8, 5)],
    "happy": [(2, 4), (3, 3), (4, 4), (7, 4), (8, 3), (9, 4)],
    "sleep": [(2, 4), (3, 4), (4, 4), (7, 4), (8, 4), (9, 4)],
    "x": [(2, 3), (4, 3), (3, 4), (2, 5), (4, 5), (7, 3), (9, 3), (8, 4), (7, 5), (9, 5)],
}
LOOKABLE = ("open", "blink", "wide")

HP_BAND = ([(0, 1), (0, 0), (1, 0), (1, -1)] + [(x, -1) for x in range(2, 10)]
           + [(10, -1), (10, 0), (11, 0), (11, 1)])
HP_CUPS = [(x, y) for y in range(2, 6) for x in (-1, 0, 11, 12)]
HP_GLINT = [(-1, 3), (12, 3)]

HEART = [".O.O.", "OOOOO", ".OOO.", "..O.."]
ZEE = ["SSS", "..S", ".S.", "SSS"]
STAR = [".S.", "SSS", ".S."]
BANG = ["SS", "SS", "SS", "..", "SS"]

CW, CH = 20, 30  # canvas size in sprite-pixels
OX = 4  # sprite x-offset inside canvas
SPIN = (1.0, 0.6, 0.2, -0.6, -1.0, -0.6, 0.2, 0.6)


def build(legs, arms, eyes, look, bob, k, fx, fxp, hp=False):
    """Return {(x, y): colour-letter} for one frame, outline included."""
    px = {}
    for y, row in enumerate(TORSO[:4] if legs == "sit" else TORSO, 8):
        for x, c in enumerate(row):
            if c != ".":
                px[(x, y)] = c
    for y, row in enumerate(LEGS[legs], 12 if legs == "sit" else 14):
        for x, c in enumerate(row):
            if c != ".":
                px[(x, y)] = c
    if arms != "down":
        for key in [p for p in px if 9 <= p[1] <= 11 and (p[0] <= 1 or p[0] >= 10)]:
            del px[key]
        for x, y, c in ARMS[arms]:
            px[(x, y)] = c
    for y, row in enumerate(HEAD):
        for x, c in enumerate(row):
            if c != ".":
                px[(x, y + bob)] = c
    shift = look if eyes in LOOKABLE else 0
    for x, y in EYES[eyes]:
        px[(min(9, max(2, x + shift)), y + bob)] = "W"
    if eyes != "x":  # visor shine; hops to the far side when he looks left so it never touches an eye
        px[(9 if look < 0 and eyes in LOOKABLE else 2, 2 + bob)] = "W"
    if hp:  # navy headphones
        for x, y in HP_BAND + HP_CUPS:
            px[(x, y + bob)] = "V"
        for x, y in HP_GLINT:
            px[(x, y + bob)] = "W"

    dy = CH - 2 - max(y for _, y in px)  # feet always on the bottom row
    body = {}
    for (x, y), c in px.items():
        nx = math.floor(5.5 + (x - 5.5) * k + 0.5) + OX
        body[(nx, y + dy)] = c
    ytop = min(y for _, y in body)

    fxpx = {}

    def blit(rows, x, y):
        for j, r in enumerate(rows):
            for i, c in enumerate(r):
                if c != "." and 0 <= x + i < CW and 0 <= y + j < CH:
                    fxpx[(x + i, y + j)] = c

    if fx == "hearts":
        for i, hx in enumerate((OX + 7, OX - 2, OX + 3)):
            if fxp >= 2 * i and (fxp - 2 * i) % 10 < 8:
                blit(HEART, hx, ytop - 5 - (fxp - 2 * i) % 10)
    elif fx == "zzz":
        for i in range(3):
            age = (fxp - 4 * i) % 12
            if age < 9:
                blit(ZEE, OX + 8 + age // 3, ytop - 4 - age)
    elif fx == "stars":
        for i in range(3):
            a = 2 * math.pi * i / 3 + fxp * (2 * math.pi / 12)
            cx = OX + 5 + round(6 * math.cos(a))
            cy = ytop - 4 + round(2 * math.sin(a))
            blit(STAR, cx - 1, cy - 1)
    elif fx == "bang":
        blit(BANG, OX + 9, ytop - 7)

    allpx = dict(body)
    allpx.update(fxpx)
    edge = set()
    for (x, y) in allpx:
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in allpx and 0 <= nx < CW and 0 <= ny < CH:
                edge.add((nx, ny))
    for p in edge:
        allpx[p] = "N"
    return allpx
