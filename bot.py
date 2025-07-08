import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from instaloader import Instaloader, Post
from dotenv import load_dotenv
import re

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

loader = Instaloader(dirname_pattern='downloads', save_metadata=False, post_metadata_txt_pattern='')

def download_instagram_post(url: str):
    shortcode_match = re.search(r"instagram\.com/(?:reel|p|tv)/([A-Za-z0-9_-]{11})", url)
    if not shortcode_match:
        return None

    shortcode = shortcode_match.group(1)
    try:
        post = Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target=shortcode)
        for file in os.listdir(f'downloads/{shortcode}'):
            if file.endswith(('.jpg', '.mp4')):
                return f'downloads/{shortcode}/{file}'
    except Exception as e:
        print("Download error:", e)
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Instagram post, reel yoki story linkini yuboring.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("Yuklanmoqda...")
    file_path = download_instagram_post(text)
    if file_path:
        if file_path.endswith('.mp4'):
            await update.message.reply_video(video=open(file_path, 'rb'))
        else:
            await update.message.reply_photo(photo=open(file_path, 'rb'))
    else:
        await update.message.reply_text("Link noto‘g‘ri yoki yuklab bo‘lmadi.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
