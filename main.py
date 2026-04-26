import os
import subprocess
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ChatAction

BOT_TOKEN = os.getenv("8659260396:AAFAN2zmbfgTmZE-oVEQV0eWWw8HugxCEa0", "8659260396:AAFAN2zmbfgTmZE-oVEQV0eWWw8HugxCEa0")

FAST_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "concurrent_fragment_downloads": 16,
    "retries": 10,
    "fragment_retries": 10,
    "socket_timeout": 20,
    "http_chunk_size": 10485760,
}

# 🔥 START UI
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "▰▰▰▰▰▰▰▰▰▰\n"
        "💜⚡ ADMIN RAHMAN 𝗕𝗢𝗧 ⚡💜\n"
        "▰▰▰▰▰▰▰▰▰▰\n\n"
        "🌌 𝗡𝗘𝗢𝗡 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗𝗘𝗥\n\n"
        "🎬 YouTube + TikTok\n"
        "🎧 MP3 Audio\n"
        "🚀 Ultra Fast Mode\n"
        "🗜 Auto Compress\n\n"
        "📎 Paste your video link 👇"
    )

# 🔍 LINK HANDLER
async def link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    url = update.message.text.strip()

    if not ("youtube.com" in url or "youtu.be" in url or "tiktok.com" in url):
        await update.message.reply_text("❌ Send valid YouTube/TikTok link")
        return

    context.user_data["url"] = url
    msg = await update.message.reply_text("🔍 Loading video...")

    try:
        with yt_dlp.YoutubeDL(FAST_OPTS) as ydl:
            data = ydl.extract_info(url, download=False)

        title = data.get("title", "Video")
        thumbnail = data.get("thumbnail")

        # 💎 NEON BUTTON UI
        buttons = [
            [
                InlineKeyboardButton("💜 1080p Neon", callback_data="1080"),
                InlineKeyboardButton("⚡ 720p Turbo", callback_data="720")
            ],
            [
                InlineKeyboardButton("🔮 360p Lite", callback_data="360"),
                InlineKeyboardButton("🎧 MP3 Glow", callback_data="mp3")
            ]
        ]

        caption = (
            "▰▰▰▰▰▰▰▰▰▰\n"
            "💜🎥 𝗩𝗜𝗗𝗘𝗢 𝗥𝗘𝗔𝗗𝗬 🎥💜\n"
            "▰▰▰▰▰▰▰▰▰▰\n\n"
            f"📌 𝗧𝗶𝘁𝗹𝗲: {title}\n\n"
            "⚡ Choose quality below 👇"
        )

        await msg.delete()

        if thumbnail:
            await update.message.reply_photo(
                photo=thumbnail,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await update.message.reply_text(
                caption,
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    except:
        await msg.edit_text("❌ Error loading video")

# ⚙️ BUTTON HANDLER
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await context.bot.send_chat_action(chat_id=query.message.chat_id, action=ChatAction.UPLOAD_VIDEO)

    url = context.user_data.get("url")
    choice = query.data

    msg = await query.message.reply_text("🚀 Download starting...")

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
                }],
            }
        elif choice == "1080":
            ydl_opts = {**base_opts, "format": "bestvideo[height<=1080]+bestaudio/best"}
        elif choice == "720":
            ydl_opts = {**base_opts, "format": "bestvideo[height<=720]+bestaudio/best"}
        else:
            ydl_opts = {**base_opts, "format": "bestvideo[height<=360]+bestaudio/best"}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(data)

        # 🎧 AUDIO
        if choice == "mp3":
            file_path = file_path.replace(".webm", ".mp3").replace(".m4a", ".mp3")
            await msg.edit_text("📤 Sending audio...")
            with open(file_path, "rb") as audio:
                await query.message.reply_audio(audio=audio)

        # 🎬 VIDEO
        else:
            if os.path.getsize(file_path) > 45 * 1024 * 1024:
                compressed = file_path.replace(".mp4", "_compressed.mp4")
                await msg.edit_text("🗜 Compressing...")

                subprocess.run([
                    "ffmpeg","-y","-i",file_path,
                    "-vcodec","libx264","-crf","28",
                    "-preset","veryfast",
                    "-acodec","aac","-b:a","128k",
                    compressed
                ])

                os.remove(file_path)
                file_path = compressed

            await msg.edit_text("📤 Sending video...")
            with open(file_path, "rb") as video:
                await query.message.reply_video(video=video)

        os.remove(file_path)
        await msg.delete()

    except:
        await msg.edit_text("❌ Download failed")

# 🚀 RUN
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, link_handler))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🔥 Neon Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
