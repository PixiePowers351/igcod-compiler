import subprocess

#get codeFiles from folder
start = 1
end = 2

for fileCode  in range(start,end+1):
    #open and transpose code to code.txt
    fileName  = f"codeFiles/{fileCode}.txt"
    code = open(fileName,"r",encoding="utf-8")
    code = code.readlines()

    codeFile = open("code.txt","w",encoding="utf-8")
    codeFile.writelines(code)
    codeFile.close()

    result = subprocess.run(['python', 'decoder.py'], capture_output=True, text=True, check=True)

    #check for terminal errors / output
    output = result.stdout

    ""