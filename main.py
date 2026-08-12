import os
import sys
import time
import schedule
from dotenv import load_dotenv
from monad_client import MonadMarketClient
from notifier import TelegramNotifier
from formatter import format_dashboard

load_dotenv()

RPC_URL = os.getenv("RPC_URL", "https://rpc.monad.xyz")
WALLET = os.getenv("WALLET_ADDRESS")
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
REPORT_INTERVAL_MIN = int(os.getenv("REPORT_INTERVAL_MIN", 10))

client = MonadMarketClient(RPC_URL)
notifier = TelegramNotifier(TOKEN, CHAT_ID)


def send_report():
    if not WALLET:
        print("Error: WALLET_ADDRESS is not set.")
        return

    try:
        data = client.get_dashboard(WALLET)
        msg = format_dashboard(data)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
              f"NW ${data['net_worth_usd']:,.2f}  HF {data['health_factor']:.2f}")
        notifier.send_message(msg)
    except Exception as e:
        print(f"Error in send_report: {e}")


schedule.every(REPORT_INTERVAL_MIN).minutes.do(send_report)

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("--- Monad Market Noti Bot Started ---")
    print(f"Target Wallet: {WALLET}")
    print(f"Report Interval: {REPORT_INTERVAL_MIN} min")
    print("--------------------------------------")

    send_report()

    while True:
        schedule.run_pending()
        time.sleep(1)
