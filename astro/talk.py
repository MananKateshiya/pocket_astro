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


def pick_chat(recent):
    pool = cfg.CHAT_TIME[time_slot()] if random.random() < cfg.TIME_CHAT_CHANCE else cfg.CHAT
    for _ in range(5):
        line = random.choice(pool)
        if line not in recent:
            break
    return line, (recent + [line])[-8:]
