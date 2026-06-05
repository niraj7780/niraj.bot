import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from PIL import Image

# ✅ Load bot token
TOKEN = os.getenv("TOKEN")

# ✅ Fake server for Render FREE plan
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

# Run fake server in background
threading.Thread(target=run_server).start()

# ✅ Store images
user_images = {}

# ✅ Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📂 Niraj File Converter Bot\n\n"
        "Send images 📷 then type /convert"
    )

# ✅ Receive images
async def receive_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_images:
        user_images[user_id] = []

    photo = update.message.photo[-1]
    file = await photo.get_file()

    file_path = f"{user_id}_{len(user_images[user_id])}.jpg"
    await file.download_to_drive(file_path)

    user_images[user_id].append(file_path)

    await update.message.reply_text("✅ Image added")

# ✅ Convert images → PDF (FIXED ✅)
async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_images or len(user_images[user_id]) == 0:
        await update.message.reply_text("❌ Send images first")
        return

    try:
        images = []

        # ✅ CORRECT LOOP
        for path in user_images[user_id]:
            img = Image.open(path).convert("RGB")
            images.append(img)

        pdf_path = f"{user_id}_output.pdf"

        images[0].save(pdf_path, save_all=True, append_images=images[1:])

        await update.message.reply_document(open(pdf_path, "rb"))

        # clear after use
        user_images[user_id] = []

    except Exception as e:
        print("Error:", e)
        await update.message.reply_text("⚠️ Conversion failed")

# ✅ Main
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("convert", convert))
    app.add_handler(MessageHandler(filters.PHOTO, receive_image))

    print("✅ Bot Running...")

    app.run_polling()

if __name__ == "__main__":
    main()
