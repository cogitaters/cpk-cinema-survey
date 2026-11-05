iimport os
import time
import threading
import requests
from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)

TARGET_URL = "https://res.cinemacity.co.jp/TicketReserver/studio/program/3726/583377"
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
CHECK_INTERVAL = 1

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def send_notification(message):
    if not DISCORD_WEBHOOK_URL:
        print("エラー: DISCORD_WEBHOOK_URL が設定されていません。")
        return
    try:
        payload = {"content": message}
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"通知送信エラー: {e}")

def monitor_loop():
    print("【Render】座席監視スレッドを開始しました（15秒間隔）")
    
    # 起動確認用のテスト通知を送信
    send_notification("✅ **【テスト通知】Renderで座席監視システムが正常に起動しました！**")

    while True:
        try:
            response = requests.get(TARGET_URL, headers=HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            seats = soup.find_all("a", class_="seat")
            available_seats = [s for s in seats if "reserved" not in s.get("class", [])]

            if len(available_seats) > 0:
                msg = f"🚨 **【シネマシティ】キャンセル空席検知！** 🚨\n現在 **{len(available_seats)} 席** の空きが出ました！\n予約URL: {TARGET_URL}"
                send_notification(msg)
                print(f"【空席検知】{len(available_seats)} 席の空きが出ました！")
        except Exception as e:
            print(f"監視一時エラー（自動復帰します）: {e}")
        
        time.sleep(CHECK_INTERVAL)

@app.route('/')
def home():
    return "Cinema City Monitor is Running!"

threading.Thread(target=monitor_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
