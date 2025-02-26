import requests
# import random


#wikipediaの記事のタイトルから検索をかけて存在したら説明を表示するAPI
def get_wikipedia_summary(title):
    # Wikipedia APIのURL
    url = "https://ja.wikipedia.org/w/api.php"
    
    # APIパラメータ
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "exintro": True,
        "explaintext": True,
        "titles": title
    }
    
    # リクエストを送信
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        # ページIDを取得
        pages = data.get("query", {}).get("pages", {})
        
        # ページの説明文を表示
        for page_id, page_data in pages.items():
            if "extract" in page_data:
                print(f"説明文: {page_data['extract']}\n\n")
                return page_data['extract']
            else:
                print("説明文が見つかりませんでした。")
    else:
        print("エラーが発生しました。")