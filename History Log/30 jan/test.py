def bracketExcludedSplit(value,splitValue):
    inBracket = 0
    temp = []

    if splitValue in list(value):
        for x in range(len(value)):
            if value[x] == splitValue and inBracket == 0:
                temp.append(value[:x].replace("".join([x+splitValue for x in temp]),""))
            elif value[x] in ["(","[",'"']:
                if inBracket == 1 and value[x] == '"':
                    inBracket = 0
                else:
                    inBracket += 1
            elif value[x] in [")","]",'"']:
                inBracket -= 1

    if len(temp) != 0:      
        temp.append(value.replace("".join([x+splitValue for x in temp]),""))

    elif len(value) > 0:
        temp = [value]

    return temp

x = bracketExcludedSplit("HELLO (W!ORLD, "/"") / HE")