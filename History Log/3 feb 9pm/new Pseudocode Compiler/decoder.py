import time
import random
import json
import copy

timer = time.time()
#open and read code file
cd = open("code.txt","r", encoding="utf-8")
cd = cd.readlines()

var = {} #variable storing all variables declared in code
files = {} #variable with all list of files open

codeOg = [x[:len(x)-1] if x[-1] == "\n" else x for x in cd] #replace "\n" characters at end of string


#remove blank lines, comments, replace some weird characters
for x in range(len(codeOg)):
    codeOg[x] = codeOg[x].split("//")[0]
    codeOg[x] = codeOg[x].replace("–","-")

#open settings
settings = open("settings.json","r", encoding="utf-8")
settings = json.load(settings)

#defaults        
delimiter = settings["delimiter"]["value"]
debug = bool(settings["debugMode"]["value"])
displayTime = bool(settings['displayTime']['value'])
noNewLineOutput = bool(settings["noNewLineOutput"]["value"])
autoDeclareVariables = bool(settings['noDeclaration']['value'])
mutableParameters = bool(settings['mutableParameters']['value'])

error = False
codePointer = 0
inProcedure = [] #variables declared in a procedure

def removeSpace(text):
    if type(text) is not str:
        return text
    
    #upper whitespace
    return text.strip()
    

def firstSpecialChar(value):
    if value.isalpha():
        return 0
    
    for x in range(len(value)):
        if not value[x].isalpha() and value[x] != " ":
            break
    return x

def bracketExcludedSplit(value,splitValue):
    inBracket = 0
    temp = []

    if len(value.split(splitValue))>1:
        for x in range(len(value)-len(splitValue)):
            if value[x] == splitValue and inBracket == 0:
                temp.append(value[:x].replace("".join([x+splitValue for x in temp]),""))
            elif value[x] in ["(","["]:
                if inBracket == 1 and value[x] == '"':
                    inBracket = 0
                else:
                    inBracket += 1
            elif value[x] in [")","]"]:
                inBracket -= 1

    if len(temp) != 0:      
        temp.append(value.replace("".join([x+splitValue for x in temp]),""))

    elif len(value) > 0:
        temp = [value]

    return temp

def varReplace(value,originalValue,replaceValue ):
    value = list(value)
    x = 0
    inBracket = 0
    while x <= len(value)-len(originalValue):
        #check if value substring matches original value and: either its on the beginning of a line or the character before it is not an alphanumeric character and character after it is not an alphanumeric character and also check if its not a string with the exact same value as the variable name
        if "".join(value[x:x+len(originalValue)]) == originalValue and (x == 0 or not value[x-1].isalpha()) and (x+1 > len(value)-len(originalValue) or not value[x+len(originalValue)].isalpha())  and (not value[x-1]=="'" and not value[x-1]=='"'):
            value[x:x+len(originalValue)] = replaceValue
            x += len(replaceValue) - 1

        x += 1

    return "".join(value)

def errorHandle(errorText):
    global error
    print(F"ERROR: {errorText}")
    error = True
    print(codeOg[codePointer])
    quit()

def removeExtraBrackets(value):

    if type(value) is not str:
        return value

    x= 0

    while value[x] == "(":
        x += 1
    
    while True:
        lastExpression = value[x:len(value)-x]
        y = 0
        for m in lastExpression:
            if m == "(":
                y += 1
            elif m == ")":
                y -= 1
        
            if y == -1:
                break
            
        if y == 0:
            break
        else:
            x -= 1
        
        if x == 0:
            lastExpression = value
            break
    
    return lastExpression

def checkClosingBracket(value,  t = "funcCheck"):
    s = ""

    delimiters = [0,0]
    if t == "funcCheck":
        delimiters = "()"
    else:
        delimiters = '[]'

    y = 0
    openedBracket = False
    for x in value:
        if x == delimiters[0]:
            y += 1
            openedBracket = True
        elif x == delimiters[1]:
            y -= 1
        
        s += x

        if y == 0 and openedBracket:
            break
        
    return s

def getVal(value):
    value = removeSpace(value)

    value = removeExtraBrackets(value)

    #check if string/char
    if value[0] == '"' or value[0] == 'ꞌ' or value[0] == "'":
        if value[-1] != "'" and value[-1] != '"' and value[-1] != 'ꞌ':
            errorHandle("Quotation marks not closed")
        else:
            value = value[1:len(value)-1]
    
    #check if int
    elif value.isnumeric() or (value[0] == "-" and value[1:].isnumeric()):
        value = int(value)

    #functions and library routines
    elif (value == checkClosingBracket(value) and value[-1] == ")" and not(True in [len(bracketExcludedSplit(value,m))>1 for m in list("+-*/^<>= ")+[f" {m} " for m in ["AND","OR","NOT"]]+[f"){m} " for m in ["AND","OR","NOT"]]+[f" {m}(" for m in ["AND","OR","NOT"]]] or value[:4]=="NOT " or value[:4]=="NOT(")):
        functionName = removeSpace(value.split("(")[0])
        #get calculated values
        values = value[firstSpecialChar(value)+1:len(value)-firstSpecialChar(value[::-1])-1]
        
        values = bracketExcludedSplit(values,",")
        backupVar = copy.deepcopy([removeExtraBrackets(x) for x in values])

        #quick expression evaluate for standard functions
        if functionName not in var:
            values = [getVal(x) for x in values]


        if functionName == "MOD":
            value = values[0]%values[1]
        
        elif functionName == "DIV":
            value = values[0] // values[1]

        elif functionName == "LENGTH":
            value = len(values[0])
        
        elif functionName == "LCASE":
            value = values[0].lower()
        
        elif functionName == "UCASE":
            value = values[0].upper()
        
        elif functionName == "SUBSTRING":
            value = values[0][values[1]-1:values[1]+values[2]-1]
        
        elif functionName == "ROUND":
            value = round(values[0],values[1])
        
        elif functionName == "RANDOM":
            value = random.random()

        elif functionName in var:
            #get parameters and code
            parameters = copy.deepcopy(var[functionName]['parameters'])
            functionCode = copy.deepcopy(var[functionName]['code'])
            localVariables = [x["name"] for x in parameters] + copy.deepcopy(var[functionName]["localVar"])
            flaggedVar = []

            if mutableParameters:
                #replace function code with pointed variables 
                for y in range(len(functionCode)):
                    for x in range(len(parameters)):
                        #check if array, variable or function
                        if not(False in [m.isalnum() for m in backupVar[x]]) or (backupVar[x] == checkClosingBracket(backupVar[x]) and backupVar[x][-1] == ")" and not(True in [len(bracketExcludedSplit(backupVar[x],m))>1 for m in list("+-*/^<>= ")+[f" {m} " for m in ["AND","OR","NOT"]]+[f"){m} " for m in ["AND","OR","NOT"]]+[f" {m}(" for m in ["AND","OR","NOT"]]] or backupVar[x][:4]=="NOT " or backupVar[x][:4]=="NOT(")) or (backupVar[x] == checkClosingBracket(backupVar[x],t="arrayCheck") and backupVar[x][-1] == "]"):
                            functionCode[y] = varReplace(functionCode[y],parameters[x]['name'],backupVar[x])
                            if backupVar[x] not in flaggedVar:
                                flaggedVar.append(backupVar[x])
            
            #remove all iterated values
            localVariables = [x for x in localVariables if x not in flaggedVar]

            if len(localVariables) > 0:
                #create new local variables
                for x in range(len(localVariables)):
                    flag = True
                    #change name of parameters
                    oldName = localVariables[x]
                    while localVariables[x] in var:
                        localVariables[x] += "q"
                        flag = False
                    
                    #check if name has been changed, and replaces changed name in code
                    if not flag:
                        for y in range(len(functionCode)):
                            functionCode[y] = varReplace(functionCode[y],oldName,localVariables[x])

                #stores variables in var
                for x in range(0,len(parameters)):
                    if localVariables[x] in [y['name'] for y in parameters]:
                        var[localVariables[x]] = {"type":parameters[x]["type"], "value":getVal(values[x])}
                
            #get code
            value = execCode(functionCode)

            #remove variables after execution
            for x in range(len(parameters)):
                if parameters[x]["name"] in var.keys():
                    del var[parameters[x]["name"]]
            
            
    #check if array
    elif value == checkClosingBracket(value,t="arrayCheck") and value[-1] == "]":
        #get first instance of brackets
        index = value[firstSpecialChar(value)+1:len(value)-firstSpecialChar(value[::-1])-1]
        index = bracketExcludedSplit(index,",")
        index = [getVal(x) for x in index]
        name = removeSpace(value.split("[")[0])
        
        #check if array exists
        if name not in var:
            errorHandle(f"{name} has not been declared yet")
        
        #check if variable is array
        if var[name]["type"] != "ARRAY":
            errorHandle(f"Cannot index {var[name]['type']} variables")

        #check if 2D or 1D - check if index matches
        if len(index) != len(var[name]['dimensions']):
            errorHandle(f"Array {name} dimensions do not match")

        #add value
        if len(index) == 1:
            #check if dimensions match
            if index[0] < var[name]["dimensions"][0][0] or index[0] > var[name]["dimensions"][0][1]:
                errorHandle("Cannot assign value outside valid range of array index")

            value = var[name]["value"][index[0]-var[name]["dimensions"][0][0]]

        elif len(index) == 2:
            #check if dimensions match
            for x in range(2):
                if index[x] < var[name]["dimensions"][x][0] or index[x] > var[name]["dimensions"][x][1]:
                    errorHandle("Cannot assign value outside valid range of array index")

            value = var[name]["value"][index[0]-var[name]["dimensions"][0][0]][index[1]-var[name]["dimensions"][1][0]]

    #check for operations
    elif True in [x in value for x in list('+-*/^<>=')+[" NOT "," AND "," OR ","(NOT "]] or value[:4] == "NOT ":
    #operations (add/mult/sub/div)
    #split it to variables / values
        valList = list(value)
        
        valList = "".join(valList)

        #check for arrays/functions
        valList = bracketExcludedSplit(valList, " ")        
        arrayFunc = [x for x in valList if ("(" in list(x[1:]) and x[x.index("(",1)-1].isalnum()) or len(x.split("[")) > 1]
        
        #check seperatey: 
        for x in arrayFunc:
            if "[" not in list(x):
                buffer = x.split("(")
                if not (True in [True for x in buffer if x[-1].isalnum()]):
                    arrayFunc.remove(x)

        valList = [x for x in valList if  not(x in arrayFunc)]

        valList = " ".join(valList)

        #get all variables / values
        for z in [" NOT "," AND "," OR "] + [x for x in '^/*+-'] + ["<>",">=","<=",">","<","="]+[f"){x} " for x in ["AND", "OR"]]+[f" {x}(" for x in ["AND", "OR"]]+[f"){x}(" for x in ["AND", "OR"]]:
            valList = valList.replace(z,"$")

        #special case for NOT at beginning
        if valList[:4] == "NOT$":
            valList = [x for x in valList]
            for x in range(3):
                valList.pop(0)

            valList = "".join(valList)

        elif valList[:5] == "(NOT$":
            valList = [x for x in valList]
            for x in range(3):
                valList.pop(1)

            valList[1] == "$"
            valList = "".join(valList)
        
        valList = valList.replace("(","$")
        valList = valList.replace(")","$")
        valList = valList.split("$")

        #get the valList values - is there variables / functions here?
        valList = list(set(valList))
        
        #remove the values which are not variables/functions
        oldValList = copy.deepcopy(valList)
        valList = [x for x in valList if x != "" and x[0] != "'" and x[0] != '"' and not x.isnumeric()]
        oldValList = [x for x in oldValList if x not in valList and x != ""]

        valList = valList + oldValList + arrayFunc
        valList = [[x, getVal(x)] for x in valList]

        #check if all values are int&float&bool or values are string&char
        valType = [getType(x[1]) for x in valList]
        if valType.count("INTEGER") + valType.count("REAL") + valType.count("BOOLEAN") != len(valType) and valType.count("STRING") + valType.count("CHAR") != len(valType):
            errorHandle("Values must be of same type for operations: (REAL, INTEGER & BOOLEAN) or (CHAR & STRING) values can be operated")
                
        #replace variables with values in statement
        for z in range(len(valList)):
            if valType[z] == "STRING":
                value = value.replace(valList[z][0],f'"{valList[z][1]}"')
            else:
                value = value.replace(valList[z][0],str(valList[z][1]))
        
        #change power sign
        value = value.replace("^","**")
        value = value.replace("<>","!=")
        value = value.replace(" AND "," and ")
        value = value.replace(" OR "," or ")
        value = value.replace(" NOT "," not ")
        value = value.replace("(NOT ", "(not ")

        if value[:4] == "NOT ":
            value = value.replace("NOT ", "not ",1)  

        value = [x for x in value]
        if "=" in value:
            for x in range(1,len(value)):
                if value[x] == "=" and value[x-1] not in ["<",">"]:
                    value[x] = "=="
        
        value = "".join(value)

        #get calculated value
        value = eval(value)
    
    #check if variable
    elif value in var:
        value = var[value]["value"]

    
    #check if boolean
    elif value == "TRUE":
        value = True
    elif value == "FALSE":
        value = False
    
    #check if real
    elif "." in value:
        value = float(value)
    
    #check if integer
    else:
        errorHandle(F"{value} is not a variable or recognizable valid value for a constant. Perhaps you missed an apostrophe?")
    
    #check if any value has been assigned
    if value == None:
        errorHandle("No value has been assigned to this variable/array index")
        
    return value

def getType(value):
    #string/char
    if type(value) is str:
        if len(value) == 1:
            return "CHAR"
        else:
            return "STRING"
        
    #boolean
    if type(value) is bool:
        return "BOOLEAN"
    
    #real
    elif type(value) is float:
        return "REAL"

    #integer
    elif type(value) is int:
        return "INTEGER"
    
    else:
        errorHandle("Value is not a valid type")

def store(name, value):
    global var
    #get calculated value
    varType = getType(removeSpace(value))
    name = removeSpace(name)
    value = removeSpace(value)

    #storing values in array
    if len(name.split("[")) == 2:
        if var[removeSpace(name.split("[")[0])]['type'] != "ARRAY":
            errorHandle(f"Cannot index {var[name]['type']} variables")

        index = removeSpace(removeSpace(name.split("[")[1]).split("]")[0])
        name = removeSpace(name.split("[")[0])

        #check if 2D or 1D - check if index matches
        if len(index.split(",")) != len(var[name]['dimensions']):
            errorHandle(f"Array {name} dimensions do not match")
        
        #get index
        index = [getVal(x) for x in index.split(",")]

        #check if type matches
        if var[name]["arrayType"] != varType and (var[name]["arrayType"] != "STRING" and varType == "CHAR"):
            errorHandle(f"Cannot assign {varType} value to {var[name]['arrayType']} ARRAY")

        #add value
        if len(index) == 1:
            #check if dimensions match
            if index[0] < var[name]["dimensions"][0][0] or index[0] > var[name]["dimensions"][0][1]:
                errorHandle("Cannot assign value outside valid range of array index")

            var[name]["value"][index[0]-var[name]["dimensions"][0][0]] = value

        elif len(index) == 2:
            #check if dimensions match
            for x in range(2):
                if index[x] < var[name]["dimensions"][x][0] or index[x] > var[name]["dimensions"][x][1]:
                    errorHandle("Cannot assign value outside valid range of array index")

            var[name]["value"][index[0]-var[name]["dimensions"][0][0]][index[1]-var[name]["dimensions"][1][0]] = value

    #check if variable exists
    elif name not in var:
        if autoDeclareVariables:
            execCode([f"DECLARE {name}:MUTABLE"])

    #check if constant
    elif var[name]["type"] == "CONSTANT":
        errorHandle("Cannot assign value to constant")

    #check if varType matches actual type of variable
    elif var[name]["type"] == varType:
        var[name]["value"] = value
    
    elif var[name]["type"] == "STRING":
        var[name]["value"] = str(value)
    
    elif var[name]["type"] == "INTEGER" and varType == "REAL":
        var[name]["value"] = int(value)

    elif var[name]["type"] == "REAL" and varType == "INTEGER":
        var[name]["value"] = float(value)

    #SC for one letter strings
    else:
        errorHandle(f"Cannot assign {varType} values to {var[name]['type']} variable")

def execCode(code):
    p = 0
    global var
    global codePointer
    global files

    skip = 0

    code = [x for x in code if removeSpace(x) != ""]

    while p < len(code):
        #change code pointer
        if code == codeOg:
            codePointer = p
        else:
            for x in range(codePointer,len(codeOg)):
                if codeOg[x].replace("    ","") == code[p]:
                    codePointer = x
                    break

        #remove whitespace
        code[p] = removeSpace(code[p])

        #declaring variables
        if code[p][:8] == "DECLARE ":
            #get variable name
            varName = removeSpace(code[p][8:].split(":")[0])
            varType = removeSpace(code[p][8:].split(":")[1])

            #check if variable alreadyexists
            if varName in var:
                errorHandle("Variable/Constant with name already exists: Variables/Constants are case-sensitive!")

            #check if valid type
            if varType in ["BOOLEAN","INTEGER","REAL","CHAR","STRING"] or (varType == "MUTABLE" and autoDeclareVariables):
                #assign value
                var[varName] = {"type":varType,"value":None}

            #array special values
            elif varType[:5] == "ARRAY":
                #get array dimensions and constrictions
                arrayDimensions = code[p].split("ARRAY")[1].split("[")[1].split("]")[0].split(",")
                arrayDimensions = [removeSpace(z).split(":") for z in arrayDimensions]
                arrayDimensions = [[getVal(z) for z in y] for y in arrayDimensions]

                #get array type
                arrayType = removeSpace(code[p].split("OF")[1])
                if arrayType not in ["BOOLEAN","INTEGER","REAL","CHAR","STRING"]:
                    errorHandle(f"{arrayType} is not a valid data type")

                var[varName] = {"type":"ARRAY","value":None,"dimensions":arrayDimensions,"arrayType":arrayType}

                if len(var[varName]["dimensions"]) == 1:
                    var[varName]["value"] = [None for z in range(0,arrayDimensions[0][1]-arrayDimensions[0][0]+1)]
                elif len(var[varName]["dimensions"]) == 2:
                    var[varName]["value"] = [[None for z in range(arrayDimensions[1][1]-arrayDimensions[1][0]+1)] for y in range(arrayDimensions[0][1]-arrayDimensions[0][0]+1)]
                else:
                    errorHandle("Array dimensions greater than 2; please check code again")

            else:
                errorHandle(f"{varType} is not a valid data type")

        #declaring constants
        elif code[p][:9] == "CONSTANT ":  
            #get constant name and value
            varName = removeSpace(code[p][9:].split(delimiter)[0])
            varValue = removeSpace(code[p][9:].split(delimiter)[1])

            #check if variable exists
            if varName in var:
                errorHandle("Variable/Constant with name already exists: Variables/Constants are case-sensitive!")
                break    

            #get calculated value
            varValue = getVal(varValue)

            #add constant
            var[varName] = {"type":"CONSTANT","value":varValue}
        
        #for loop
        elif code[p][:4] == "FOR ":
            #get code in for loop
            forLoopCode = code[p+1:]
            for x in range(len(forLoopCode)):
                if forLoopCode[x][:4] == "NEXT":
                    break

            forLoopCode = forLoopCode[:x]
            forLoopCode = [x[4:] for x in forLoopCode]

            #get range to loop code
            rangeLoop = [getVal(x) for x in code[p].split(delimiter)[1].split("TO")]
            
            #get looping variable and declare it
            loopVar = removeSpace(code[p].split(delimiter)[0].split("FOR")[1])

            var[loopVar] = {"type":"INTEGER","value":rangeLoop[0]}

            #execute loop
            for x in range(rangeLoop[0],rangeLoop[1]+1):
                var[loopVar]['value'] = x
                execCode(forLoopCode)

            #get range of p to skip
            skip = len(forLoopCode) + 2

        #repeat loop
        elif code[p] == "REPEAT":
            #find until part
            for x in range(p+1,len(code)):
                if code[x][:5] == "UNTIL":
                    break
            
            loopCode = code[p+1:x]
            loopCode = [x[4:] for x in loopCode if x != ""] #remove tabs

            condition = code[x].split("UNTIL ")[1]

            while True:
                execCode(loopCode)
                if getVal(condition):
                    break
            
            skip = x - p + 1

        #while loop
        elif code[p][:6] == "WHILE ":
            #find endwhile
            for x in range(p+1,len(code)):
                if code[x] == "ENDWHILE":
                    break
            
            loopCode = code[p+1:x]
            loopCode = [x[4:] for x in loopCode if x != ""] #remove tabs

            condition = code[p].split("WHILE ")[1].split(" DO")[0]

            while getVal(condition):
                execCode(loopCode)
            
            skip = x - p + 1

        #inputting values
        elif code[p][:6] == "INPUT ":
            #get input value
            inputValue = input()
            try:
                if inputValue.upper() != inputValue.lower():
                    inputValue = getVal(f'"{inputValue}"')
                else:
                    inputValue = getVal(inputValue)
                

            #exception is string
            except:
                inputValue = getVal(f'"{inputValue}"')
            
            #get variable name
            varName = removeSpace(code[p].split("INPUT")[1])

            #store value
            store(varName, inputValue)

        #output values
        elif code[p][:7] == "OUTPUT ":
            valueOutput = code[p].split("OUTPUT")[1]
            valueOutput = bracketExcludedSplit(valueOutput,",")

            valueOutput = [str(getVal(x)) for x in valueOutput]
            
            if noNewLineOutput:
                print("".join(valueOutput),end='')
            else:
                print("".join(valueOutput))

        #if statement
        elif code[p][:3] == "IF ":
            #get if code and else code
            elseCode = []
            y = None
            for x in range(p+2,len(code)):
                if code[x][4:] == "ELSE":
                    ifCode = code[p+2:x]
                    for y in range(x,len(code)):
                        if code[y] == "ENDIF":
                            break

                    elseCode = code[x+1:y]
                    break

                elif code[x] == "ENDIF":
                    ifCode = code[p+2:x]
                    break

            ifCode = [z[8:] for z in ifCode]
            elseCode = [z[8:] for z in elseCode]

            #execute if and else statement
            if getVal(code[p].split("IF")[1]):
                execCode(ifCode)
                
            elif elseCode != []:
                execCode(elseCode)

            if y == None:
                skip = x + 1 - p
            else:
                skip = y + 1 - p

        #case statement
        elif code[p][:5] == "CASE ":
            #get variable/array value to test on
            value = getVal(code[p].split(" OF ")[1])

            #get all combinations to test on
            for x in range(p,len(code)):
                if code[x] == "ENDCASE":
                    break

            testValues = code[p+1:x]
            skip = x - p + 1

            testValues = [x[4:] for x in testValues]

            testValues = [bracketExcludedSplit(x,":") for x in testValues]

            #get code executed for each value
            testCode = []
            
            for x in range(len(testValues)):
                if len(testValues[x]) == 2:
                    testCode.append([testValues[x][1]])
                elif testValues[x][0][:9] == "OTHERWISE":
                    testCode.append([testValues[x][0][9:]])
                else:
                    testCode[len(testCode)-1].append(testValues[x][0][4:])
            

            #get actual values
            testValues = [getVal(x[0]) for x in testValues if len(x) == 2]

            #check if values match
            executed = False
            for x in range(len(testValues)):
                if value == testValues[x]:
                    execCode(testCode[x])
                    break
            
            #run otherwise statement
            if not executed and len(testCode) == x + 2:
                execCode(testCode[x+1])

        #declaring procedures/functions
        elif code[p][:10] == "PROCEDURE " or code[p][:9] == "FUNCTION ":
            #get procedure name
            if code[p][:9] == "PROCEDURE":
                procedureName = code[p].split("PROCEDURE ")[1]
            else:
                procedureName = code[p].split("FUNCTION ")[1]

            #check for parameters
            if "(" in list(procedureName):
                parameters = removeSpace(procedureName.split("(")[1])
                parameters = bracketExcludedSplit(parameters,")")[0]
                parameters = bracketExcludedSplit(parameters,",")
                parameters = [x.split(":") for x in parameters]
            else:
                parameters = []

            procedureName = removeSpace(procedureName.split("(")[0])
            localVariables = []

            #get procedure code and skip length
            #also check any local variables declared and store their names
            for x in range(p+1,len(code)):
                if code[p][:9] == "PROCEDURE" and code[x] == "ENDPROCEDURE" or code[p][:8] == "FUNCTION" and code[x] == "ENDFUNCTION":
                    break
                
                elif code[x][:12] == "    DECLARE ":
                    varName = removeSpace(bracketExcludedSplit(code[x].split("DECLARE")[1],":")[0])
                    localVariables.append(varName)
            
            skip = x - p + 1

            procedureCode = code[p+1:x]
            procedureCode = [x[4:] for x in procedureCode]

            #store procedure/function and its code & parameters
            var[procedureName] = {"type":"PROCEDURE","value":None,"code":procedureCode,"parameters":[{"name":removeSpace(x[0]), "type":removeSpace(x[1])} for x in parameters],"localVar":localVariables}

            #add returnValueType if function
            #get return value type
            if code[p][:8] == "FUNCTION":
                returnType = code[p].split("RETURNS ")[1]
                var[procedureName]['returnType'] = removeSpace(returnType)
                var[procedureName]['type'] = "FUNCTION"

        #calling procedures
        elif code[p][:5] == "CALL ":
            #get procedure name and parameters & local variables (only temporaru values)
            procedureName = code[p].split("CALL ")[1].split("(")[0]
            parameters = copy.deepcopy(var[procedureName]["parameters"])
            procedureCode = copy.deepcopy(var[procedureName]["code"])
            localVariables = [x["name"] for x in parameters] + copy.deepcopy(var[procedureName]["localVar"])

            #get user values
            if len(parameters) > 0:
                #get user values
                userValues = code[p].split("(")[1]
                userValues = removeSpace(userValues)
                userValues = userValues[:len(userValues)-1]
                userValues = bracketExcludedSplit(userValues, ",")

            if not mutableParameters:
                #create new local variables
                for x in range(len(localVariables)):
                    flag = True
                    #change name of parameters
                    oldName = localVariables[x]
                    while localVariables[x] in var:
                        localVariables[x] += "q"
                        flag = False
                    
                    #check if name has been changed, and replaces changed name in code
                    if not flag:
                        for y in range(len(procedureCode)):
                            procedureCode[y] = varReplace(procedureCode[y],oldName,localVariables[x])
                    
                    #rename variable in parameter list
                        parameters[[x['name'] for x in parameters].index(oldName)]['name'] = localVariables[x]

                #stores variables in var
                for x in range(0,len(parameters)):
                    if localVariables[x] in [y['name'] for y in parameters]:
                        var[localVariables[x]] = {"type":parameters[x]["type"], "value":getVal(userValues[x])}
                
                execCode(procedureCode)

                #remove local variables
                for x in range(len(localVariables)):
                    del var[localVariables[x]]

            else: #if mutable parameters
                #replace parameter variables with global variables it refers to
                for y in range(len(procedureCode)):
                    for x in range(len(userValues)):
                        procedureCode[y] = varReplace(procedureCode[y],parameters[x]['name'],userValues[x])
                
                #run code
                execCode(procedureCode)
            
        #return value
        elif code[p][:7] == "RETURN ":
            value = code[p].split("RETURN ")[1]
            return getVal(value)

        #open file
        elif code[p][:9] == "OPENFILE ":
            fileName = code[p].split(" FOR ")
            readMode = removeSpace(code[p].split(" FOR ")[1])
            fileName = removeSpace(fileName[0].split("OPENFILE ")[1])

            if readMode == "READ":
                file = open(fileName, "r")
                contents = file.readlines()
                file.close()
            
            elif readMode == "WRITE":
                contents = []
                file = open(fileName,"w")
                file.close()
            
            files[fileName] = {"mode":readMode, "contents":contents, "accessIndex":0}

        #read line and store value / write line of text to file
        elif code[p][:9] == "READFILE " or code[p][:10] == "WRITEFILE ":
            #get file name and variable
            if code[p][:9] == "READFILE ":
                fileName = code[p].split("READFILE ")[1]
            else:
                fileName = code[p].split("WRITEFILE ")[1]

            fileName = bracketExcludedSplit(fileName,",")
            variableStore = fileName[1]
            fileName = fileName[0]


            #store value in variable if reading file
            if code[p][:9] == "READFILE ":
                store(variableStore, files[fileName]["contents"][files[fileName]["accessIndex"]])
                files[fileName]["accessIndex"] += 1 #increment access pointer of file
            else:
                files[fileName]["contents"].append(getVal(variableStore))

        #close file
        elif code[p][:10] == "CLOSEFILE ":
            #get file name
            fileName = removeSpace(code[p].split("CLOSEFILE ")[1])
            
            #checks if file opened for write and writes lines of text to file
            if files[fileName]["mode"] == "WRITE":
                file = open(fileName, "w")
                file.writelines(files[fileName]["contents"])
                file.close()

            #deletes file from files dictionary
            del files[fileName]

        #assigning values
        elif removeSpace(removeSpace(code[p].split(delimiter)[0]).split("[")[0]) in var:
            varName = removeSpace(code[p].split(delimiter)[0])
            varValue = code[p].split(delimiter)[1]

            #get calculated value
            varValue = getVal(varValue)
            store(varName,varValue)

        #error code if not comment
        else:
            errorHandle("Unrecognized statement")

        if skip > 0:
            p += skip
            skip = 0
        else:
            p += 1
        
        if error:
            break
       
execCode(codeOg)

if debug:
    print("debug variables:")
    print(var)

if displayTime:
    print()
    print(f"{((time.time() - timer)*1000)}ms")