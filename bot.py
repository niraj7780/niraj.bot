import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from PIL import Image

TOKEN = os.getenv("TOKEN")

user_images = {}

# ✅ Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📂 Niraj File Converter Bot\n\n"
        "✅ Send images\n"
        "✅ Then type /convert"
    )

# ✅ Receive Image
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

# ✅ Convert to PDF
async def convert_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_images or len(user_images[user_id]) == 0:
        await update.message.reply_text("❌ Send images first")
        return

    images = []

    for path in user_images[user_id]:
        img = Image.open(path).convert("RGB")
        images.append(img)

    pdf_path = f"{user_id}_output.pdf"
    images[0].save(pdf_path, save_all=True, append_images=images[1:])

    await update.message.reply_document(document=open(pdf_path, "rb"))

    user_images[user_id] = []

# ✅ Main
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("convert", convert_to_pdf))
    app.add_handler(MessageHandler(filters.PHOTO, receive_image))

    print("✅ Bot Running...")

    app.run_polling()

if __name__ == "__main__":
    main()
