import random
import time

timer = time.time()

RandomNumber = [0 for x in range(0,100001)]

for Index1 in range(0, 100001):
    print(Index1)
    RandomNumber[Index1] = round(random.random() * 9, 0) + 1

print(time.time()-timer)
print(34.7/(time.time()-timer))