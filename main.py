import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("8659260396:AAFAN2zmbfgTmZE-oVEQV0eWWw8HugxCEa0", "8659260396:AAFAN2zmbfgTmZE-oVEQV0eWWw8HugxCEa0")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 *Video Downloader Bot*\n\n"
        "📥 Send YouTube or TikTok video link.\n"
        "⚡ I will download it for you.\n\n"
        "✅ *Supported:*\n"
        "• YouTube\n"
        "• TikTok\n\n"
        "🔗 Send your link now!",
        parse_mode="Markdown"
    )

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not ("youtube.com" in url or "youtu.be" in url or "tiktok.com" in url):
        await update.message.reply_text("❌ Valid YouTube/TikTok link পাঠাও")
        return

    msg = await update.message.reply_text("⏳ Download হচ্ছে...")

    try:
        os.makedirs("downloads", exist_ok=True)

        ydl_opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "format": "best[filesize<45M][ext=mp4]/best[ext=mp4]/best",
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        await msg.edit_text("📤 Telegram এ পাঠাচ্ছি...")

        with open(file_path, "rb") as video:
            await update.message.reply_video(video=video, caption="✅ Download Complete")

        os.remove(file_path)
        await msg.delete()

    except Exception as e:
        await msg.edit_text("❌ Download failed\n\n" + str(e)[:250])

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

    print("✅ Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
