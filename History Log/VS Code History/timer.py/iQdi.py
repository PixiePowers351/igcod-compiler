import webbrowser
import time
import random
import math

timerRange = [0,120]

while True:
    input()
    timerInit = random.randint(timerRange[0],timerRange[1])
    breakRange = [math.ceil(timerInit / 10), math.ceil(timerInit / 2)]
    breakInit = random.randint(breakRange[0],breakRange[1])

    timer = time.time()
    while time.time() - timer < timerInit:
        ""

    webbrowser.open("https://www.youtube.com/watch?v=YZ3XjVVNagU&list=PLkVMflJLxsICiJLYcqoXd0I73CW3VC_RT&pp=gAQBiAQB")
    timer = time.time()
    while time.time() - timer < breakInit:
        ""
        