import webbrowser
import time
import random
import math

timerRange = [0,120]

while True:
    input("Enter for new study session: ")
    timerInit = random.randint(timerRange[0],timerRange[1])*60
    breakRange = [math.ceil(timerInit / 10), math.ceil(timerInit / 2)]
    breakInit = random.randint(breakRange[0],breakRange[1]) 


    timer = time.time()
    while time.time() - timer < timerInit:
        ""

    print(f"Total time: {round(timerInit/60)}min")
    print(f"Break: {round(breakInit/60)}min")

    webbrowser.open("https://www.youtube.com/watch?v=YZ3XjVVNagU&list=PLkVMflJLxsICiJLYcqoXd0I73CW3VC_RT&pp=gAQBiAQB")
    timer = time.time()
    while time.time() - timer < breakInit:
        ""
    
    webbrowser.open("https://www.youtube.com/watch?v=YZ3XjVVNagU&list=PLkVMflJLxsICiJLYcqoXd0I73CW3VC_RT&pp=gAQBiAQB")
