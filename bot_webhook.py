import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai

# === 1. Read tokens from environment variables ===
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_KEY"]
openai.api_key = OPENAI_API_KEY

# === 2. Flask app ===
app = Flask(__name__)
PORT = int(os.environ.get("PORT", 5000))

# === 3. Telegram bot logic ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! 😊 Send me your mood in any language or even just emojis 😢😂💪, "
        "and I'll reply with a motivational quote in the same language."
    )

async def detect_language(user_text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Detect the language of the input text and reply only with its name."},
            {"role": "user", "content": user_text}
        ]
    )
    return response["choices"][0]["message"]["content"].strip()

async def correct_text(user_text, language):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Correct the spelling and grammar of the text in {language} without changing its meaning."},
            {"role": "user", "content": user_text}
        ]
    )
    return response["choices"][0]["message"]["content"].strip()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    language = await detect_language(user_text)
    corrected_text = await correct_text(user_text, language)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Generate a short, uplifting motivational quote in the same language as the user ({language})."},
            {"role": "user", "content": f"User feels: {corrected_text}"}
        ]
    )
    quote = response["choices"][0]["message"]["content"].strip()
    await update.message.reply_text(quote)

# === 4. Telegram Application ===
application = Application.builder().token(TELEGRAM_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === 5. Webhook route ===
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

@app.route("/")
def index():
    return "Bot is running on Render!", 200

# === 6. Set webhook when Flask starts ===
@app.before_first_request
def activate_webhook():
    async def set_webhook():
        webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"
        await application.bot.set_webhook(webhook_url)
        print(f"Webhook set to: {webhook_url}")

    loop = asyncio.get_event_loop()
    loop.create_task(set_webhook())