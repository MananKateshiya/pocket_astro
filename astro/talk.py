import random
import time

from . import config as cfg


def time_slot():
    h = time.localtime().tm_hour
    if h < 5 or h >= 22:
        return "night"
    if h < 12:
        return "morning"
    if h < 17:
        return "afternoon"
    return "evening"


def greeting(name):
    part = {"morning": "Good morning", "afternoon": "Good afternoon",
            "evening": "Good evening", "night": "Hey, night owl"}[time_slot()]
    return part + (", " + name if name else "") + "!"


def due_reminder(fired):
    lt = time.localtime()
    today, nowm = (lt.tm_year, lt.tm_yday), lt.tm_hour * 60 + lt.tm_min
    for hhmm, text in cfg.REMINDERS:
        h, m = map(int, hhmm.split(":"))
        if 0 <= nowm - (h * 60 + m) <= 5 and (today, hhmm) not in fired:
            fired.add((today, hhmm))
            return text
    return None


class ChatPicker:
    def __init__(self):
        self.remaining = {}
        self.last_shown = {}

    def _draw(self, name, pool):
        if not pool:
            return None
        if not self.remaining.get(name):
            lines = list(pool)
            random.shuffle(lines)
            last = self.last_shown.get(name)
            if len(lines) > 1 and lines[0] == last:
                lines[0], lines[1] = lines[1], lines[0]
            self.remaining[name] = lines
        line = self.remaining[name].pop(0)
        self.last_shown[name] = line
        return line

    def pick(self):
        slot = time_slot()
        time_name, time_pool = slot, cfg.CHAT_TIME[slot]
        general_name, general_pool = "general", cfg.CHAT
        if random.random() < cfg.TIME_CHAT_CHANCE:
            choices = ((time_name, time_pool), (general_name, general_pool))
        else:
            choices = ((general_name, general_pool), (time_name, time_pool))
        for name, pool in choices:
            line = self._draw(name, pool)
            if line is not None:
                return line
        raise ValueError("Chat pools cannot both be empty")
