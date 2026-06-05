import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ✅ Token
TOKEN = os.getenv("TOKEN")

# ✅ Fake server for Render
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
        ["🔍 Search", "📄 Info", "🛍 Shop"],
        ["⚙ Settings", "📚 Menu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# -------------------------
# ✅ Start Command
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🕵️ I can help you with multiple tools.\nChoose an option below 👇",
        reply_markup=get_menu()
    )

# -------------------------
# ✅ Handle Button Clicks
# -------------------------
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🔍 Search":
        await update.message.reply_text("🔍 Send anything to search")

    elif text == "📄 Info":
        await update.message.reply_text("📄 This is Niraj File Tool Bot")

    elif text == "🛍 Shop":
        await update.message.reply_text("🛍 Feature coming soon")

    elif text == "⚙ Settings":
        await update.message.reply_text("⚙ No settings yet")

    elif text == "📚 Menu":
        await update.message.reply_text(
            "📚 Features:\n✅ Image → PDF\n✅ Multi tools"
        )

    else:
        await update.message.reply_text(
            "❓ Unknown option\nUse buttons 👇",
            reply_markup=get_menu()
        )

# -------------------------
# ✅ Main
# -------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    print("✅ UI Bot Running...")

    app.run_polling()

if __name__ == "__main__":
    main()
