def bracketExcludedSplit(value,splitValue):
    inBracket = value[:len(splitValue)].count("(")+value[:len(splitValue)].count("[")-(value[:len(splitValue)].count(")")+value[:len(splitValue)].count("]"))
    temp = []

    if len(value.split(splitValue))>1:
        for x in range(len(value)-len(splitValue)+1):
            if value[x:x+len(splitValue)] == splitValue and (inBracket == 0 or (splitValue[0] == ")" and inBracket==1)):
                temp.append(value[:x].replace("".join([x+splitValue for x in temp]),""))

            if value[x+len(splitValue)-1] in ["(","["]:
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

def detectType(value):
    if not(False in [x.isalnum() for x in value.split("[")[0]]) and value[-1] == "]":
        return "array"
    elif not(False in [x.isalnum() for x in value.split("(")[0]]) and value[-1] == ")" and not(True in [len(bracketExcludedSplit(value,m))>1 for m in list("+-*/^<>= ")+[f" {m} " for m in ["AND","OR","NOT"]]+[f"){m} " for m in ["AND","OR","NOT"]]+[f" {m}(" for m in ["AND","OR","NOT"]]+[f"){m}(" for m in ["AND","OR","NOT"]]+[f" {m}(" for m in ["AND","OR","NOT"]]] or value[:4]=="NOT " or value[:5]==" NOT("):
        return "function"
    elif (True in [len(value.split(m))>1 for m in list("+-*/^<>= ")+[f" {m} " for m in ["AND","OR","NOT"]]+[f"){m} " for m in ["AND","OR","NOT"]]+[f" {m}(" for m in ["AND","OR","NOT"]]+[f"){m}(" for m in ["AND","OR","NOT"]]+[f" {m}(" for m in ["AND","OR","NOT"]+["(NOT ","(NOT("]]] or value[:4]=="NOT " or value[:5]==" NOT("):
        return "expression"
    else:
        return None

bracketExcludedSplit('(NOT 9=9 OR(5=4)'," OR(")