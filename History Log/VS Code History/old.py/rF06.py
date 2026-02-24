import time
import random
import json
import copy

timer = time.time()
#open and read code file
cd = open("code.txt","r", encoding="utf-8")
cd = cd.readlines()
operators = {"all":list("+-*/^<>=")+[f" {m} " for m in ["AND","OR","NOT"]]+[f"){m} " for m in ["AND","OR","NOT"]]+[f" {m}(" for m in ["AND","OR","NOT"]]+[f"){m}(" for m in ["AND","OR","NOT"]]+[f" {m}(" for m in ["AND","OR","NOT"]+["(NOT ","(NOT("]],
        'bad':[f"){x} " for x in ["AND", "OR","NOT"]]+[f" {x}(" for x in ["AND", "OR","NOT"]]+[f"){x}(" for x in ["AND", "OR", "NOT"]]+["(NOT("],
        'good':[f") {x} " for x in ["AND", "OR","NOT"]]+[f" {x} (" for x in ["AND", "OR","NOT"]]+[f") {x} (" for x in ["AND", "OR", "NOT"]]+["(NOT ("],
        'andornotVar':[f"){x} " for x in ["AND", "OR","NOT"]]+[f" {x}(" for x in ["AND", "OR","NOT"]]+[f"){x}(" for x in ["AND", "OR", "NOT"]]+["(NOT "]+["(NOT ","(NOT("]+[f" {x} " for x in ["AND", "OR","NOT"]],
        'cmprs':[x for x in '^/*+-'] + ["<>",">=","<=",">","<","="]+[f" {x} " for x in ["AND","OR","NOT"]]}

var = {} #variable storing all variables declared in code
files = {} #variable with all list of files open

codeOg = [x[:len(x)-1] if x[-1] == "\n" else x for x in cd] #replace "\n" characters at end of string

cache = {'functionCalls':{}, 'arrayCalls':{}, 'evalCalls':{}}
cacheState = False

#remove blank lines, comments, replace some weird characters
for x in range(len(codeOg)):
    codeOg[x] = codeOg[x].split("//")[0]
    codeOg[x] = codeOg[x].replace("–","-")
    codeOg[x] = codeOg[x].replace("ꞌ","'")

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
    if value == "":
        return []

    temp = value.split(splitValue)

    if len(temp) == 1:
        return temp
    
    if splitValue[-1] == "(" or splitValue[0] == "(":
        temp = [temp[0]] + ["("+x for x in temp[1:]]
    
    if splitValue[0] == ")":
        temp = [x+")" for x in temp[:len(temp)-1]] + [temp[len(temp)-1]] 


    x = 1
    while x < len(temp) :
        if not(temp[x-1].count(")")-temp[x-1].count("(") == 0 and temp[x-1].count("[")-temp[x-1].count("]") == 0 and temp[x-1].count('"')%2 == 0 and temp[x-1].count("'")%2 == 0):
            temp[x-1] = temp[x-1] + splitValue + temp[x]
            temp.pop(x)
        else:
            x += 1

    return temp

def varReplace(value,originalValue,replaceValue):
    value = value.split(originalValue)
    if len(value) == 1:
        return value[0]

    x = 0
    while x < len(value) - 1:
        if (len(value[x]) >0 and value[x][-1].isalpha()) or (len(value[x+1]) > 0 and value[x+1][0].isalpha()) or value[x].count('"')%2!=0 or value[x].count('"')%2!=0 or value[x].count("'")%2!=0 or value[x].count("'")%2!=0:
            value[x] = value[x] + originalValue + value[x+1]
            value.pop(x+1)
        else:
            x += 1
        
    return replaceValue.join(value)

def errorHandle(errorText):
    global error
    print(F"ERROR: {errorText}")
    error = True
    print(codeOg[codePointer])
    quit()

def removeExtraBrackets(value):

    if type(value) is not str or len(value) == 0 or value[0] != "(" or value[-1] != ")":
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
        
        if not x.isalnum() and x not in delimiters and y == 0 and x != " ":
            s = ""
        else:
            s += x

        if y == 0 and openedBracket:
            break
    
    return s

def checkOperators(value):
    for m in operators['all']:
        if len(bracketExcludedSplit(value,m)) > 1:
            return True
    
    return False

def getVal(value,skipChecks=False):
    global operators
    global cacheState

    if not skipChecks:
        value = removeSpace(value)

        value = removeExtraBrackets(value)

    #check if int     #check if integer
    #check if variable
    if value in var:
        value = var[value]["value"]
    
    #check if boolean
    elif value == "TRUE":
        value = True
    elif value == "FALSE":
        value = False
    
    elif value.isnumeric() or (value[0] == "-" and value[1:].isnumeric()):
        value = int(value)

    #check if real
    elif "." in value and len(value.split(".")) == 2 and value.split(".")[0].isnumeric() and value.split(".")[1].isnumeric():
        value = float(value)

    #check if string/char
    elif value[0] in ['"', "'"] and value[-1] in ['"', "'"] and (value.count('"')==2 or value.count("'")==2):
        value = value[1:len(value)-1]

    #functions and library routines
    elif value in cache["functionCalls"].keys() or (value[-1] == ")" and value == checkClosingBracket(value)):
        if value in cache["functionCalls"].keys():
            functionName = cache["functionCalls"][value]["functionName"]
            values = cache["functionCalls"][value]["values"].copy()
            backupVar = cache["functionCalls"][value]["backupVar"].copy()

        else:
            functionName = removeSpace(value.split("(")[0])
            #get calculated values
            values = value[firstSpecialChar(value)+1:len(value)-firstSpecialChar(value[::-1])-1]
            
            values = bracketExcludedSplit(values,",")
            backupVar = [removeExtraBrackets(x) for x in values]

            if cacheState:
                cache["functionCalls"] = {value:{"functionName":functionName, 
                                                "values":values.copy(),
                                                "backupVar":backupVar.copy()}}

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

        elif functionName == "NOT":
            value = not(values[0])

        elif functionName in var:
            if value in cache["functionCalls"].keys() and "parameters" in cache["functionCalls"][value].keys():
                parameters = copy.deepcopy(cache["functionCalls"][value]["parameters"] )
                functionCode = cache["functionCalls"][value]["functionCode"].copy()
                localVariables = cache["functionCalls"][value]["localVariables"].copy()
                flaggedVar = cache["functionCalls"][value]["flaggedVar"].copy()
                deleteExcludedVariables = cache["functionCalls"][value]["deleteExcludedVariables"].copy()

                #stores variables in var
                for x in range(0,len(parameters)):
                    if localVariables[x] in [y['name'] for y in parameters]:
                        var[localVariables[x]] = {"type":parameters[x]["type"], "value":getVal(values[x])}

            else:
                #get parameters and code
                parameters = copy.deepcopy(var[functionName]['parameters'])
                functionCode = var[functionName]['code'].copy()
                localVariables = [x["name"] for x in parameters] + var[functionName]["localVar"].copy()
                flaggedVar = []

                #copy all variables to NOT delete because they were declared globally
                deleteExcludedVariables = [x for x in localVariables if x in var.keys()]

                if mutableParameters:
                    #replace function code with pointed variables
                    for y in range(len(functionCode)):
                        for x in range(len(parameters)):
                            #check if array, variable or function
                            if not(False in [m.isalnum() for m in backupVar[x]]) or (backupVar[x] == checkClosingBracket(backupVar[x]) and backupVar[x][-1] == ")" and not(True in [len(bracketExcludedSplit(backupVar[x],m))>1 for m in list("+-*/^<>= ")+[f" {m} " for m in ["AND","OR","NOT"]]+[f"){m} " for m in ["AND","OR","NOT"]]+[f" {m}(" for m in ["AND","OR","NOT"]]+[f"){m}(" for m in ["AND","OR","NOT"]]+[f" {m}(" for m in ["AND","OR","NOT"]]] or backupVar[x][:4]=="NOT " or backupVar[x][:5]==" NOT(")) or (backupVar[x] == checkClosingBracket(backupVar[x],t="arrayCheck") and backupVar[x][-1] == "]"):
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
                
                if cacheState:
                    cache["functionCalls"][value]["parameters"] = copy.deepcopy(parameters)
                    cache["functionCalls"][value]["functionCode"] = functionCode.copy()
                    cache["functionCalls"][value]["localVariables"] =   localVariables.copy()
                    cache["functionCalls"][value]["flaggedVar"] = flaggedVar.copy()
                    cache["functionCalls"][value]["deleteExcludedVariables"] = deleteExcludedVariables.copy()

            #get code
            value = execCode(functionCode)

            #remove variables after execution
            for x in range(len(parameters)):
                if parameters[x]["name"] in var.keys() and parameters[x]["name"] not in deleteExcludedVariables:
                    del var[parameters[x]["name"]]
            
    #check if array
    elif value[-1] == "]" and value == checkClosingBracket(value,t="arrayCheck"):
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
    elif value[:4]=="NOT " or checkOperators(value):
    #operations (add/mult/sub/div)
    #split it to variables / values
        valList = value

        #space out brackets
        bad = operators['bad']
        good = operators['good']
        for x in range(len(bad)):
            valList = valList.replace(bad[x],good[x])

        comparision = False #check if there is a comparing value
        ignoreTypeChecks = False
        concat = False

        #get all variables / values
        for z in operators['cmprs']:
            v = bracketExcludedSplit(valList,z)
            if len(v)>1:
                valList = "$".join(v)
                if z in ["<>",">=","<=",">","<"]:
                    comparision = True
                elif z in ["*"]:
                    ignoreTypeChecks = True
                elif z == "+":
                    concat = True
                    
        #special case for NOT at beginning
        if valList[:4] == "NOT ":
            valList = [x for x in valList]
            for x in range(3):
                valList.pop(0)
            
            valList[0] = "$"

            valList = "".join(valList)
        
        #only replace outer brackets
        valList = list(valList)

        inBracket = 0
        functionStart = False
        for x in range(len(valList)):
            if valList[x] in ["(","["]:
                if inBracket == 0:
                    if x > 0 and valList[x-1].isalnum():
                        functionStart = True
                    else:
                        valList[x] = "$"
                inBracket += 1
            
            elif valList[x] in [")","]"]:
                if inBracket == 1:
                    if functionStart:
                        functionStart = False
                    else:
                        valList[x] = "$"
                inBracket -= 1
            
        valList = "".join(valList)
        valList = valList.split("$")

        #get the valList values - is there variables / functions here?
        valList = list(set(valList))

        valList = [removeSpace(removeExtraBrackets(x)) for x in valList]
        
        #remove the values which are not variables/functions
        #remove integers,strings, and empty vakues
        valList = [x for x in valList if not(x.isnumeric() or removeSpace(x) == "") ]
        oldValList = valList.copy()
        valList = [x for x in valList if not(x[0] in ['"',"'"])]
        oldValList = [x for x in oldValList if x not in valList]

        valList = [[x, getVal(x,skipChecks=True)] for x in valList]


        #check if all values are int&float&bool or values are string&char
        valType = [getType(x[1]) for x in valList]
        if valType.count("INTEGER") + valType.count("REAL") + valType.count("BOOLEAN") != len(valType) and valType.count("STRING") + valType.count("CHAR") != len(valType):
            if not ignoreTypeChecks:
                errorHandle("Values must be of same type for operations: (REAL, INTEGER & BOOLEAN) or (CHAR & STRING) values can be operated")

        #exception for strings: gettig numerical values
        if comparision and valType.count("CHAR") == len(valType):
            oldValList = [[x,getVal(x)] for x in oldValList ]
            oldValList = [[x[0],ord(x[1])] if len(x[1])>=1 else [x[0],0] for x in oldValList]
            valList = oldValList + valList

        #sort values by length
        valList = sorted(valList, key=lambda x:len(x[0]),reverse=True)
        #replace variables with values in statement
        for z in range(len(valList)):
            if valType[z] == "CHAR" or valType[z] == "STRING":
                value = value.replace(valList[z][0],'"'+str(valList[z][1])+'"')
            else:
                value = value.replace(valList[z][0],str(valList[z][1]))
        
        
        #change power sign
        value = value.replace("^","**")
        value = value.replace("<>","!=")
        for x in operators['andornotVar']:
            value = value.replace(x,x.lower())

        if value[:4] == "NOT ":
            value = value.replace("NOT ", "not ",1)  

        value = [x for x in value]
        if "=" in value:
            for x in range(1,len(value)):
                if value[x] == "=" and value[x-1] not in ["<",">"]:
                    value[x] = "=="
        
        value = "".join(value)

        #exceptions for concatenation
        if concat and (valType.count("INTEGER") + valType.count("REAL") + valType.count("BOOLEAN") != len(valType) and valType.count("STRING") + valType.count("CHAR") != len(valType)):
            value = bracketExcludedSplit(value,"+")
            value = [getVal(x) for x in value]
            value = f'{"".join([str(x) for x in value])}'
            
        else:
            #get calculated value
            value = eval(value)


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
    if varType not in ["STRING","CHAR"]:
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
        if var[name]["arrayType"] != varType:
            if var[name]["arrayType"] == "INTEGER":
                value = int(value)
            elif var[name]["arrayType"] == "REAL":
                value = float(value)
            elif var[name]["arrayType"] == "BOOLEAN":
                var[name]["value"] = bool(value)

            elif var[name]["arrayType"]=="STRING" or var[name]["arrayType"]=="CHAR":
                value = str(value)
                if var[name]["arrayType"] == "CHAR" and len(value) > 1:
                    errorHandle(f"Cannot assign value with length > 1 for CHAR variable")

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

    elif var[name]["type"] == "CHAR":
        if len(str(value)) > 1:
            errorHandle("CHAR Variables cannot store strings with length > 1")
        else:
            var[name]["value"] = str(value)

    elif var[name]["type"] == "INTEGER" and varType == "REAL":
        var[name]["value"] = int(value)

    elif var[name]["type"] == "REAL" and varType == "INTEGER":
        var[name]["value"] = float(value)

    elif var[name]["type"] == "BOOLEAN":
        if type(value) is str and value.upper() == "TRUE":
            value = True
        elif type(value) is str and value.upper() == "FALSE":
            value = False

        var[name]["value"] = bool(value)

    #SC for one letter strings
    else:
        errorHandle(f"Cannot assign {varType} values to {var[name]['type']} variable")

def execCode(code):
    p = 0
    global var
    global codePointer
    global files
    global cacheState

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

            #get step for for loop code
            step = code[p].split(" STEP ")
            if len(step) > 1:
                step = getVal(step[1])
            else:
                step = 1

            #get range to loop code
            rangeLoop = [getVal(x) for x in code[p].split(delimiter)[1].split("STEP")[0].split("TO")]
            
            #get looping variable and declare it
            loopVar = removeSpace(code[p].split(delimiter)[0].split("FOR")[1])

            var[loopVar] = {"type":"INTEGER","value":rangeLoop[0]}

            #execute loop
            for x in range(rangeLoop[0],rangeLoop[1]+step,step):
                var[loopVar]['value'] = x
                cacheState = True
                execCode(forLoopCode)

            #get range of p to skip
            skip = len(forLoopCode) + 2
            
            if code == codeOg:
                for key in cacheState.keys():
                    cacheState[key] = {}

                cacheState = False

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
                parameters = parameters.split(') RETURNS ')[0]
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
            fileName = removeSpace(fileName[0].split("OPENFILE ")[1]).replace('"','')

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
            fileName = fileName[0].replace('"','')


            #store value in variable if reading file
            if code[p][:9] == "READFILE ":
                store(variableStore, files[fileName]["contents"][files[fileName]["accessIndex"]])
                files[fileName]["accessIndex"] += 1 #increment access pointer of file
            else:
                files[fileName]["contents"].append(getVal(variableStore))

        #close file
        elif code[p][:10] == "CLOSEFILE ":
            #get file name
            fileName = removeSpace(code[p].split("CLOSEFILE ")[1]).replace('"','')
            
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
    print(var)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
if displayTime:
    print()
    print(f"{((time.time() - timer)*1000)}ms")