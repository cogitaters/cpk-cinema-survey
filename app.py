import time
import requests
import datetime
from bs4 import BeautifulSoup

TARGET_URL = "https://res.cinemacity.co.jp/TicketReserver/studio/program/3726/583377"
# ご自身の Discord Webhook URL に書き換えてください
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1566122855891206186/RzfJUrWe8SKFietuLdPWV00v4A9zKm_poaRhw3SpmCYeCTd97SyOrMUL8iLFX4DjlU-y"
CHECK_INTERVAL = 1# 安全な15秒間隔

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def log_to_file(message):
    """スマホ内にログを保存してバックグラウンド動作を証明する関数"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{now}] {message}\n"
    print(log_entry.strip())
    try:
        with open("monitor.log", "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception:
        pass

def check_seats():
    try:
        response = requests.get(TARGET_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        seats = soup.find_all("a", class_="seat")
        available_seats = [s for s in seats if "reserved" not in s.get("class", [])]

        if len(available_seats) > 0:
            send_notification(len(available_seats))
            log_to_file(f"【空席検知】{len(available_seats)} 席の空きが出ました！")
        else:
            # 20回（約5分）ごとにログファイルへ追記
            global check_count
            check_count += 1
            if check_count % 600 == 0:
                log_to_file(f"監視継続中...（累計: {check_count} 回）")
    except Exception as e:
        log_to_file(f"一時的な取得エラー: {e}")

def send_notification(seat_count):
    try:
        payload = {
            "content": (
                f"🚨 **【シネマシティ】キャンセル空席検知！** 🚨\n"
                f"現在 **{seat_count} 席** の空きが出ました！\n"
                f"予約URL: {TARGET_URL}"
            )
        }
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        log_to_file(f"通知送信エラー: {e}")

if __name__ == "__main__":
    check_count = 0
    log_to_file("座席監視を開始しました（15秒間隔・ログ保存モード）")
    while True:
        try:
            check_seats()
        except Exception as e:
            log_to_file(f"予期せぬエラー保護: {e}")
        time.sleep(CHECK_INTERVAL)
