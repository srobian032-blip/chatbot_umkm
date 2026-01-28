import logging
import asyncio 
from dotenv import load_dotenv# Penting untuk mengatasi bug Python 3.14 jika masih ada
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from core import get_bot_reply 

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Kami dari robi printing. Ada yang bisa dibantu?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    # Mengambil jawaban dari file core.py yang terhubung ke json
    response = get_bot_reply(user_text) 
    await update.message.reply_text(response)

load_dotenv()
TOKEN = os.getenv("TOKEN")
    
# Membangun aplikasi
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler('start', start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

print("--- Bot Siap Digunakan ---")
    
# Gunakan run_polling standar
app.run_polling()