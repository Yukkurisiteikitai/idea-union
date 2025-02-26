#Delete not need Object.
def deleteObjectStr(content:str):
    deletes = ["<",">","sys","SYS","INST","[","]","/","s>"]
    res = ""
    res = content
    for i in deletes:
        res = str(res).replace(i,"")
    return res