import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from PIL import Image

# ✅ TOKEN
TOKEN = os.getenv("TOKEN")

# ✅ Fake server for Render free plan
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot running")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

threading.Thread(target=run_server).start()

# ✅ BUTTON MENU
def get_menu():
    keyboard = [
        ["📂 Image → PDF", "🖼 JPG → PNG"],
        ["📊 Compress Image", "ℹ About Bot"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ✅ START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Niraj File Converter Bot\n\nChoose option 👇",
        reply_markup=get_menu()
    )

# ✅ HANDLE BUTTONS
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📂 Image → PDF":
        await update.message.reply_text("Send image(s) 📷")

    elif text == "🖼 JPG → PNG":
        await update.message.reply_text("Send JPG image")

    elif text == "📊 Compress Image":
        await update.message.reply_text("Send image to compress")

    elif text == "ℹ About Bot":
        await update.message.reply_text(
            "👨‍💻 Niraj Charpe\n"
            "🤖 Telegram Converter Bot\n"
            "🚀 Built using Python"
        )

# ✅ IMAGE HANDLER (ALL FEATURES)
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.message.caption or ""

    photo = update.message.photo[-1]
    file = await photo.get_file()

    await file.download_to_drive("input.jpg")

    img = Image.open("input.jpg")

    # ✅ JPG → PNG
    img.save("output.png")
    await update.message.reply_document(open("output.png", "rb"))

    # ✅ Compress
    img.save("compressed.jpg", quality=30)
    await update.message.reply_document(open("compressed.jpg", "rb"))

    # ✅ Image → PDF
    pdf_path = "output.pdf"
    img.convert("RGB").save(pdf_path)
    await update.message.reply_document(open(pdf_path, "rb"))

# ✅ MAIN
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))

    print("✅ Final Bot Running...")

    app.run_polling()

if __name__ == "__main__":
    main()
