zz ={'X': {'type': 'INTEGER', 'value': 4}, 'Y': {'type': 'BOOLEAN', 'value': False}, 'StudentNames': {'type': 'ARRAY', 'value': [None, None, None, 204.0, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], 'dimensions': [[1, 30]], 'arrayType': 'INTEGER'}, 'Z': {'type': 'INTEGER', 'value': 377}, 'SumSquare': {'type': 'FUNCTION', 'value': None, 'code': ['RETURN Number1 * Number1 + Number2 * Number2'], 'parameters': [{'name': 'Number1', 'type': 'INTEGER'}, {'name': 'Number2', 'type': 'INTEGER'}], 'localVar': [], 'returnType': 'INTEGER'}}

y = (not 9==0 or 5 == 4)

X = 4
StudentNames = [x for x in range(6)]
StudentNames[X-1] = int(800/4+X)

def SumSquare(number1, number2):
    return int(number1) * int(number1) + int(number2) * int(number2)

z = (SumSquare(5+(X),(X*3)) + (StudentNames[(X)-1]))
""