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
REPORT_INTERVAL_MIN = int(os.getenv("REPORT_INTERVAL_MIN", 2))
HF_THRESHOLD = float(os.getenv("HF_THRESHOLD", 1.1))
HF_CHECK_INTERVAL_MIN = int(os.getenv("HF_CHECK_INTERVAL_MIN", 1))

client = MonadMarketClient(RPC_URL)
notifier = TelegramNotifier(TOKEN, CHAT_ID)

# Tracks whether we've already fired the emergency alert for the current
# below-threshold streak, so we don't spam a message every check interval.
_hf_alert_active = False


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


def check_health():
    global _hf_alert_active

    if not WALLET:
        return

    try:
        hf = client.get_health_factor(WALLET)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] HF check: {hf:.4f}")

        if hf < HF_THRESHOLD and not _hf_alert_active:
            msg = (
                f"\U0001F6A8 *HEALTH FACTOR WARNING*\n"
                f"HF `{hf:.4f}` fell below threshold `{HF_THRESHOLD}`"
            )
            notifier.send_message(msg)
            _hf_alert_active = True
            print("Emergency HF alert sent!")
        elif hf >= HF_THRESHOLD and _hf_alert_active:
            notifier.send_message(
                f"✅ HF recovered to `{hf:.4f}` (above `{HF_THRESHOLD}`)"
            )
            _hf_alert_active = False
    except Exception as e:
        print(f"Error in check_health: {e}")


schedule.every(REPORT_INTERVAL_MIN).minutes.do(send_report)
schedule.every(HF_CHECK_INTERVAL_MIN).minutes.do(check_health)

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("--- Monad Market Noti Bot Started ---")
    print(f"Target Wallet: {WALLET}")
    print(f"Report Interval: {REPORT_INTERVAL_MIN} min")
    print(f"HF Threshold: {HF_THRESHOLD} (checked every {HF_CHECK_INTERVAL_MIN} min)")
    print("--------------------------------------")

    send_report()
    check_health()

    while True:
        schedule.run_pending()
        time.sleep(1)
