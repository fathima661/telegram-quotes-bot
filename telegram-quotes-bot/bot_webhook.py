import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# --- Your bot logic here ---
async def start(update: Update, context):
    await update.message.reply_text("Hello! I am your bot running on Render 🚀")

async def handle_message(update: Update, context):
    user_text = update.message.text
    # Example: Echo back
    await update.message.reply_text(f"You said: {user_text}")
    # TODO: Replace with your OpenAI call logic if needed

# --- Flask app for webhook ---
app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")  # set in Render Dashboard
PORT = int(os.environ.get("PORT", 5000))

application = Application.builder().token(TOKEN).build()

# Register handlers (same as bot.py)
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


@app.route("/webhook", methods=["POST"])
def webhook():
    """Receive updates from Telegram and pass to Application"""
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200


@app.route("/")
def index():
    return "Bot is running on Render!", 200


if __name__ == "__main__":
    # Set webhook when app starts
    import asyncio

    async def set_webhook():
        webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"
        await application.bot.set_webhook(webhook_url)
        print(f"Webhook set to: {webhook_url}")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())

    # Start Flask app
    app.run(host="0.0.0.0", port=PORT)
