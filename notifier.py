import requests


class TelegramNotifier:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        if not self.token or not self.chat_id:
            print("Warning: Telegram Token or Chat ID is missing.")
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_message(self, text, silent=False, remove_keyboard=False):
        if not self.token or not self.chat_id:
            print("Skip sending telegram: Token/ChatID missing")
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown",
            "disable_notification": silent,
        }
        if remove_keyboard:
            payload["reply_markup"] = {"remove_keyboard": True}
        try:
            response = requests.post(self.base_url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending telegram: {e}")
            return False
