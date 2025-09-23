import requests

TOKEN = "7953918660:AAFOsfFl569vVOp4rqFeIORvqOFE4FtyuAE"
WEBHOOK_URL = f"https://telegram-quotes-bot-6.onrender.com/{TOKEN}"

response = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}")
print(response.json())
