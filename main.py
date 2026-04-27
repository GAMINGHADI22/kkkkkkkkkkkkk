import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("8659260396:AAFAN2zmbfgTmZE-oVEQV0eWWw8HugxCEa0", "8659260396:AAFAN2zmbfgTmZE-oVEQV0eWWw8HugxCEa0")
CHANNEL_USERNAME = "@bangladeshkobor"   # এখানে তোমার channel username দাও

FAST_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "concurrent_fragment_downloads": 16,
    "retries": 10,
    "fragment_retries": 10,
    "socket_timeout": 20,
}

async def is_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def force_join_msg(update: Update):
    buttons = [
        [InlineKeyboardButton("💜 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")],
        [InlineKeyboardButton("✅ I Joined", callback_data="check_join")]
    ]

    await update.message.reply_text(
        "╭━━━〔 🔒 JOIN REQUIRED 〕━━━╮\n"
        "┃ Bot use করতে আগে channel join করো\n"
        "┃ তারপর ✅ I Joined চাপো\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_joined(update, context):
        await force_join_msg(update)
        return

    msg = await update.message.reply_text("💜 Initializing...")

    for t in ["💜 Initializing.", "💜 Initializing..", "💜 Initializing..."]:
        await asyncio.sleep(0.4)
        await msg.edit_text(t)

    await msg.edit_text(
        "╔══════════════════════════════╗\n"
        "║ 💜✨ ADMIN RAHMAN BOT ✨💜 ║\n"
        "╠══════════════════════════════╣\n"
        "║ 🌌 NEON VIDEO DOWNLOADER     ║\n"
        "║ 🎬 YouTube • TikTok          ║\n"
        "║ 🎧 MP3 • HD Video            ║\n"
        "║ 🚀 Ultra Fast Engine         ║\n"
        "╚══════════════════════════════╝\n\n"
        "💜 Send your video link 👇"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "╭━━━〔 💜 HELP MENU 〕━━━╮\n"
        "┃ 1. YouTube/TikTok link পাঠাও\n"
        "┃ 2. Quality select করো\n"
        "┃ 3. Video/MP3 পেয়ে যাবে\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "╭━━━〔 ℹ️ ABOUT 〕━━━╮\n"
        "┃ 💜 RAHMAN NEON DOWNLOADER\n"
        "┃ 🎬 Video + 🎧 Audio Downloader\n"
        "┃ 👤 Admin: @ABDUR9X\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯"
    )

async def link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_joined(update, context):
        await force_join_msg(update)
        return

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

        context.user_data["title"] = title

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
            "╭━━━━〔 💜 NEON PREVIEW 💜 〕━━━━╮\n"
            f"🎬 {title[:45]}\n"
            f"⏱ Duration: {m}:{s:02d}\n"
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
        await msg.edit_text("❌ Preview failed\n\n" + str(e)[:150])

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "check_join":
        if await is_joined(update, context):
            await q.message.edit_text(
                "✅ Joined successfully!\n\n"
                "Now send your YouTube/TikTok link 💜"
            )
        else:
            await q.message.reply_text("❌ এখনো channel join করোনি")
        return

    if not await is_joined(update, context):
        await q.message.reply_text("🔒 আগে channel join করো")
        return

    url = context.user_data.get("url")
    title = context.user_data.get("title", "Your file")
    choice = q.data

    quality_name = {
        "1080": "1080p HD",
        "720": "720p HD",
        "360": "360p Lite",
        "mp3": "MP3 Audio"
    }.get(choice, "Video")

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
            "╭━━━〔 🔊 PREPARING 〕━━━╮\n"
            "┃ ▰▰▰▰▱▱▱▱▱▱ 40%\n"
            "┃ 🎶 Encoding media...\n"
            "┃ ⚡ Finalizing file...\n"
            "╰━━━━━━━━━━━━━━━━━━━━╯"
        )
        await asyncio.sleep(1)

        if choice == "mp3":
            file = file.replace(".webm", ".mp3").replace(".m4a", ".mp3")

        size = round(os.path.getsize(file) / (1024 * 1024), 2)

        await msg.edit_text(
            "╭━━━〔 📤 SENDING 〕━━━╮\n"
            "┃ ▰▰▰▰▰▰▰▰▱▱ 80%\n"
            "┃ 💜 Uploading to Telegram...\n"
            "┃ ⏳ Please wait...\n"
            "╰━━━━━━━━━━━━━━━━━━━━╯"
        )

        if choice == "mp3":
            with open(file, "rb") as f:
                await q.message.reply_audio(
                    audio=f,
                    caption=(
                        "╭━━━〔 🎧 AUDIO READY 〕━━━╮\n"
                        f"┃ 🎵 Title: {title[:25]}\n"
                        f"┃ 💾 Size: {size} MB\n"
                        "┃ 💜 ADMIN RAHMAN BOT\n"
                        "╰━━━━━━━━━━━━━━━━━━━━╯"
                    )
                )
        else:
            with open(file, "rb") as f:
                await q.message.reply_video(
                    video=f,
                    caption=(
                        "╭━━━〔 ✅ DOWNLOAD COMPLETE 〕━━━╮\n"
                        f"┃ 🎬 Title: {title[:25]}\n"
                        f"┃ 📺 Quality: {quality_name}\n"
                        f"┃ 💾 Size: {size} MB\n"
                        "┃ 💜 ADMIN RAHMAN BOT\n"
                        "╰━━━━━━━━━━━━━━━━━━━━╯"
                    )
                )

        os.remove(file)
        await msg.delete()

    except Exception as e:
        await msg.edit_text("❌ Download failed\n\n" + str(e)[:200])

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("about", about))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, link_handler))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("💜 Force Join Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
