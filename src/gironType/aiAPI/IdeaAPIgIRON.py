import openai

openai.api_base = "http://localhost:1234/v1"  # LM Studio の API エンドポイント
openai.api_key = "lm-studio"  # APIキーは空欄でOK

converty = []  # 会話履歴を保持するため、ループの外で定義
sysPrompt = ""
model_name = "deepseek-r1-distill-qwen-32b"

save_data = []
save_path = "./log/giron.jsonl"

def SetSystemPrompt(context):
    global sysPrompt,converty
    sysPrompt = context
    converty = []
    converty.append({"role": "user", "content": sysPrompt})

def AddSaveDataInfo(systemPrompt:str,qestion:str,answer:str):
    return    {
        "messages":[
            {'SystemPrompt":"'+''+systemPrompt},
            {'question":"'+qestion},
            {'answer":"'+answer}
        ]
    }


response_temp =""
def Outputs_custom(question):
    global converty
    converty = [{"role": "user", "content": question}]  # "user" の発言を追加

    try:
        completion = openai.ChatCompletion.create(
            model=model_name,  # LM Studio で動作しているモデル名
            messages=converty
        )

        answer = completion.choices[0].message.content
        converty.append({"role": "assistant", "content": answer})  # スペル修正済み

        response_temp = str(answer).replace('"','**')
        save = AddSaveDataInfo(sysPrompt, question, response_temp)

        save_data.append(str(save).replace("'", '"'))

        return answer

    except Exception as e:
        print("Error:", e)




def Reset():
    global sysPrompt
    converty = []
    converty.append({"role": "user", "content": sysPrompt})

def PromptSave():
    global save_data,save_path
    if save_data == []:
        print("[NotingSaveData]")
    else:
        with open(save_path,"a",encoding="utf8")as file:
            file.writelines(f"{line}\n" for line in save_data)
        print("[Success Save]")
        save_data = []
    # save_data = []
# q = ""

# while True:
#     q = input("q:")
#     ask(q)


def test():
    print(Outputs_custom(question="helloworl"))

# test()