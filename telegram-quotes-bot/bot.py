from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai
import os

# === 1. Read tokens from environment variables ===
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_KEY"]

openai.api_key = OPENAI_API_KEY

# === 2. Start command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! 😊 Send me your mood in any language or even just emojis 😢😂💪, "
        "and I'll reply with a motivational quote in the same language."
    )

# === 3. Function to detect language ===
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
    language = response["choices"][0]["message"]["content"].strip()
    return language

# === 4. Function to correct typos in the same language ===
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
    corrected = response["choices"][0]["message"]["content"].strip()
    return corrected

# === 5. Handle user messages ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    # Step 1: Detect language
    language = await detect_language(user_text)

    # Step 2: Correct typos in the same language
    corrected_text = await correct_text(user_text, language)

    # Step 3: Generate motivational quote in the same language
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

# === 6. Main ===

# def main():
#     app = Application.builder().token(TELEGRAM_TOKEN).build()

#     app.add_handler(CommandHandler("start", start))
#     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

#     print("Bot is running...")
#     app.run_polling()

# if __name__ == "__main__":
#     main()
