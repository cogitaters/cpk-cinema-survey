import os
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

def send_notification(msg):
    if not DISCORD_WEBHOOK_URL:
        print("WEBHOOK_URL未設定")
        return
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": msg}, timeout=10)
    except Exception as e:
        print(f"送信エラー: {e}")

def monitor_loop():
    print("監視スレッド開始")
    # 起動直後にDiscordへテスト通知を送る
    send_notification("✅ **【テスト通知】Renderで座席監視システムが正常に起動しました！**")
    
    while True:
        try:
            res = requests.get(TARGET_URL, headers=HEADERS, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            seats = soup.find_all("a", class_="seat")
            available = [s for s in seats if "reserved" not in s.get("class", [])]
            
            if len(available) > 0:
                msg = f"🚨 **【シネマシティ】キャンセル空席検知！** 🚨\n現在 **{len(available)} 席** の空きが出ました！\n予約URL: {TARGET_URL}"
                send_notification(msg)
                print(f"空席検知: {len(available)}席")
        except Exception as e:
            print(f"エラー: {e}")
        
        time.sleep(CHECK_INTERVAL)

@app.route('/')
def home():
    return "Cinema City Monitor is Running!"

threading.Thread(target=monitor_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)