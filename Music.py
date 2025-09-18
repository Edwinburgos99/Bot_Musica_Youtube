import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from googleapiclient.discovery import build
import asyncio

# Cargar variables desde el archivo .env
load_dotenv("secretKeys.env")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Configurar cliente de YouTube
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY, cache_discovery=False)

# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Hola!, envíame el nombre de una canción para buscar en YouTube.")

def buscar_videos(query: str):
    req = youtube.search().list(
        part="snippet",
        q=query,
        maxResults=5,
        type="video"
    )
    res = req.execute()
    return [
        (
            item["snippet"]["title"],
            f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            item["snippet"]["thumbnails"]["high"]["url"]
        )
        for item in res["items"]
    ]

# ✅ Comando /buscar con miniatura + título + link
async def buscar_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        query = " ".join(context.args)
        results = await asyncio.to_thread(buscar_videos, query)

        if results:
            for title, url, thumb in results:
                botones = [[InlineKeyboardButton("🔗 Ver en YouTube", url=url)]]
                reply_markup = InlineKeyboardMarkup(botones)

                # Enviar portada + título + link
                await update.message.reply_photo(
                    photo=thumb,
                    caption=f"🎶 {title}\n{url}",
                    reply_markup=reply_markup
                )
        else:
            await update.message.reply_text("❌ No encontré resultados en YouTube.")
    else:
        await update.message.reply_text("⚠️ Debes escribir algo. Ejemplo:\n/buscar Shakira Waka Waka")

async def advertencia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.startswith("/"):
        return  # ignora comandos diferentes a /buscar o /start
    await update.message.reply_text("⚠️ Debes usar el comando:\n/buscar <nombre de la canción>")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buscar", buscar_cmd))

    # 🚫 Texto sin comando muestra advertencia
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, advertencia))

    app.run_polling()

if __name__ == "__main__":
    main()
