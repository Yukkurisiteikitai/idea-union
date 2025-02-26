import sys
import os
import random

# 現在のスクリプトのディレクトリを取得
current_dir = os.path.dirname(os.path.abspath(__file__))

# gironType のパスを追加
sys.path.append(os.path.join(current_dir, "gironType"))

#計測スタート
import time
all_do_start = time.time()

import gironType.earstProbe as earstProbe
from gironType.Toolfunction.Loadquestion import LoadSimgle
from gironType.Toolfunction.wikiAPI import get_wikipedia_summary
import sys



save_path = "./testPrompts/Log.jsonl"

themes_path = "./q.csv"
themes_list = LoadSimgle(themes_path)

def randWord():
    return themes_list[random.randint(0,len(themes_list)-1)]




def longIdea(count:int):
    temp = ""
    sentence = ""
    ideaWords = []
    
    
    # ideaWords
    for i in range(count):
        idea_temp = randWord()
        get_sentense = get_wikipedia_summary(idea_temp)
        print("fjioej;feajfawjfioew")
        print(get_sentense)
        print("oifejf;jawiofjeawio;fj")

        if get_sentense != None and get_sentense != "":
            sentence += f"'{idea_temp}':[{get_sentense}]\n"

        ideaWords.append(idea_temp)
        if i == 0:
            temp += idea_temp
        temp += "×" + idea_temp
    

    
    answer =  f"{temp}\n"
    if answer != "\n" and answer != None:
        answer += f"以下の文章は補足説明です。\n{sentence}"

    print("funtionBy",answer)
    return answer




def print_do_time(start_time,option):
    end_time=time.time()
    print(option+"かかった時間{:.2f}".format(end_time-start_time))



#Auto Test Mode

#Propaty
Lenght_objects = 2
items = 20

print(f"推定処理時間:{((40 * Lenght_objects) * items) /60} 分")


#議論の種
for t in range(items):
    themes = longIdea(Lenght_objects)
    answer = earstProbe.giron(themes=themes)
    print(answer)


all_do_end = time.time()
print("全ての演算に使用した時間:{:.2f}".format(all_do_end-all_do_start))