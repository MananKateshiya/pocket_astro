import random
import time
import tkinter as tk

from . import config as cfg
from .bubble import Bubble
from .music import NowPlaying
from .sprites import CH, CW, COL, KEY, SPIN, build
from .talk import ChatPicker, due_reminder, greeting
from .winapi import (fullscreen_active, make_dpi_aware, set_topmost,
                     system_idle_seconds, winapi, work_area)


AIR = {"fall", "happy", "spin"}
TICK_MS = 33


class Astro:
    def __init__(self):
        make_dpi_aware()
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
        self.chat_picker = ChatPicker()
        now = time.time()
        self.greet_at, self.next_clock = now + cfg.GREETING_DELAY_S, 0.0
        self.schedule_chat()

        r.geometry(f"{self.W}x{self.H}+{int(self.x)}+{int(self.y)}")
        r.update_idletasks()
        self.hwnd = self.u.GetParent(r.winfo_id()) or r.winfo_id()

        self.menu = tk.Menu(r, tearoff=0)
        self.menu.add_command(label="Wave", command=lambda: self.ground_do("wave", 90))
        self.menu.add_command(label="Spin jump", command=self.start_spin)
        self.menu.add_command(label="Take a nap", command=lambda: self.ground_do("sleep", 2400))
        self.menu.add_command(label="Say something",
                              command=lambda: setattr(self, "pending", (self.pick_chat(), False)))
        self.menu.add_checkbutton(label="Wander around", variable=self.autowalk)
        self.menu.add_checkbutton(label="Speech on", variable=self.speech)
        self.menu.add_separator()
        self.menu.add_command(label="Quit Astro", command=r.destroy)

        self.bubble = Bubble(self)
        self.music_pending = None
        self.music = NowPlaying(self.on_song) if cfg.NOW_PLAYING else None
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
        wa = work_area(self.u)
        self.ground = wa.bottom
        self.minx, self.maxx = wa.left, wa.right - self.W

    # ── fullscreen / always-on-top ──
    def fullscreen_active(self):
        return fullscreen_active(self.u)

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
                set_topmost(self.u, self.hwnd)
            except Exception:
                pass

    # ── are you around? (asks Windows for "seconds since last input" - a timestamp, never what you type) ──
    def system_idle_seconds(self):
        return system_idle_seconds(self.u)

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
        self.next_chat = time.time() + random.uniform(*cfg.CHAT_EVERY_MIN) * 60

    def pick_chat(self):
        return self.chat_picker.pick()

    def greeting(self):
        return greeting(cfg.USER_NAME)

    def due_reminder(self):
        return due_reminder(self.fired)

    def on_song(self, title, artist):  # called from the watcher thread
        title = title if len(title) <= 60 else title[:57] + "..."
        if cfg.NOW_PLAYING_SHOW_ARTIST and artist:
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
                    self.pending = (self.pick_chat(), False)
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
        if idle_for > cfg.SLEEP_AFTER_IDLE_S - 60 and r < 0.5:
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
            if self.idle_for() > cfg.SLEEP_AFTER_IDLE_S:
                self.set("sleep", 10 ** 9)  # sleeps until you come back
            else:
                self.set("idle", random.randint(40, 100))
        elif s == "sleep":
            if self.st % 30 == 0 and self.dur > 10 ** 6 and self.system_idle_seconds() < 5:
                self.set("idle", 60)  # you're back: wake up
            elif self.st >= self.dur:  # a manual nap from the menu ran out
                self.last_active = time.time()
                self.set("idle", 60)
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

    def _tick(self):
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

    def tick(self):
        try:
            self._tick()
        finally:
            self.root.after(TICK_MS, self.tick)

