import os
import time
import threading
import requests
from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)

TARGET_URL = "https://res.cinemacity.co.jp/TicketReserver/studio/program/3726/583377"
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
CHECK_INTERVAL = 1 # 15秒間隔

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def send_notification(msg):
    if not DISCORD_WEBHOOK_URL:
        print("[警告] DISCORD_WEBHOOK_URL が環境変数に設定されていません。")
        return
    try:
        payload = {"content": msg}
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"[エラー] Discord通知送信失敗: {e}")

def monitor_loop():
    print("==================================================")
    print("【Render】座席監視スレッドを開始しました（15秒間隔）")
    print(f"対象URL: {TARGET_URL}")
    print("==================================================")
    
    # 起動確認用テスト通知
    send_notification("✅ **【テスト通知】Renderで座席監視システムが正常に起動しました！**")

    check_count = 0

    while True:
        check_count += 1
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            response = requests.get(TARGET_URL, headers=HEADERS, timeout=10)
            status_code = response.status_code
            
            if status_code != 200:
                print(f"[{timestamp}] [#{check_count}] HTTPエラー (Status: {status_code})")
            else:
                soup = BeautifulSoup(response.text, "html.parser")
                
                # ① 'seat' クラスを持つ <a> タグをすべて検索
                all_seats = soup.find_all(lambda tag: tag.name == "a" and "seat" in tag.get("class", []))
                
                # ② <a> タグで見つからない場合、他のタグ（div等）も含めて予備検索
                if len(all_seats) == 0:
                    all_seats = soup.find_all(lambda tag: tag.get("class") and any("seat" in c for c in tag.get("class")))

                total_count = len(all_seats)
                reserved_seats = [s for s in all_seats if "reserved" in s.get("class", [])]
                available_seats = [s for s in all_seats if "reserved" not in s.get("class", [])]

                reserved_count = len(reserved_seats)
                available_count = len(available_seats)

                # ③ 検出結果のログ出力（判定項目）
                if total_count == 0:
                    print(f"[{timestamp}] [#{check_count}] ⚠️ 検出失敗: 座席要素が0件です。HTML構造変更またはアクセス制限の可能性があります。")
                else:
                    print(f"[{timestamp}] [#{check_count}] 検出成功 | 全座席: {total_count}席 / 予約済: {reserved_count}席 / 空席: {available_count}席")

                # ④ 空席検知時の通知処理
                if available_count > 0:
                    msg = (
                        f"🚨 **【シネマシティ】キャンセル空席検知！** 🚨\n"
                        f"現在 **{available_count} 席** の空きが出ました！（全{total_count}席中）\n"
                        f"予約URL: {TARGET_URL}"
                    )
                    send_notification(msg)
                    print(f"[{timestamp}] 📢 Discordへ空席通知を送信しました！")

        except Exception as e:
            print(f"[{timestamp}] [#{check_count}] 通信・解析例外エラー: {e}")
        
        time.sleep(CHECK_INTERVAL)

@app.route('/')
def home():
    return "Cinema City Monitor is Running!"

# バックグラウンドスレッドで監視を実行
threading.Thread(target=monitor_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)