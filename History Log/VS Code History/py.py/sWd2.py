NumberGenerated = [[]]
var = {'Player1': {'type': 'STRING', 'value': 'Ali'}, 'Player2': {'type': 'STRING', 'value': 'Aisha'}, 'NumberGenerated': {'type': 'ARRAY', 'value': [[5, 3, 2, 5, 5, 2, 1, 3, 1, 5, 5, 6, 2, 1, 4, 3, 3, 4, 3, 2, 3, 3, 4, 2, 4, 3, 3, 3, 3, 4, 1, 3, 5, 6, 5, 4, 5, 5, 2, 3, 4, 3, 3, 1, 3, 1, 6, 3, 6, 4, 2, 3, 2, 2, 5, 2, 6, 2, 3, 4, 2, 5, 3, 6, 4, 3, 4, 2, 6, 4, 6, 1, 2, 5, 5, 5, 3, 4, 3, 2, 2, 5, 2, 2, 3, 2, 2, 4, 4, 4, 2, 1, 6, 1, 4, 3, 4, 2, 4, 3], [6, 5, 3, 1, 5, 3, 5, 3, 5, 4, 2, 4, 5, 5, 2, 4, 3, 1, 5, 3, 3, 2, 1, 2, 6, 3, 2, 5, 4, 5, 5, 5, 2, 2, 1, 4, 6, 4, 4, 5, 3, 1, 3, 6, 1, 4, 3, 2, 4, 6, 3, 3, 4, 4, 6, 3, 3, 4, 2, 4, 2, 5, 3, 4, 6, 1, 3, 5, 4, 5, 2, 2, 5, 4, 5, 3, 5, 3, 2, 5, 4, 4, 1, 2, 1, 2, 5, 4, 4, 2, 5, 2, 6, 5, 1, 5, 4, 1, 1, 5]], 'dimensions': [[1, 2], [1, 100]], 'arrayType': 'INTEGER'}, 'Points': {'type': 'ARRAY', 'value': [94, 106], 'dimensions': [[1, 2]], 'arrayType': 'INTEGER'}, 'X': {'type': 'INTEGER', 'value': 100}, 'Y': {'type': 'INTEGER', 'value': 100}}

Points = [0,0]

print("Please enter the name of player 1 ")
Player1 = input()

while Player1 == "":
    print("You must enter a name, try again ")
    Player1 = input()

print("Please enter the name of player 2 ")
Player2 = input()
while Player2 == "":
    print("You must enter a name, try again ")
    Player2 = input()

for X in range(1,3):
    for Y in range(1,101):
        NumberGenerated[X, Y] ← ROUND(RANDOM() * 5, 0) + 1
    NEXT Y
NEXT X

//comparing the random numbers
FOR X ← 1 TO 100
    IF NumberGenerated[1, X] > NumberGenerated[2, X]
        THEN
            Points[1] ← Points[1] + 2
        ELSE
            IF NumberGenerated[1, X] < NumberGenerated[2, X]
                THEN
                    Points[2] ← Points[2] + 2
            ENDIF
    ENDIF
    IF NumberGenerated[1, X] = NumberGenerated[2, X] // if tied (the same)
        THEN
            Points[1] ← Points[1] + 1
            Points[2] ← Points[2] + 1
    ENDIF
NEXT X

// if player 1 and player 2 tie
// could be a function
IF Points[1] = Points[2]
    THEN
        REPEAT
            P1 ← ROUND(RANDOM * 6, 0) + 1
            P2 ← ROUND(RANDOM * 6, 0) + 1
        UNTIL P1 <> P2
    IF P1 > P2
        THEN
            Points[1] ← Points[1] + 2
        ELSE
            Points[2] ← Points[2] + 2
    ENDIF
ENDIF

// determine the overall winner
IF Points[1] > Points[2]
    THEN
        OUTPUT "First is ", Player1
        OUTPUT "With a total score of ", Points[1]
        OUTPUT "Second is ", Player2
        OUTPUT "With a total score of ", Points[2]
    ELSE
        OUTPUT "First is ", Player2
        OUTPUT "With a total score of ", Points[2]
        OUTPUT "Second is ", Player1
        OUTPUT "With a total score of ", Points[1]
ENDIF