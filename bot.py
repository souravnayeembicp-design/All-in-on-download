import os
import logging
import tempfile
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

# Logging চালু
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Set TELEGRAM_BOT_TOKEN environment variable first!")

def remove_tiktok_watermark(input_path, output_path):
    command = [
        "ffmpeg",
        "-i", input_path,
        "-vf", "crop=iw:ih-50:0:0",
        "-c:a", "copy",
        output_path,
        "-y"
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def download_video(url):
    ydl_opts = {
        'outtmpl': '%(id)s.%(ext)s',
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'nocheckcertificate': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        if not info_dict:
            return None, None
        video_title = info_dict.get('title', None)
        video_id = info_dict.get('id', None)

        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, f"{video_id}.mp4")
        ydl_opts['outtmpl'] = temp_path
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return temp_path, video_title

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("হ্যালো! ভিডিও লিঙ্ক পাঠাও আমি ডাউনলোড করে দিবো (YouTube, TikTok, Facebook, Instagram)")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = ("ভিডিও ডাউনলোড করার জন্য ভিডিও লিঙ্ক পাঠাও।\n"
                 "সমর্থিত সাইট: YouTube, TikTok, Facebook, Instagram\n"
                 "TikTok ভিডিও থেকে ওয়াটারমার্ক অপসারণ করা হবে।")
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    await update.message.reply_text("ভিডিও ডাউনলোড শুরু হচ্ছে... একটু ধৈর্য ধরো।")

    try:
        video_path, title = download_video(url)
        if not video_path:
            await update.message.reply_text("দুঃখিত, ভিডিও ডাউনলোড করা যায়নি। লিঙ্কটি সঠিক কিনা চেক করুন।")
            return

        if "tiktok.com" in url:
            no_wm_path = video_path.replace(".mp4", "_nowm.mp4")
            remove_tiktok_watermark(video_path, no_wm_path)
            os.remove(video_path)
            video_path = no_wm_path

        with open(video_path, 'rb') as video_file:
            await update.message.reply_video(video_file, caption=title or "ভিডিও")

        os.remove(video_path)
    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        await update.message.reply_text(f"ত্রুটি: {e}")

def main():
    app = ApplicationBuilder()\
        .token(TOKEN)\
        .request_kwargs({"read_timeout": 30, "connect_timeout": 30})\
        .build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    logger.info("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
