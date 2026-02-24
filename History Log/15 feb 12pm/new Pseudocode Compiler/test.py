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

def varReplaceNew(value,originalValue,replaceValue):
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

v = varReplaceNew("world+'world+world'+world + world","world",'hello')
v = 0