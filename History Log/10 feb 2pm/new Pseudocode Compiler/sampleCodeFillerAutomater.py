import subprocess
import os
import json
import shutil

def bracketExcludedSplit(value,splitValue):
    inBracket = 0
    temp = []

    if splitValue in list(value):
        for x in range(len(value)):
            if value[x] == splitValue and inBracket == 0:
                temp.append(value[:x].replace("".join([x+splitValue for x in temp]),""))
            elif value[x] in ["(","[",'"',"{"]:
                if inBracket == 1 and value[x] == '"':
                    inBracket = 0
                else:
                    inBracket += 1
            elif value[x] in [")","]",'"',"}"]:
                inBracket -= 1

    if len(temp) != 0:      
        temp.append(value.replace("".join([x+splitValue for x in temp]),""))

    elif len(value) > 0:
        temp = [value]

    return temp

def varReplace(value,originalValue,replaceValue):
    value = list(value)
    x = 0
    while x <= len(value)-len(originalValue):
        #check if value substring matches original value and: either its on the beginning of a line or the character before it is not an alphanumeric character and character after it is not an alphanumeric character
        if "".join(value[x:x+len(originalValue)]) == originalValue and (x == 0 or not value[x-1].isalpha()) and (x+1 > len(value)-len(originalValue) or not value[x+len(originalValue)].isalpha()) and (not value[x-1]=="'" and not value[x-1]=='"'):
            value[x:x+len(originalValue)] = replaceValue
            x += len(replaceValue) - 1
        
        x += 1

    return "".join(value)

#get codeFiles from folder
files = os.listdir("codeFiles")

#change settings in settings.json
settings = open("settings.json","r",encoding="utf-8")
settings = json.load(settings)

settings['debugMode']['value'] = 1
settings['displayTime']['value'] = 0

f = open('settings.json','w',encoding="utf-8")
json.dump(settings, f, indent=4, ensure_ascii=False)
f.close()

#samplecode list
sampleCode = []
files = files[files.index("1.010 2o25 validateEmail.txt"):]

for fileCode  in files:
    #open and transpose code to code.txt
    print(f"Running {fileCode}")
    fileName  = f"codeFiles/{fileCode}"
    code = open(fileName,"r",encoding="utf-8")
    code = code.readlines()

    codeFile = open("code.txt","w",encoding="utf-8")
    codeFile.writelines(code)
    codeFile.close()

    os.system('python ./decoder.py')
    input()