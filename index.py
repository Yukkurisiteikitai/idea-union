import csv
import random
import json
import time
import os
from datetime import datetime
from openai import AsyncOpenAI # AsyncOpenAIをインポート
import signal
import sys
import asyncio # asyncioをインポート

# --- 設定 ---
LMSTUDIO_BASE_URL = "http://localhost:1234/v1"
API_KEY = "lm-studio"
# model_name = "deepseek-r1-distill-qwen-32b" # 参考コードにあった他のモデル候補
# model_name = "qwen2.5-bakeneko-32b-instruct" # 参考コードにあった他のモデル候補
MODEL_NAME = "gemma-3-12b-it" # デフォルトはこちらを使用
CSV_FILENAME = "q.csv"
GOOD_SERVICE_FILENAME = "good-service.json"
ALL_IDEAS_FILENAME_PREFIX = "all_ideas_"
IDEAS_PER_CYCLE = 5
NUM_ELEMENTS_TO_COMBINE = 3

# --- 参考コードから取り込んだ詳細なシステムプロンプト ---
VISIONARY_DESIGNER_SYS_PROMPT = """
あなたは、社会課題の解決と未来の創造に情熱を燃やす**【ビジョナリー・サービスデザイナー】です。デザイン思考、人間中心設計、そして鋭い洞察力を武器に、まだ見ぬ価値を社会に実装することを使命としています。単なるアイデア出しに留まらず、そのアイデアがどのように社会に根付き、人々の生活や意識を変えていくか**までを構想します。
これからユーザーが「〇〇 × △△ × ◇◇」という形式で、異なる概念、技術、課題、文化、あるいは全く予期せぬ要素の組み合わせを提示します。それは、未来への可能性を秘めた「問い」です。
あなたはその「問い」を受け取り、以下の視点を盛り込みながら、社会実装を前提とした革新的で具体的なアイデアをデザインし、提案してください。

コンセプトの核心 (The Core Concept):
その組み合わせから生まれる**独自の価値（Unique Value Proposition）**は何か？
**誰の、どのような深いニーズや課題（ペインポイント/インサイト）**に応えるものか？（ターゲットユーザー像とその背景）
このアイデアが実現した**理想の未来像（Vision）**は？ 社会にどのようなポジティブな変化をもたらすか？

具体的な体験のデザイン (Experience Design):
ユーザーは**どのようにそのアイデアに出会い、触れ、どのような体験（ジャーニー）**をするのか？ 感動や驚き、利便性はどこにあるか？ (具体的な利用シーンやストーリー)
アイデアを形にするための主要な機能、サービスの流れ、必要なタッチポイントは？ (サービスブループリントの骨子)
**デザインの「らしさ」**はどこに宿るか？（世界観、トーン＆マナー、重要なUI/UX要素など）

社会実装へのロードマップ (Roadmap to Reality):
実現可能性はどうか？ 鍵となる技術、必要なリソース、協力すべきパートナーは？
持続可能性はあるか？ 考えられるビジネスモデルやマネタイズ、あるいは非営利での運営モデルは？
社会に受け入れられるための倫理的・文化的な配慮事項は？ 乗り越えるべき障壁は？
最初の小さな成功を生むための**第一歩（Minimum Viable Product / Prototype）**として何から始められるか？

あなたのデザイン提案における原則:
常に**【人間中心】**であること。
【サステナビリティ】（環境・社会・経済）への貢献を意識すること。
**【インクルーシブ】**であり、多様な人々が恩恵を受けられる可能性を考慮すること。
**【倫理的】**な観点を忘れないこと。
単なる機能だけでなく、**【感情的な価値】や【物語性】**を大切にすること。

さあ、ユーザーからの刺激的な「〇〇 × △△ × ◇◇」という問いを受け取り、あなたの発想力とデザインスキルを最大限に発揮して、未来を動かす魅力的なアイデアを具体的に描き出してください！ 余計な前置きや結びは最小限にし、上記の構造に沿ってアイデアを記述してください。
"""

# アイデア選定用のシステムプロンプト (こちらは変更しない)
SELECTION_SYS_PROMPT = "You are an experienced business analyst. Evaluate the presented service ideas and objectively select the best ones based on uniqueness, feasibility, and potential impact. Provide the selected service names and a brief reason for each."

# --- グローバル変数 ---
client = None
elements = []
running = True
main_task = None

# --- 関数定義 ---

def initialize_openai_client():
    """AsyncOpenAIクライアントを初期化する"""
    global client
    try:
        client = AsyncOpenAI(base_url=LMSTUDIO_BASE_URL, api_key=API_KEY)
        print(f"✅ AsyncOpenAIクライアントを初期化しました (接続先: {LMSTUDIO_BASE_URL})")
        print(f"   使用モデル: {MODEL_NAME}")
        return True
    except Exception as e:
        print(f"❌ AsyncOpenAIクライアントの初期化に失敗しました: {e}")
        return False

async def test_api_connection():
    """API接続を非同期でテストする"""
    if not client: return False
    try:
        await client.models.list()
        print(f"✅ LM Studio API ({LMSTUDIO_BASE_URL}) への接続成功。")
        return True
    except Exception as e:
        print(f"❌ LM Studio API ({LMSTUDIO_BASE_URL}) への接続に失敗しました: {e}")
        print(f"   エラー: {e}\n   LM Studioが起動しており、モデルがロードされているか確認してください。")
        return False

def load_elements_from_csv(filename):
    """CSVファイルから要素を読み込む"""
    global elements
    elements = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                elements.extend([item.strip() for item in row if item.strip()])
        if not elements:
            print(f"⚠️ 警告: {filename} が空か、有効な要素が含まれていません。"); return False
        if len(elements) < NUM_ELEMENTS_TO_COMBINE:
            print(f"❌ エラー: 要素数 ({len(elements)}) が組み合わせ ({NUM_ELEMENTS_TO_COMBINE}) に不足"); return False
        print(f"✅ {filename} から {len(elements)} 個の要素を読み込みました。"); return True
    except FileNotFoundError: print(f"❌ エラー: {filename} が見つかりません。"); return False
    except Exception as e: print(f"❌ {filename} 読込エラー: {e}"); return False

async def generate_service_idea(selected_elements, index):
    """AIにサービスアイデアを非同期で生成させる (詳細プロンプト使用)"""
    if not client: return None

    print(f"  🔄 アイデア {index+1} 生成開始 (要素: {', '.join(selected_elements)})")

    # ユーザープロンプト: 要素の組み合わせという「問い」を提示
    user_prompt = f"""
以下の要素の組み合わせについて、あなたの能力を発揮して革新的なサービスアイデアをデザインしてください:

要素の組み合わせ (問い):
{selected_elements[0]} × {selected_elements[1]} × {selected_elements[2]}

システムプロンプトで指示された項目（コンセプトの核心、具体的な体験のデザイン、社会実装へのロードマップなど）を含めて、詳細に記述してください。
"""

    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": VISIONARY_DESIGNER_SYS_PROMPT}, # 詳細なシステムプロンプトを使用
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7, # 詳細な指示があるので少し低めでも良いかも
            max_tokens=1500, # 詳細な出力を期待するため、トークン数を増やす
        )
        idea_text = response.choices[0].message.content.strip()

        # レスポンスのパースは簡略化: raw_textを主とし、簡単なキーワード抽出を試みる
        idea_data = {"elements": selected_elements, "raw_text": idea_text}
        # 簡単なサービス名の抽出を試みる（なければN/A）
        name_found = False
        for line in idea_text.split('\n'):
             # "サービス名:" や "コンセプト名:" のような行を探す
             if ("サービス名:" in line or "コンセプト名:" in line or "アイデア名:" in line) and ":" in line:
                 idea_data["service_name"] = line.split(":", 1)[1].strip().replace('*', '') # 簡単な整形
                 name_found = True
                 break
        if not name_found:
            # 見つからない場合、最初の非空行を仮のタイトルとするか、N/Aにする
            first_line = next((line for line in idea_text.split('\n') if line.strip()), None)
            idea_data["service_name"] = first_line if first_line else "N/A"


        print(f"     -> ✅ アイデア {index+1} 生成完了: {idea_data.get('service_name', 'N/A')}")
        return idea_data

    except Exception as e:
        print(f"❌ アイデア {index+1} の生成中にエラーが発生しました: {e}")
        # エラー発生時も、どの要素で失敗したか分かるように情報を返す
        return {"elements": selected_elements, "error": str(e), "raw_text": None, "service_name": "Generation Failed"}


async def select_best_ideas(ideas_list):
    """生成されたアイデアリストから良いものを非同期で選ぶ"""
    if not client: return []

    valid_ideas = [idea for idea in ideas_list if "error" not in idea and idea.get("raw_text")]
    if not valid_ideas:
        print("⚠️ 有効なアイデアがないため、ベストアイデアの選定をスキップします。")
        return []

    prompt = "以下のサービスアイデアのリストの中から、最もユニークで実現可能性があり、社会的インパクトの大きいと思われるアイデアを3つ選んでください。\n\n"
    for i, idea in enumerate(valid_ideas):
        prompt += f"--- アイデア {i+1} ---\n"
        # サービス名があれば表示、なければRaw Textの冒頭を表示
        service_name = idea.get('service_name', 'N/A')
        prompt += f"サービス名（または概要）: {service_name}\n"
        prompt += f"要素: {', '.join(idea.get('elements', []))}\n"
        # Raw Textの冒頭部分を追加情報として含める (長すぎないように)
        raw_text_snippet = idea.get('raw_text', '')[:300] # 最初の300文字程度
        prompt += f"アイデア詳細抜粋:\n{raw_text_snippet}...\n\n"


    prompt += """
選定結果として、選んだアイデアの番号（上記リストの番号）、サービス名（または概要）、そして選定理由（なぜそれが良いと思ったか）を、以下のような形式で3つ挙げてください。

1. アイデア番号: [番号]
   サービス名（または概要）: [サービス名または概要]
   選定理由: [簡単な理由]
2. ...
3. ...
"""

    print(f"\n🤖 {len(valid_ideas)}個の有効なアイデアからベストアイデアを選定中...")

    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME, # 選定にも同じモデルを使用
            messages=[
                {"role": "system", "content": SELECTION_SYS_PROMPT}, # 選定用システムプロンプト
                {"role": "user", "content": prompt}
            ],
            temperature=0.4, # 選定なので低めの温度設定
            max_tokens=500,
        )
        selection_text = response.choices[0].message.content.strip()
        print("\n--- AIによるベストアイデア選定結果 ---")
        print(selection_text)
        print("------------------------------------\n")

        # AIの選定結果テキストから、対応する元のアイデアデータを特定する (番号ベースで試みる)
        selected_ideas_data = []
        selected_indices = []
        try:
            lines = selection_text.split('\n')
            for line in lines:
                 if line.strip().startswith("アイデア番号:") or (line.strip().startswith(tuple(f"{i}." for i in range(1,4))) and "アイデア番号:" in line) : # 番号行を探す
                    try:
                        # "アイデア番号: 1" や "1. アイデア番号: 1" のような形式を想定
                        index_str = line.split(":")[-1].strip()
                        # 数字以外の文字を取り除く（例: "1." -> "1"）
                        index_str_cleaned = ''.join(filter(str.isdigit, index_str))
                        if index_str_cleaned:
                           idea_index = int(index_str_cleaned) - 1 # 0-based index
                           if 0 <= idea_index < len(valid_ideas):
                               selected_indices.append(idea_index)
                           else:
                                print(f"⚠️ 抽出されたアイデア番号が無効です: {idea_index + 1}")
                    except ValueError:
                        print(f"⚠️ アイデア番号の抽出に失敗しました: {line}")
                    except Exception as parse_err:
                        print(f"⚠️ アイデア番号パース中にエラー: {parse_err} (Line: {line})")

            # 重複を除き、最大3つまで選択
            selected_indices = sorted(list(set(selected_indices)))[:3]

            for index in selected_indices:
                 selected_ideas_data.append(valid_ideas[index])

        except Exception as e:
            print(f"❌ 選定結果のパース中にエラーが発生しました: {e}")


        # もし上記でうまく選べなかった場合、フォールバック
        if not selected_ideas_data and valid_ideas:
            print("⚠️ AIの選定結果からアイデアを特定できませんでした。代わりに最初の3つを選びます。")
            selected_ideas_data = valid_ideas[:3]

        # 選定理由をアイデアデータに追加（オプション）
        # ここでは省略。選定結果テキスト全体を別途保存することも考えられる。

        return selected_ideas_data

    except Exception as e:
        print(f"❌ AIによるベストアイデア選定中にエラーが発生しました: {e}")
        print("⚠️ ベストアイデアの選定に失敗したため、代わりに最初の3つのアイデアを選択します。")
        return valid_ideas[:min(len(valid_ideas), 3)]


def save_to_json(data, filename):
    """データをJSONファイルに保存する"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"💾 データを {filename} に保存しました。")
    except Exception as e:
        print(f"❌ {filename} への保存中にエラーが発生しました: {e}")

def signal_handler(sig, frame):
    """Ctrl+Cを受け取ったときの処理"""
    global running, main_task
    if running: # 最初のCtrl+Cでのみメッセージ表示
        print("\n🛑 終了シグナル受信。現在のタスク完了後に停止します...")
    running = False
    if main_task and not main_task.done():
        main_task.cancel()

async def main():
    """メインの非同期処理"""
    global running, elements, main_task

    if not initialize_openai_client(): return
    if not await test_api_connection(): return
    if not load_elements_from_csv(CSV_FILENAME): return

    cycle_count = 0
    while running:
        cycle_count += 1
        print(f"\n--- サイクル {cycle_count} 開始 ---")

        if len(elements) < NUM_ELEMENTS_TO_COMBINE:
             print(f"❌ エラー: 要素数不足({len(elements)} < {NUM_ELEMENTS_TO_COMBINE})"); break

        tasks = []
        print(f"  💡 {IDEAS_PER_CYCLE} 個のアイデア生成タスクを作成中...")
        selected_elements_list = []
        attempts = 0
        while len(tasks) < IDEAS_PER_CYCLE and attempts < IDEAS_PER_CYCLE * 5 and running:
             attempts += 1
             try:
                selected = random.sample(elements, NUM_ELEMENTS_TO_COMBINE)
                if selected not in selected_elements_list:
                     selected_elements_list.append(selected)
                     task = generate_service_idea(selected, len(tasks))
                     tasks.append(task)
             except ValueError: print(f"❌ 要素数不足({len(elements)} < {NUM_ELEMENTS_TO_COMBINE})"); running = False; break
             except Exception as e: print(f"❌ 要素選択エラー: {e}")

        if not running or not tasks:
             print("タスク作成失敗または中断。サイクルスキップ。"); continue

        print(f"  🚀 {len(tasks)} 個のアイデア生成タスクを並列実行...")
        current_cycle_ideas = []
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception): print(f"  ⚠️ タスク実行中例外: {result}")
                elif result: current_cycle_ideas.append(result)
        except asyncio.CancelledError: print("  タスクがキャンセルされました。"); break

        print(f"  🏁 {len(current_cycle_ideas)} 個のアイデア結果取得。")

        if not running: print("アイデア生成後に終了シグナル検出。"); break

        if current_cycle_ideas:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            all_ideas_filename = f"{ALL_IDEAS_FILENAME_PREFIX}{timestamp}.json"
            save_to_json(current_cycle_ideas, all_ideas_filename)

            best_ideas = await select_best_ideas(current_cycle_ideas)

            if best_ideas:
                save_to_json(best_ideas, GOOD_SERVICE_FILENAME)
            else:
                print("⚠️ ベストアイデア選定失敗 or 発見できず。good-service.json 未更新。")
        else:
            print("⚠️ このサイクルで有効なアイデアが生成/取得されませんでした。")

        if not running: break

        print(f"--- サイクル {cycle_count} 完了 ---")
        print(f"次のサイクルまで5秒待機... (Ctrl+Cで終了)")
        try:
            await asyncio.sleep(5)
        except asyncio.CancelledError: print("待機中にキャンセル。"); running = False; break

# --- メイン処理実行 ---
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    try:
        main_task = asyncio.ensure_future(main())
        asyncio.get_event_loop().run_until_complete(main_task)
    except asyncio.CancelledError:
        print("\n🚫 メインプロセスがキャンセルされ、終了します。")
    finally:
        # 必要であれば非同期クリーンアップ処理をここに追加
        print("\n👋 スクリプトを終了します。")
