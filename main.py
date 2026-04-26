import os
import subprocess
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("8659260396:AAFAN2zmbfgTmZE-oVEQV0eWWw8HugxCEa0", "8659260396:AAFAN2zmbfgTmZE-oVEQV0eWWw8HugxCEa0")

FAST_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "concurrent_fragment_downloads": 8,
    "retries": 5,
    "fragment_retries": 5,
    "socket_timeout": 15,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 *Video Downloader Bot*\n\n"
        "📥 Send YouTube or TikTok video link.\n"
        "⚡ I will download it for you.\n\n"
        "✅ *Supported:*\n• YouTube\n• TikTok\n\n"
        "🔗 Send your link now!",
        parse_mode="Markdown"
    )

async def link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not ("youtube.com" in url or "youtu.be" in url or "tiktok.com" in url):
        await update.message.reply_text("❌ YouTube/TikTok link পাঠাও")
        return

    context.user_data["url"] = url
    msg = await update.message.reply_text("🔍 Video info loading...")

    try:
        with yt_dlp.YoutubeDL(FAST_OPTS) as ydl:
            data = ydl.extract_info(url, download=False)

        title = data.get("title", "Video")
        duration = data.get("duration", 0)
        thumbnail = data.get("thumbnail")

        buttons = [
            [InlineKeyboardButton("🎬 Best", callback_data="best"), InlineKeyboardButton("📺 1080p", callback_data="1080")],
            [InlineKeyboardButton("📺 720p", callback_data="720"), InlineKeyboardButton("📱 360p", callback_data="360")],
            [InlineKeyboardButton("🎵 MP3 Audio", callback_data="mp3"), InlineKeyboardButton("💾 Save Link", callback_data="save")],
            [InlineKeyboardButton("ℹ️ Info", callback_data="info"), InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
        ]

        caption = (
            f"✅ *Video Found!*\n\n"
            f"🎬 *Title:* {title}\n"
            f"⏱ *Duration:* {duration}s\n\n"
            f"👇 Choose download option:"
        )

        await msg.delete()

        if thumbnail:
            await update.message.reply_photo(photo=thumbnail, caption=caption, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await update.message.reply_text(caption, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))

    except Exception as e:
        await msg.edit_text("❌ Video info নিতে সমস্যা হয়েছে\n\n" + str(e)[:150])

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get("url")
    if not url:
        await query.message.reply_text("❌ আগে video link পাঠাও")
        return

    choice = query.data

    if choice == "cancel":
        await query.message.edit_text("❌ Menu closed")
        return

    if choice == "save":
        await query.message.reply_text("💾 Saved Link:\n" + url)
        return

    if choice == "info":
        try:
            with yt_dlp.YoutubeDL(FAST_OPTS) as ydl:
                data = ydl.extract_info(url, download=False)

            title = data.get("title", "N/A")
            duration = data.get("duration", 0)
            thumbnail = data.get("thumbnail")
            text = f"🎬 {title}\n⏱ Duration: {duration}s"

            if thumbnail:
                await query.message.reply_photo(photo=thumbnail, caption=text)
            else:
                await query.message.reply_text(text)
        except:
            await query.message.reply_text("❌ Info নিতে সমস্যা হয়েছে")
        return

    msg = await query.message.reply_text("⏳ Processing...")

    try:
        os.makedirs("downloads", exist_ok=True)

        base_opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "noplaylist": True,
            **FAST_OPTS
        }

        if choice == "mp3":
            ydl_opts = {
                **base_opts,
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }
        elif choice == "1080":
            ydl_opts = {
                **base_opts,
                "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best",
                "merge_output_format": "mp4",
            }
        elif choice == "720":
            ydl_opts = {
                **base_opts,
                "format": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best",
                "merge_output_format": "mp4",
            }
        elif choice == "360":
            ydl_opts = {
                **base_opts,
                "format": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best",
                "merge_output_format": "mp4",
            }
        else:
            ydl_opts = {
                **base_opts,
                "format": "best[ext=mp4]/best",
                "merge_output_format": "mp4",
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(data)

        if choice == "mp3":
            file_path = file_path.replace(".webm", ".mp3").replace(".m4a", ".mp3")
            await msg.edit_text("📤 Sending audio...")
            with open(file_path, "rb") as audio:
                await query.message.reply_audio(audio=audio, caption="🎵 MP3 Ready")
        else:
            if os.path.getsize(file_path) > 45 * 1024 * 1024:
                compressed_path = file_path.replace(".mp4", "_compressed.mp4")
                await msg.edit_text("🗜 File বড়, compress হচ্ছে...")

                subprocess.run([
                    "ffmpeg", "-y", "-i", file_path,
                    "-vcodec", "libx264", "-crf", "28",
                    "-preset", "veryfast",
                    "-acodec", "aac", "-b:a", "128k",
                    compressed_path
                ], check=True)

                os.remove(file_path)
                file_path = compressed_path

            await msg.edit_text("📤 Sending video...")
            with open(file_path, "rb") as video:
                await query.message.reply_video(video=video, caption="✅ Download Complete")

        os.remove(file_path)
        await msg.delete()

    except Exception as e:
        await msg.edit_text("❌ Download failed\n\n" + str(e)[:250])

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, link_handler))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("🔥 Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
