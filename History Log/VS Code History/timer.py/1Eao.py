import webbrowser
import time
import random

timerRange = [0,120]

while True:
    input()
    timerInit = random.randint(timerRange[0],timerRange[1])
    breakRange = []
    timer = time.time()
    while time.time() - timer < 