import random
import time

timer = time.time()

RandomNumber = [0 for x in range(100000)]
CountedNumber = [[0,0] for x in range(10)]
for Index1 in range(100000):
    RandomNumber[Index1] = round(random.random() * 9, 0) + 1

for Index1 in range(10):
    CountedNumber[Index1][0] = Index1
    CountedNumber[Index1][1] = 0

for Index1 in range(10):
    for Index2 in range(100000):
        if RandomNumber[Index2] == CountedNumber[Index1][0]:
            CountedNumber[Index1][1] = CountedNumber[Index1][1] + 1

Swap = True
while Swap:
    Swap = False
    for Index1 in range(9):
            if CountedNumber[Index1][1] < CountedNumber[Index1 + 1][1]:
                Temp1 = CountedNumber[Index1][0]
                Temp2 = CountedNumber[Index1][1]
                CountedNumber[Index1][0] = CountedNumber[Index1+1][0]
                CountedNumber[Index1][1] = CountedNumber[Index1+1][1]
                CountedNumber[Index1+1][0] = Temp1
                CountedNumber[Index1+1][1] = Temp2
                Swap = True

for Index1 in range(10):
    print("The chance of ", CountedNumber[Index1][0], " occurring is: ")
    print(round(CountedNumber[Index1][1]/100000, 4))


print(time.time()-timer)
print(179389/(time.time()-timer))