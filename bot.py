import os
import json
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Charger le dictionnaire
with open("bamananbot_dictionary_with_audio.json", "r", encoding="utf-8") as f:
    DICT = json.load(f)

API_TOKEN = os.environ.get("TELEGRAM_TOKEN")  # variable d'environnement sécurisée

# -------- Handlers Telegram --------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Envoie-moi un mot en français, par exemple : bonjour")

async def handle_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mot = update.message.text.strip().lower()
    entry = DICT.get(mot)

    if not entry:
        await update.message.reply_text("Je ne connais pas encore ce mot.")
        return

    bm = entry.get("bm", "")
    audio_path = entry.get("audio")

    await update.message.reply_text(f"{mot} → {bm}")

    if audio_path and os.path.exists(audio_path):
        with open(audio_path, "rb") as f:
            await update.message.reply_audio(f)

# -------- Application Telegram --------

def run_bot():
    app = ApplicationBuilder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_word))

    print("Bot lancé...")
    app.run_polling(close_loop=False)

# -------- Serveur web Flask --------

flask_app = Flask(__name__)

@flask_app.route("/")
def index():
    return "Bamananbot est en ligne."

if __name__ == "__main__":
    # Lancer le bot dans un thread séparé
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # Lancer le serveur web sur le port imposé par Render
    port = int(os.environ.get("PORT", 8000))
    print(f"Serveur Flask sur le port {port}...")
    flask_app.run(host="0.0.0.0", port=port)
