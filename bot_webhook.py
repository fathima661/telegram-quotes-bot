import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import openai
import asyncio

# === 1. Read tokens from environment variables ===
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_KEY"]
openai.api_key = OPENAI_API_KEY

# === 2. Start command ===
async def start(update: Update, context):
    await update.message.reply_text(
        "Hello! 😊 Send me your mood in any language or even just emojis 😢😂💪, "
        "and I'll reply with a motivational quote in the same language."
    )

# === 3. Detect language ===
async def detect_language(user_text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a language detector. Detect the language of the input text. "
                           "Reply only with the language name (like English, Malayalam, Hindi, Spanish)."
            },
            {"role": "user", "content": user_text}
        ]
    )
    return response["choices"][0]["message"]["content"].strip()

# === 4. Correct typos in same language ===
async def correct_text(user_text, language):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a text corrector. Correct the spelling and grammar of the input text in {language}. "
                    "Do not change the meaning. Keep it in the same language."
                )
            },
            {"role": "user", "content": user_text}
        ]
    )
    return response["choices"][0]["message"]["content"].strip()

# === 5. Handle user messages ===
async def handle_message(update: Update, context):
    user_text = update.message.text
    language = await detect_language(user_text)
    corrected_text = await correct_text(user_text, language)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a motivational quote generator. You can understand emotions expressed in words or emojis. "
                    f"Reply in the same language as the user ({language}). Always give a short, uplifting quote."
                )
            },
            {"role": "user", "content": f"User feels: {corrected_text}. Give a motivational quote based on this."}
        ]
    )
    quote = response["choices"][0]["message"]["content"].strip()
    await update.message.reply_text(quote)

# === 6. Flask app for webhook ===
app = Flask(__name__)
PORT = int(os.environ.get("PORT", 5000))

# === 7. Telegram Application ===
application = Application.builder().token(TELEGRAM_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === 8. Webhook route ===
@app.route(f'/{TELEGRAM_TOKEN}', methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

# === 9. Default route ===
@app.route("/")
def index():
    return "Bot is running on Render!", 200

# === 10. Set webhook and run Flask app ===
if __name__ == "__main__":
    async def set_webhook():
        webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TELEGRAM_TOKEN}"
        await application.bot.set_webhook(webhook_url)
        print(f"Webhook set to: {webhook_url}")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())

    app.run(host="0.0.0.0", port=PORT)
