USER_NAME = "MANAN"              # put your name here, e.g. "Manan", to be greeted by name
GREETING_DELAY_S = 10       # greets you this many seconds after he starts
CHAT_EVERY_MIN = (5, 13)    # random small-talk every 6-14 minutes
SLEEP_AFTER_IDLE_S = 180    # he only dozes off after this long with no keyboard/mouse use at all
NOW_PLAYING = True          # announce songs/videos playing in any app or browser tab
NOW_PLAYING_SHOW_ARTIST = False   # True -> "Title - Artist" (YouTube shows the channel name)
REMINDERS = [               # ("HH:MM" 24h clock, message) - each fires once a day
    ("10:30", "Water time! Sip sip."),
    ("14:00", "Lunch break? Fuel up, astronaut."),
    ("16:00", "Stretch your back for a minute."),
    ("18:00", "It's 6 PM... coffee time?"),
    ("23:30", "Getting late. Maybe wrap up soon?"),
]


TIME_CHAT_CHANCE = 0.65   # how often he picks from the current time-of-day pool

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
    "It works on my machine.",
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

CHAT_TIME = {
    "morning": [
        "Rise and shine! Today's mission: be awesome.",
        "Fresh day, fresh orbit. Let's go!",
        "Three, two, one... let's get started!",
        "Morning energy: loading... 100%!",
        "Today is a great day to launch something.",
        "Fuel up before you code. Breakfast counts!",
        "The Sun is up and so are you. Impressive.",
        "Pick one big task and own it today.",
    ],
    "afternoon": [
        "Hydration check! Water, please.",
        "Quick stretch time. Shoulders down!",
        "Feeling sluggish? A short walk reboots you.",
        "Halfway through the mission. Keep your pace.",
        "Posture check: sit up straight, astronaut.",
        "Snack break? Brains run on fuel.",
        "Try 25 minutes of focus, then a break.",
        "Look at something far away for a moment.",
    ],
    "evening": [
        "The day's work is done. Slow down a little.",
        "Dim the lights and breathe out slowly.",
        "You did enough today. Really.",
        "Maybe a walk or some music? You've earned it.",
        "Time to cool the engines.",
        "Tea sounds nice right about now.",
        "Today counted. Be kind to yourself tonight.",
        "The stars are coming out. Go look.",
    ],
    "night": [
        "Human, the Sun has been gone for hours. Please reconsider.",
        "It's late. Even rockets get grounded for the night.",
        "The bugs will still be there tomorrow. Sleep.",
        "I'm sleepy and you're still typing. Rude.",
        "Sleep is the best debugging tool.",
        "Your pillow is feeling neglected.",
        "This is a 3 AM idea. It will look worse in daylight.",
        "Go to bed. I'll guard the taskbar.",
    ],
}
