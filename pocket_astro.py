"""
POCKET_ASTRO - a tiny pixel-art orange astronaut that lives on your Windows 11 taskbar.

Run:        python pocket_astro.py          (or  pythonw pocket_astro.py  for no console window)
Needs:      Python 3.8+ for Windows (tkinter is included). No pip installs.

What he does
  * Stands on top of the taskbar, always on top of other windows
  * Hides automatically while a fullscreen app / game / video is in front
  * Wanders, sits, waves, blinks, looks at your mouse, falls asleep (Zzz)
  * Click         -> happy hops + hearts
  * Click x3      -> big spin jump
  * Click x6      -> dizzy (stars!)
  * Drag him     -> he dangles and panics; let go and he drops (throw him!)
  * Right-click   -> menu (wave, spin, nap, wander on/off, quit)

Autostart: press Win+R, type  shell:startup , and drop a shortcut to
           pythonw.exe pocket_astro.py in that folder.
"""
import asyncio
import ctypes
import math
import random
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
from ctypes import wintypes

# ───────────────────────── things he says (edit freely!) ─────────────────────────
USER_NAME = ""              # put your name here, e.g. "Manan", to be greeted by name
GREETING_DELAY_S = 10       # greets you this many seconds after he starts
<<<<<<< HEAD
CHAT_EVERY_MIN = (6, 14)    # random small-talk every 6-14 minutes
=======
CHAT_EVERY_MIN = (5, 13)    # random small-talk every 6-14 minutes
SLEEP_AFTER_IDLE_S = 180    # he only dozes off after this long with no keyboard/mouse use at all
>>>>>>> experimental
NOW_PLAYING = True          # announce songs/videos playing in any app or browser tab
NOW_PLAYING_SHOW_ARTIST = False   # True -> "Title - Artist" (YouTube shows the channel name)
REMINDERS = [               # ("HH:MM" 24h clock, message) - each fires once a day
    ("10:30", "Water time! Sip sip."),
    ("14:00", "Lunch break? Fuel up, astronaut."),
    ("16:00", "Stretch your back for a minute."),
    ("18:00", "It's 6 PM... coffee time?"),
    ("23:30", "Getting late. Maybe wrap up soon?"),
]
# CHAT = [
#     "Don't forget to drink water!",
#     "Look away from the screen for 20 seconds.",
#     "Ctrl+S, friend. Ctrl+S.",
#     "Houston, we have no bugs. Yet.",
#     "Take a deep breath. You've got this.",
#     "Beep boop. Just checking in.",
#     "Stand up and stretch a little?",
#     "Great job today!",
# ] <- ORIGINAL CHAT

CHAT = [
    # ☀️ Wholesome & Friendly
    "Don't forget to drink water!",
    "Look away from the screen for 20 seconds.",
    "Take a deep breath. You've got this.",
    "Hey, you're doing better than you think.",
    "One step at a time, astronaut.",
    "I'm glad we're on this mission together.",
    "You deserve a little break.",
    "Don't be too hard on yourself today.",
    "Progress is progress, no matter how small.",
    "Remember to unclench your jaw.",
    "Your future self will thank you.",
    "It's okay to take things slowly.",
    "Proud of you, space ranger!",
    "A little rest is part of the mission.",

    # 🚀 Space-themed
    "Houston, we have no bugs. Yet.",
    "Ground control to Major Human.",
    "All systems nominal. Probably.",
    "Space is vast. Your potential is vaster.",
    "Another day, another orbit around the Sun.",
    "Keep reaching for the stars!",
    "Warning: Excessive brilliance detected.",
    "Gravity is optional. Sleep is not.",
    "Mission control says you're doing great.",
    "Somewhere out there, a star is being born.",
    "I've seen the stars. Your code is scarier.",
    "Exploration protocol: Keep going.",
    "We are made of stardust, you know.",
    "Just a little guy in a big universe.",

    # 💻 Developer Humor
    "Ctrl+S, friend. Ctrl+S.",
    "It works on my machine. 🚀",
    "Have you tried turning it off and on again?",
    "Another bug? Must be a space anomaly.",
    "Remember: 99 little bugs in the code...",
    "Commit early. Commit often.",
    "That's not a bug. It's an undocumented feature.",
    "Your code called. It misses you.",
    "Coffee.exe has stopped working.",
    "Please don't push directly to production.",
    "Stack Overflow is our mission control.",
    "One does not simply write bug-free code.",
    "404: Motivation not found.",
    "The compiler fears you.",
    "Have you checked the console?",
    "Rubber duck debugging is scientifically valid.",

    # 😂 Silly & Random
    "Beep boop. Just checking in.",
    "I wonder if aliens have Wi-Fi.",
    "I saw you move that mouse. Suspicious.",
    "Do astronauts get space sickness?",
    "I could really go for a space sandwich.",
    "Just standing here. Menacingly.",
    "Do you think the Moon gets lonely?",
    "I'm small, but my dreams are astronomical.",
    "I have absolutely no idea what I'm doing.",
    "Blink twice if you need a coffee.",
    "Can we go to Mars after work?",
    "My helmet smells like yesterday.",
    "I was promised a spaceship.",
    "I wonder what's happening in Andromeda.",

    # 🌱 Productivity & Motivation
    "What's the next small thing on your list?",
    "Don't chase perfect. Chase progress.",
    "Focus mode: ENGAGED.",
    "A little consistency goes a long way.",
    "You've got this. I believe in you.",
    "Take a break before your brain files a complaint.",
    "Stand up and stretch a little?",
    "Great job today!",
    "Your dreams aren't going to build themselves.",
    "Keep showing up. That's the secret.",
    "Don't let perfect be the enemy of done.",
    "One task at a time. No need to rush.",
    "Even rockets need time to launch.",
]

# ───────────────────────── palette (from the Artemis-II sheet) ─────────────────────────
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
<<<<<<< HEAD
=======
    if eyes != "x":  # visor shine; hops to the far side when he looks left so it never touches an eye
        px[(9 if look < 0 and eyes in LOOKABLE else 2, 2 + bob)] = "W"
>>>>>>> experimental
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


# ───────────────────────── Windows helpers ─────────────────────────
class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", wintypes.RECT),
        ("rcWork", wintypes.RECT),
        ("dwFlags", wintypes.DWORD),
    ]


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]


def winapi():
    u = ctypes.windll.user32
    u.GetForegroundWindow.restype = wintypes.HWND
    u.GetParent.argtypes = [wintypes.HWND]
    u.GetParent.restype = wintypes.HWND
    u.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    u.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    u.MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD]
    u.MonitorFromWindow.restype = wintypes.HANDLE
    u.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MONITORINFO)]
    u.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
    u.GetWindowLongW.restype = ctypes.c_long
    u.IsWindowVisible.argtypes = [wintypes.HWND]
    u.IsIconic.argtypes = [wintypes.HWND]
    u.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    u.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
                               ctypes.c_int, ctypes.c_int, wintypes.UINT]
    return u


SHELL_CLASSES = {"Progman", "WorkerW", "Shell_TrayWnd", "Shell_SecondaryTrayWnd"}
AIR = {"fall", "happy", "spin"}
TICK_MS = 33


class NowPlaying:
    """Hears about song changes straight from Windows (the same media info the
    volume flyout and Wallpaper Engine use). It is event-driven: this thread
    sleeps until Windows says something changed - no polling, ~0% CPU.
    Optional: needs  pip install winrt-runtime winrt-Windows.Media.Control
                     winrt-Windows.Foundation winrt-Windows.Foundation.Collections
                     winrt-Windows.Storage.Streams
<<<<<<< HEAD
    Without it Pocket_Astro simply doesn't announce music."""
=======
    Without it Astro simply doesn't announce music."""
>>>>>>> experimental

    def __init__(self, callback):
        self.cb, self.last, self.sess, self.timer, self.loop = callback, None, None, None, None
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            try:
                from winrt.windows.media.control import (
                    GlobalSystemMediaTransportControlsSessionManager as Manager)
            except ImportError:
                from winsdk.windows.media.control import (
                    GlobalSystemMediaTransportControlsSessionManager as Manager)
        except ImportError:
            print("Astro: music announcements are off (pip install winrt-runtime "
                  "winrt-Windows.Media.Control winrt-Windows.Foundation "
                  "winrt-Windows.Foundation.Collections winrt-Windows.Storage.Streams)")
            return
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self._start(Manager))
            self.loop.run_forever()  # idle until Windows calls us
        except Exception as e:
<<<<<<< HEAD
            print("Pocket_Astro: music announcements unavailable:", e)
=======
            print("Astro: music announcements unavailable:", e)
>>>>>>> experimental

    async def _start(self, Manager):
        self.mgr = await Manager.request_async()
        self._on_session = lambda sender, args: self.loop.call_soon_threadsafe(self._rebind)
        self._on_change = lambda sender, args: self.loop.call_soon_threadsafe(self._schedule)
        self.mgr.add_current_session_changed(self._on_session)
        self._rebind(first=True)
        await self._read(announce=False)  # remember what's already playing, stay quiet

    def _rebind(self, first=False):
        if self.sess is not None:
            try:
                self.sess.remove_media_properties_changed(self.tok1)
                self.sess.remove_playback_info_changed(self.tok2)
            except Exception:
                pass
        try:
            self.sess = self.mgr.get_current_session()
        except Exception:
            self.sess = None
        if self.sess is not None:
            self.tok1 = self.sess.add_media_properties_changed(self._on_change)
            self.tok2 = self.sess.add_playback_info_changed(self._on_change)
        if not first:
            self._schedule()

    def _schedule(self):  # wait a moment: players fire several half-filled updates per song
        if self.timer:
            self.timer.cancel()
        self.timer = self.loop.call_later(
            1.0, lambda: asyncio.ensure_future(self._read(), loop=self.loop))

    async def _read(self, announce=True):
        s = self.sess
        if s is None:
            return
        try:
            if int(s.get_playback_info().playback_status) != 4:  # 4 = playing
                return
            info = await s.try_get_media_properties_async()
            title, artist = (info.title or "").strip(), (info.artist or "").strip()
        except Exception:
            return
        if not title or (title, artist) == self.last:
            return
        self.last = (title, artist)
        if announce:
            self.cb(title, artist)


class Bubble:
    """Pixel-style speech bubble in its own tiny see-through window."""

    def __init__(self, pet):
        self.pet, S = pet, pet.S
        self.m, self.n, self.o = max(1, S // 2), S, max(1, S // 2)
        w = self.win = tk.Toplevel(pet.root)
        w.withdraw()
        w.overrideredirect(True)
        w.configure(bg=KEY)
        w.attributes("-topmost", True)
        w.attributes("-transparentcolor", KEY)
        self.cv = tk.Canvas(w, bg=KEY, highlightthickness=0, bd=0)
        self.cv.pack()
        self.cv.bind("<Button-1>", lambda e: self.hide())  # click bubble to dismiss
        self.font = tkfont.Font(family="Consolas", size=-round(3.4 * S), weight="bold")
        self.visible, self.until, self.pos, self.rel = False, 0.0, None, None
        self.w = self.h = 0

    def show(self, text, secs):
        cv, m, n, o = self.cv, self.m, self.n, self.o
        cv.delete("all")
        pad = 2 * self.pet.S
        t = cv.create_text(m + pad, m + pad, text=text, anchor="nw", font=self.font,
                           fill=NAVY, width=round(46 * self.pet.S))
        x0, y0, x1, y1 = cv.bbox(t)
        self.w, body_h = x1 + pad + m, y1 + pad + m
        self.h = body_h + 2 * n
        self.L, self.T, self.R, self.B = m, m, self.w - m, body_h - m
        L, T, R, B = self.L, self.T, self.R, self.B
        pts = [L + n, T, R - n, T, R - n, T + n, R, T + n, R, B - n, R - n, B - n,
               R - n, B, L + n, B, L + n, B - n, L, B - n, L, T + n, L + n, T + n]
        cv.create_polygon(pts, fill=CREAM, outline=OUTLINE, width=o)
        cv.tag_raise(t)
        cv.config(width=self.w, height=self.h)
        self.rel = self.pos = None
        self.until = time.time() + secs
        self.visible = True
        self.place()
        self.win.deiconify()

    def tail(self, cx):
        cv, n, o, B = self.cv, self.n, self.o, self.B
        cx = int(min(max(cx, self.L + 2 * n + o), self.R - 2 * n - o))
        cv.delete("tail")
        cv.create_polygon(cx - 2 * n, B, cx + 2 * n, B, cx + 2 * n, B + n, cx + n, B + n,
                          cx + n, B + 2 * n, cx - n, B + 2 * n, cx - n, B + n, cx - 2 * n, B + n,
                          fill=CREAM, outline=OUTLINE, width=o, tags="tail")
        cv.create_rectangle(cx - 2 * n + o, B - o, cx + 2 * n - o, B + o,
                            fill=CREAM, outline="", tags="tail")

    def place(self):
        pet, S = self.pet, self.pet.S
        cx = pet.x + pet.W / 2
        x = int(min(max(cx - self.w / 2, pet.minx), pet.maxx + pet.W - self.w))
        y = int(max(0, pet.y + 11 * S - self.h))
        rel = int(cx - x)
        if self.rel is None or abs(rel - self.rel) >= S:
            self.tail(rel)
            self.rel = rel
        if (x, y) != self.pos:
            self.win.geometry(f"{self.w}x{self.h}+{x}+{y}")
            self.pos = (x, y)

    def hide(self):
        if self.visible:
            self.win.withdraw()
            self.visible = False


class Astro:
    def __init__(self):
        for fn in (lambda: ctypes.windll.shcore.SetProcessDpiAwareness(2),
                   lambda: ctypes.windll.user32.SetProcessDPIAware()):
            try:
                fn()
                break
            except Exception:
                pass
        self.u = winapi()
        try:
            dpi = self.u.GetDpiForSystem()
        except Exception:
            dpi = 96
        S = self.S = max(3, round(4 * dpi / 96))
        self.W, self.H = CW * S, CH * S
        self.G, self.J, self.WALK, self.HARD = 0.55 * S, 4.0 * S, 0.6 * S, 6.0 * S

        r = self.root = tk.Tk()
        r.title("Astro")
        r.overrideredirect(True)
        r.configure(bg=KEY)
        r.attributes("-topmost", True)
        r.attributes("-transparentcolor", KEY)
        self.cv = tk.Canvas(r, width=self.W, height=self.H, bg=KEY, highlightthickness=0, bd=0)
        self.cv.pack()
        self.item = self.cv.create_image(0, 0, anchor="nw")
        self.cache, self.cur, self.pos = {}, None, None

        self.refresh_screen()
        self.x = random.randint(int(self.minx), int(self.maxx))
        self.y = float(self.floor)
        self.vx = self.vy = 0.0
        self.dir, self.look, self.hops = 1, 0, 0
        self.state, self.st, self.dur = "idle", 0, 60
        self.hidden = False
        self.clicks, self.hist = [], []
        self.last_active = time.time()
        self.autowalk = tk.BooleanVar(value=True)
        self.moved = False
        self.speech = tk.BooleanVar(value=True)
        self.pending, self.fired = None, set()
        now = time.time()
        self.greet_at, self.next_clock = now + GREETING_DELAY_S, 0.0
        self.schedule_chat()

        r.geometry(f"{self.W}x{self.H}+{int(self.x)}+{int(self.y)}")
        r.update_idletasks()
        self.hwnd = self.u.GetParent(r.winfo_id()) or r.winfo_id()

        self.menu = tk.Menu(r, tearoff=0)
        self.menu.add_command(label="Wave", command=lambda: self.ground_do("wave", 90))
        self.menu.add_command(label="Spin jump", command=self.start_spin)
        self.menu.add_command(label="Take a nap", command=lambda: self.ground_do("sleep", 2400))
        self.menu.add_command(label="Say something",
                              command=lambda: setattr(self, "pending", (random.choice(CHAT), False)))
        self.menu.add_checkbutton(label="Wander around", variable=self.autowalk)
        self.menu.add_checkbutton(label="Speech on", variable=self.speech)
        self.menu.add_separator()
        self.menu.add_command(label="Quit Astro", command=r.destroy)

        self.bubble = Bubble(self)
        self.music_pending = None
        self.music = NowPlaying(self.on_song) if NOW_PLAYING else None
        self.cv.bind("<ButtonPress-1>", self.on_press)
        self.cv.bind("<B1-Motion>", self.on_motion)
        self.cv.bind("<ButtonRelease-1>", self.on_release)
        self.cv.bind("<Button-3>", self.on_menu)
        self.tick_count = 0
        self.tick()

    # ── geometry ──
    @property
    def floor(self):
        return self.ground - self.H

    def refresh_screen(self):
        wa = wintypes.RECT()
        self.u.SystemParametersInfoW(0x30, 0, ctypes.byref(wa), 0)  # work area = above taskbar
        self.ground = wa.bottom
        self.minx, self.maxx = wa.left, wa.right - self.W

    # ── fullscreen / always-on-top ──
    def fullscreen_active(self):
        try:
            u = self.u
            hwnd = u.GetForegroundWindow()
            if not hwnd or not u.IsWindowVisible(hwnd) or u.IsIconic(hwnd):
                return False
            pid = wintypes.DWORD()
            u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value == ctypes.windll.kernel32.GetCurrentProcessId():
                return False
            buf = ctypes.create_unicode_buffer(64)
            u.GetClassNameW(hwnd, buf, 64)
            if buf.value in SHELL_CLASSES:
                return False
            rc = wintypes.RECT()
            u.GetWindowRect(hwnd, ctypes.byref(rc))
            mi = MONITORINFO()
            mi.cbSize = ctypes.sizeof(MONITORINFO)
            u.GetMonitorInfoW(u.MonitorFromWindow(hwnd, 2), ctypes.byref(mi))
            m = mi.rcMonitor
            covers = rc.left <= m.left and rc.top <= m.top and rc.right >= m.right and rc.bottom >= m.bottom
            exact = (rc.left, rc.top, rc.right, rc.bottom) == (m.left, m.top, m.right, m.bottom)
            captioned = (u.GetWindowLongW(hwnd, -16) & 0x00C00000) == 0x00C00000
            return covers and (exact or not captioned)  # maximised windows keep a caption
        except Exception:
            return False

    def housekeeping(self):
        self.refresh_screen()
        fs = self.fullscreen_active()
        if fs and not self.hidden:
            self.root.withdraw()
            self.bubble.hide()
            self.hidden = True
        elif not fs and self.hidden:
            self.root.deiconify()
            self.hidden, self.pos = False, None
        if not self.hidden:
            try:  # re-assert topmost (the taskbar likes to steal it)
                self.u.SetWindowPos(self.hwnd, wintypes.HWND(-1), 0, 0, 0, 0, 0x13)
            except Exception:
                pass

    # ── are you around? (asks Windows for "seconds since last input" - a timestamp, never what you type) ──
    def system_idle_seconds(self):
        try:
            li = LASTINPUTINFO()
            li.cbSize = ctypes.sizeof(li)
            if self.u.GetLastInputInfo(ctypes.byref(li)):
                return ((ctypes.windll.kernel32.GetTickCount() - li.dwTime) & 0xFFFFFFFF) / 1000
        except Exception:
            pass
        return 0.0  # unknown -> assume you're there, so he never falls asleep by mistake

    def idle_for(self):
        return min(self.system_idle_seconds(), time.time() - self.last_active)

    # ── state helpers ──
    def set(self, state, dur=0):
        self.state, self.st, self.dur = state, 0, dur

    def ground_do(self, state, dur):
        if self.state not in AIR and self.state != "drag":
            self.last_active = time.time()
            self.set(state, dur)

    def start_happy(self):
        self.hops, self.vy, self.vx = 2, -self.J, 0
        self.set("happy")

    def start_spin(self):
        if self.state in AIR or self.state == "drag":
            return
        self.last_active = time.time()
        self.vy, self.vx = -self.J * 1.25, 0
        self.set("spin")

    # ── mouse ──
    def on_press(self, e):
        self.grab = (e.x_root - self.x, e.y_root - self.y)
        self.press = (e.x_root, e.y_root)
        self.moved, self.hist = False, []

    def on_motion(self, e):
        if not self.moved:
            if abs(e.x_root - self.press[0]) + abs(e.y_root - self.press[1]) < 5:
                return
            self.moved = True
            self.vx = self.vy = 0
            self.set("drag")
        self.x = min(self.maxx, max(self.minx, e.x_root - self.grab[0]))
        self.y = min(self.floor, max(0, e.y_root - self.grab[1]))
        self.hist = (self.hist + [(time.time(), self.x, self.y)])[-6:]
        self.last_active = time.time()
        self.place()

    def on_release(self, e):
        if self.moved:
            self.vx = self.vy = 0.0
            if len(self.hist) >= 2:
                t0, x0, y0 = self.hist[0]
                t1, x1, y1 = self.hist[-1]
                dt = max(t1 - t0, 0.03)
                lim = 5 * self.S
                self.vx = max(-lim, min(lim, (x1 - x0) / dt * TICK_MS / 1000))
                self.vy = max(-lim, min(lim, (y1 - y0) / dt * TICK_MS / 1000))
            self.set("fall")
        else:
            self.on_click()

    def on_click(self):
        now = time.time()
        self.last_active = now
        self.bubble.hide()
        self.clicks = [t for t in self.clicks if now - t < 1.6] + [now]
        if self.state in AIR:
            return
        n = len(self.clicks)
        if n >= 6:
            self.clicks = []
            self.set("dizzy", 100)
        elif n >= 3:
            self.start_spin()
        else:
            self.start_happy()

    def on_menu(self, e):
        try:
            self.menu.tk_popup(e.x_root, e.y_root)
        finally:
            self.menu.grab_release()

    # ── talking (just a clock check every ~20 s; no listening to anything) ──
    def schedule_chat(self):
        self.next_chat = time.time() + random.uniform(*CHAT_EVERY_MIN) * 60

    def greeting(self):
        h = time.localtime().tm_hour
        part = ("Good morning" if 5 <= h < 12 else "Good afternoon" if h < 17
                else "Good evening" if h < 22 else "Hey, night owl")
        return part + (", " + USER_NAME if USER_NAME else "") + "!"

    def due_reminder(self):
        lt = time.localtime()
        today, nowm = (lt.tm_year, lt.tm_yday), lt.tm_hour * 60 + lt.tm_min
        for hhmm, text in REMINDERS:
            h, m = map(int, hhmm.split(":"))
            if 0 <= nowm - (h * 60 + m) <= 5 and (today, hhmm) not in self.fired:
                self.fired.add((today, hhmm))
                return text

    def on_song(self, title, artist):  # called from the watcher thread
        title = title if len(title) <= 60 else title[:57] + "..."
        if NOW_PLAYING_SHOW_ARTIST and artist:
            title += " - " + artist
        self.music_pending = ("Now playing!\n" + title, time.time())

    def talk_check(self):
        if not self.speech.get():
            self.pending = self.music_pending = None
            self.bubble.hide()
            return
        now = time.time()
        if self.music_pending:
            text, ts = self.music_pending
            if now - ts > 15:  # stale (e.g. you were in a fullscreen game)
                self.music_pending = None
            elif not self.hidden and self.state not in AIR and self.state != "drag":
                self.music_pending = None
                self.bubble.show(text, max(5.0, 3 + 0.07 * len(text)))
                self.last_active = now
                self.set("music", 75)  # ~2.5 s of headphone bopping
                return
        if self.pending is None and now >= self.next_clock:
            self.next_clock = now + 20
            if self.greet_at and now >= self.greet_at:
                self.greet_at = None
                self.pending = (self.greeting(), True)
            else:
                text = self.due_reminder()
                if text:
                    self.pending = (text, True)
                elif now >= self.next_chat:
                    self.pending = (random.choice(CHAT), False)
                    self.schedule_chat()
        if (self.pending and not self.hidden and not self.bubble.visible
                and self.state not in AIR and self.state != "drag"):
            text, wave = self.pending
            self.pending = None
            secs = max(5.0, 3 + 0.07 * len(text))
            self.last_active = now
            self.bubble.show(text, secs)
            if wave:
                self.set("wave", 60)
            else:
                self.set("idle", int(secs * 1000 / TICK_MS))

    # ── behaviour ──
    def update_look(self):
        px, py = self.root.winfo_pointerxy()
        cx, cy = self.x + self.W / 2, self.y + self.H / 2
        if abs(px - cx) < 400 and abs(py - cy) < 350:
            self.look = 1 if px > cx + self.W * 0.3 else -1 if px < cx - self.W * 0.3 else 0
        elif random.random() < 0.3:
            self.look = random.choice((-1, 0, 1))

    def choose_next(self):
        idle_for = self.idle_for()
        r = random.random()
        if idle_for > SLEEP_AFTER_IDLE_S - 60 and r < 0.5:
            return self.set("sit", random.randint(60, 120))
        if self.autowalk.get() and r < 0.5:
            self.dir = random.choice((-1, 1))
            if self.x < self.minx + self.W:
                self.dir = 1
            if self.x > self.maxx - self.W:
                self.dir = -1
            return self.set("walk", random.randint(50, 200))
        if r < 0.68:
            return self.set("sit", random.randint(120, 280))
        if r < 0.82:
            return self.set("wave", 84)
        self.set("idle", random.randint(50, 140))

    def land(self):
        v = self.vy
        self.y, self.vy, self.vx = float(self.floor), 0.0, 0.0
        if self.state == "fall":
            self.set("dizzy", 90) if v > self.HARD else self.set("land", 12)
        elif self.state == "happy":
            self.hops -= 1
            if self.hops > 0:
                self.vy = -self.J * 0.7
            else:
                self.set("idle", 40)
        else:
            self.set("land", 8)

    def update(self):
        self.st += 1
        s = self.state
        if s == "drag":
            return
        if s in AIR:
            self.vy += self.G
            self.y += self.vy
            self.x += self.vx
            if self.x < self.minx or self.x > self.maxx:
                self.x = min(self.maxx, max(self.minx, self.x))
                self.vx *= -0.6
            if self.y >= self.floor:
                self.land()
            return
        self.y = float(self.floor)
        if s in ("idle", "sit") and self.st % 8 == 0:
            self.update_look()
        if s == "idle" and self.st >= self.dur:
            self.choose_next()
        elif s == "walk":
            self.x += self.dir * self.WALK
            self.look = self.dir
            if self.x <= self.minx or self.x >= self.maxx:
                self.x = min(self.maxx, max(self.minx, self.x))
                self.dir *= -1
            if self.st >= self.dur:
                self.set("idle", random.randint(40, 100))
        elif s == "sit" and self.st >= self.dur:
            if self.idle_for() > SLEEP_AFTER_IDLE_S:
                self.set("sleep", 10 ** 9)  # sleeps until you come back
            else:
                self.set("idle", random.randint(40, 100))
<<<<<<< HEAD
        elif s == "sleep" and self.st >= self.dur:
            self.last_active = time.time()
            self.set("idle", 60)
=======
        elif s == "sleep":
            if self.st % 30 == 0 and self.dur > 10 ** 6 and self.system_idle_seconds() < 5:
                self.set("idle", 60)  # you're back: wake up
            elif self.st >= self.dur:  # a manual nap from the menu ran out
                self.last_active = time.time()
                self.set("idle", 60)
>>>>>>> experimental
        elif s in ("wave", "land", "dizzy", "music") and self.st >= self.dur:
            self.set("idle", random.randint(40, 100))

    # ── drawing ──
    def pose(self):
        s, t, look = self.state, self.st, self.look
        legs, arms, eyes, bob, k, fx, fp, hp = "stand", "down", "open", 0, 1.0, None, 0, False
        if s == "idle":
            eyes, bob = ("blink" if t % 110 > 104 else "open"), (t // 25) % 2
        elif s == "walk":
            legs = ("walkA", "walkB", "walkA", "walkC")[(t // 4) % 4]
            bob = 1 if legs == "walkA" else 0
        elif s == "sit":
            legs, eyes = "sit", ("blink" if t % 110 > 104 else "open")
        elif s == "sleep":
            legs, eyes, look, bob, fx, fp = "sit", "sleep", 0, (t // 30) % 2, "zzz", (t // 8) % 12
        elif s == "music":
            eyes, look, bob, hp = "happy", 0, (t // 6) % 2, True
        elif s == "wave":
            arms, eyes, look = ("waveA", "waveB")[(t // 6) % 2], "happy", 0
        elif s == "happy":
            arms, eyes, look, fx, fp = "up", "happy", 0, "hearts", min(t // 2, 30)
            legs = "tuck" if self.y < self.floor - 1 else "stand"
        elif s == "spin":
            arms, legs, eyes, look, k = "up", "tuck", "happy", 0, SPIN[(t // 2) % 8]
        elif s == "drag":
            arms, legs, eyes, look, fx = "up", ("dangleA", "dangleB")[(t // 5) % 2], "wide", 0, "bang"
        elif s == "fall":
            arms, legs, eyes, look = "up", "dangleB", "wide", 0
        elif s == "land":
            legs, eyes, look = "sit", "sleep", 0
        elif s == "dizzy":
            legs, eyes, look, fx, fp = "sit", "x", 0, "stars", (t // 3) % 12
        return (legs, arms, eyes, look, bob, k, fx, fp, hp)

    def image_for(self, key):
        img = self.cache.get(key)
        if img is None:
            px = build(*key)
            rows = ["{" + " ".join(COL.get(px.get((x, y)), KEY) for x in range(CW)) + "}"
                    for y in range(CH)]
            small = tk.PhotoImage(width=CW, height=CH)
            small.put(" ".join(rows))
            img = self.cache[key] = small.zoom(self.S)
        return img

    def place(self):
        p = (int(self.x), int(self.y))
        if p != self.pos:
            self.root.geometry(f"+{p[0]}+{p[1]}")
            self.pos = p

    def tick(self):
        self.tick_count += 1
        if self.tick_count % 15 == 1:
            self.housekeeping()
            self.talk_check()
        if self.bubble.visible:
            if self.hidden or self.state == "drag" or time.time() >= self.bubble.until:
                self.bubble.hide()
            else:
                self.bubble.place()
        if not self.hidden:
            self.update()
            key = self.pose()
            if key != self.cur:
                self.cv.itemconfig(self.item, image=self.image_for(key))
                self.cur = key
            self.place()
        self.root.after(TICK_MS, self.tick)


if __name__ == "__main__":
    if sys.platform != "win32":
        sys.exit("Astro is built for Windows (it uses the Windows taskbar and window APIs).")
    Astro().root.mainloop()