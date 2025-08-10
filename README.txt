Telegram Video Downloader Bot

Setup Instructions:

1. Install required packages:
   pip install -r requirements.txt

2. Install ffmpeg on your server/PC.
   On Ubuntu/Debian:
     sudo apt update
     sudo apt install ffmpeg

3. Replace YOUR_TELEGRAM_BOT_TOKEN_HERE in bot.py with your Bot token from BotFather.

4. Run the bot:
   python bot.py

5. Send a supported video URL (YouTube, TikTok, Facebook, Instagram) to your bot in Telegram.

Note: TikTok videos will have watermark removed by cropping the bottom 50 pixels.
