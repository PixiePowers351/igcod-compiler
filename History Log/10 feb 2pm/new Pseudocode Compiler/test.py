def bracketExcludedSplit(value,splitValue):
    inBracket = value[:len(splitValue)-1].count("(")+value[:len(splitValue)-1].count("[")
    temp = []
    lastIndex = 0
    quotation = "~"

    if len(value.split(splitValue))>1:
        for x in range(len(value)-len(splitValue)+1):
            if value[x] in ['"',"'"]:
                if quotation == "~":
                    quotation = value[x]
                elif value[x] == quotation:
                    quotation = "~"
            
            if quotation != "~":
                continue

            if value[x:x+len(splitValue)] == splitValue and (inBracket == 0 or (splitValue[0] in ["(",")","[",""] and inBracket==1) or (splitValue[0] == ")" and splitValue[-1] == "(" and inBracket==1) or (inBracket == 2 and splitValue[0] == "(" and splitValue[-1] == "(")):
                temp.append(value[:x].replace("".join([x+splitValue for x in temp]),""))
                lastIndex = x + len(splitValue)

                if splitValue[0] in [")","]"]:
                    temp[len(temp)-1] = temp[len(temp)-1] + splitValue[0]

                if len(temp) > 1:
                    if (splitValue[-1] in ["(","["]):
                        temp[len(temp)-1] = splitValue[-1] + temp[len(temp)-1]
                    
                    if (splitValue[0] in ["(","["]):
                        temp[len(temp)-1] = splitValue[0] + temp[len(temp)-1]          

            if value[x+len(splitValue)-1] in ["(","["] and (len(splitValue) == 1 or x!=0):
                inBracket += 1

            if value[x] in [")","]"] and (len(splitValue) == 1 or x!=0):
                inBracket -= 1

    if len(temp) != 0:      
        temp.append(value[lastIndex:])

        if (splitValue[-1] in ["(","["]):
            temp[len(temp)-1] = splitValue[-1] + temp[len(temp)-1]
        
        if (splitValue[0] in ["(","["]):
            temp[len(temp)-1] = splitValue[0] + temp[len(temp)-1]
            
    elif len(value) > 0:
        temp = [value]

    return temp


