import os
import time
import threading
import requests
from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)

TARGET_URL = "https://res.cinemacity.co.jp/TicketReserver/studio/program/3726/583377"
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
CHECK_INTERVAL = 1  # 15秒間隔

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
            response = requests.get(TARGET