import json

with open("log/log.jsonl","r",encoding="utf-8")as f:
    data = [json.loads(i) for i in f]

# print(data)
for i in range(len(data)):
    print(f"{i}版:{data[i]['messages'][2]['answer']}")