import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("8659260396:AAFAN2zmbfgTmZE-oVEQV0eWWw8HugxCEa0", "8659260396:AAFAN2zmbfgTmZE-oVEQV0eWWw8HugxCEa0")
FAST_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "concurrent_fragment_downloads": 16,
    "retries": 10,
    "fragment_retries": 10,
    "socket_timeout": 20,
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("💜 Initializing...")

    for t in ["💜 Initializing.", "💜 Initializing..", "💜 Initializing..."]:
        await asyncio.sleep(0.4)
        await msg.edit_text(t)

    await msg.edit_text(
        "╔══════════════════════════════╗\n"
        "║ 💜✨ 𝗔𝗗𝗠𝗜𝗡 𝗥𝗔𝗛𝗠𝗔𝗡 𝗕𝗢𝗧 ✨💜 ║\n"
        "╠══════════════════════════════╣\n"
        "║ 🌌 𝗡𝗘𝗢𝗡 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗𝗘𝗥        ║\n"
        "║ 🎬 YouTube • TikTok         ║\n"
        "║ 🎧 MP3 • HD Video          ║\n"
        "║ 🚀 Ultra Fast Engine       ║\n"
        "╚══════════════════════════════╝\n\n"
        "💜 Send your video link 👇"
    )

async def link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not ("youtube.com" in url or "youtu.be" in url or "tiktok.com" in url):
        await update.message.reply_text("❌ Valid YouTube/TikTok link পাঠাও")
        return

    context.user_data["url"] = url

    msg = await update.message.reply_text("💜 Scanning...")
    for t in ["💜 Scanning.", "💜 Scanning..", "💜 Scanning..."]:
        await asyncio.sleep(0.4)
        await msg.edit_text(t)

    try:
        with yt_dlp.YoutubeDL(FAST_OPTS) as ydl:
            data = ydl.extract_info(url, download=False)

        title = data.get("title", "Unknown")
        duration = data.get("duration", 0)
        thumbnail = data.get("thumbnail")

        m = duration // 60
        s = duration % 60

        buttons = [
            [
                InlineKeyboardButton("💜 1080p", callback_data="1080"),
                InlineKeyboardButton("⚡ 720p", callback_data="720")
            ],
            [
                InlineKeyboardButton("🔮 360p", callback_data="360"),
                InlineKeyboardButton("🎧 MP3", callback_data="mp3")
            ]
        ]

        caption = (
            "╭━━━━〔 💜 𝗡𝗘𝗢𝗡 𝗣𝗥𝗘𝗩𝗜𝗘𝗪 💜 〕━━━━╮\n"
            f"🎬 {title[:40]}\n"
            f"⏱ {m}:{s:02d}\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
            "⚡ Choose format 👇"
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

    except Exception as e:
        await msg.edit_text("❌ Failed to load preview\n\n" + str(e)[:150])

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    url = context.user_data.get("url")
    choice = q.data

    msg = await q.message.reply_text("🚀 Starting download...")

    progress_steps = [
        "📥 Downloading... 10%\n🟪⬛⬛⬛⬛⬛⬛⬛⬛⬛",
        "📥 Downloading... 30%\n🟪🟪🟪⬛⬛⬛⬛⬛⬛⬛",
        "📥 Downloading... 50%\n🟪🟪🟪🟪🟪⬛⬛⬛⬛⬛",
        "📥 Downloading... 70%\n🟪🟪🟪🟪🟪🟪🟪⬛⬛⬛",
        "📥 Downloading... 90%\n🟪🟪🟪🟪🟪🟪🟪🟪🟪⬛",
        "📥 Downloading... 100%\n🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪"
    ]

    for step in progress_steps:
        await asyncio.sleep(0.4)
        await msg.edit_text(step)

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
            file = ydl.prepare_filename(data)

    await msg.edit_text(
    "╭━━━〔 🔊 𝗣𝗥𝗘𝗣𝗔𝗥𝗜𝗡𝗚 〕━━━╮\n"
    "┃ ▰▰▰▰▱▱▱▱▱▱ 40%\n"
    "┃ 🎶 Encoding media...\n"
    "┃ ⚡ Finalizing file...\n"
    "╰━━━━━━━━━━━━━━━━━━━━╯"
)
await asyncio.sleep(1)

await msg.edit_text(
    "╭━━━〔 📤 𝗦𝗘𝗡𝗗𝗜𝗡𝗚 〕━━━╮\n"
    "┃ ▰▰▰▰▰▰▰▰▱▱ 80%\n"
    "┃ 💜 Uploading to Telegram...\n"
    "┃ ⏳ Please wait...\n"
    "╰━━━━━━━━━━━━━━━━━━━━╯"
)
        if choice == "mp3":
            file = file.replace(".webm", ".mp3").replace(".m4a", ".mp3")
            with open(file, "rb") as f:
                await q.message.reply_audio(
                    audio=f,
                    caption=(
                        "╭━━━〔 🎧 𝗔𝗨𝗗𝗜𝗢 𝗥𝗘𝗔𝗗𝗬 〕━━━╮\n"
                        "┃ 💜 Powered by ADMIN RAHMAN BOT\n"
                        "┃ 🎵 Your MP3 is ready\n"
                        "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
                    )
                )
        else:
            with open(file, "rb") as f:
                await q.message.reply_video(
                    video=f,
                    caption=(
                        "╭━━━〔 ✅ 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘 〕━━━╮\n"
                        "┃ 💜 Powered by ADMIN RAHMAN BOT\n"
                        "┃ 🎬 Your video is ready\n"
                        "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
                    )
                )

        os.remove(file)
        await msg.delete()

    except Exception as e:
        await msg.edit_text("❌ Download failed\n\n" + str(e)[:200])

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, link_handler))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("💜 Neon Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
