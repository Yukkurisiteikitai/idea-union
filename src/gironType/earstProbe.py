import time
import aiAPI.IdeaAPIgIRON as IdeaAPIgIRON
from Toolfunction.deleteObject import deleteObjectStr
from Toolfunction.TextConverter import ListChangeText
from Toolfunction.Loadquestion import LoadQuestion


#Propaty
themes = ""

# 質問の設定
conversation_history = []
SystemPrompt = "あなたは発想豊かなデザイナーです。×で組み合わせられたこれから来るUserの質問に対してあなたはこれをアイデアとして社会実装する場合を想定してデザインをしてください。"

#時間計測
def print_do_time(start_time,option):
    end_time=time.time()
    print(option+"かかった時間{:.2f}".format(end_time-start_time))



def giron(themes):
    IdeaAPIgIRON.SetSystemPrompt(SystemPrompt)
    output = deleteObjectStr(IdeaAPIgIRON.Outputs_custom(themes))
    IdeaAPIgIRON.PromptSave()
    IdeaAPIgIRON.Reset()
    return output