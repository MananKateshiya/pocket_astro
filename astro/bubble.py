import tkinter as tk
import tkinter.font as tkfont
import time

from .sprites import CREAM, KEY, NAVY, OUTLINE

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

