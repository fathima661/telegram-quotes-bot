import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

webhook_url = "https://telegram-quotes-bot-6.onrender.com/webhook"

response = requests.get(
    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook",
    params={"url": webhook_url}
)

print(response.json())