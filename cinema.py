import os
import requests
from bs4 import BeautifulSoup

TARGET_URL = "https://res.cinemacity.co.jp/TicketReserver/studio/program/3726/583377"
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def check_seats():
    try:
        response = requests.get(TARGET_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 空席の判定
        seats = soup.find_all("a", class_="seat")
        available_seats = [s for s in seats if "reserved" not in s.get("class", [])]

        if len(available_seats) > 0:
            send_notification(len(available_seats))
            print(f"【検知】空席が {len(available_seats)} 席見つかりました！")
        else:
            print("現在満席です。")
    except Exception as e:
        print(f"エラー発生: {e}")

def send_notification(seat_count):
    payload = {
        "content": (
            f"🚨 **【シネマシティ】キャンセル空席検知！** 🚨\n"
            f"現在 **{seat_count} 席** の空きが出ました！\n"
            f"予約URL: {TARGET_URL}"
        )
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    check_seats()
