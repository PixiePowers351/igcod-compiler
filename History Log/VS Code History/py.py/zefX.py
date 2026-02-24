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
        ENDIF
    NEXT Index2
NEXT Index1

// performing sort on frequencies, so the possible random numbers
// are stored in descending order of frequency
Swap ← TRUE
WHILE Swap DO
    // sort is terminated when no swaps take place during a pass
    Swap ← FALSE
    FOR Index1 ← 1 TO 9
        IF CountedNumber[Index1, 2] < CountedNumber[Index1 + 1, 2]
            THEN
                Temp1 ← CountedNumber[Index1, 1]
                Temp2 ← CountedNumber[Index1, 2]
                CountedNumber[Index1, 1] ← CountedNumber[Index1 + 1, 1]
                CountedNumber[Index1, 2] ← CountedNumber[Index1 + 1, 2]
                CountedNumber[Index1 + 1, 1] ← Temp1
                CountedNumber[Index1 + 1, 2] ← Temp2
                Swap ← TRUE
        ENDIF
    NEXT Index1
ENDWHILE

// outputting the results, with chances for each random number
// calculated to 4 d.p.
// results in descending order of frequency
FOR Index1 ← 1 TO 10
    OUTPUT "The chance of ", CountedNumber[Index1, 1], " occurring is: "
    OUTPUT ROUND(CountedNumber[Index1, 2]/100000, 4)
NEXT Index1


print(time.time()-timer)
print(179389/(time.time()-timer))