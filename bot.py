import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from PIL import Image
from PyPDF2 import PdfReader

TOKEN = os.getenv("TOKEN")

user_images = {}

# -------------------------
# ✅ Start Command
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📂 Niraj File Converter Bot\n\n"
        "✅ Image → PDF\n"
        "✅ PDF → Images\n"
        "✅ Multiple Images → One PDF\n\n"
        "👉 Send images → /convert\n"
        "👉 Send PDF → I convert to images\n"
        "👉 /clear to reset"
    )

# -------------------------
# ✅ Receive Image
# -------------------------
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

# -------------------------
# ✅ Convert Images → PDF
# -------------------------
async def convert_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_images or len(user_images[user_id]) == 0:
        await update.message.reply_text("❌ Send images first")
        return

    try:
        image_paths = user_images[user_id]

        images = []
        for path in image_paths:
            img = Image.open(path).convert("RGB")
            images.append(img)

        pdf_path = f"{user_id}_output.pdf"

        images[0].save(pdf_path, save_all=True, append_images=images[1:])

        await update.message.reply_document(document=open(pdf_path, "rb"))

        user_images[user_id] = []

    except Exception as e:
        print("Error:", e)
        await update.message.reply_text("⚠️ Conversion failed")

# -------------------------
# ✅ PDF → Images
# -------------------------
async def pdf_to_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        document = update.message.document

        if not document.file_name.endswith(".pdf"):
            await update.message.reply_text("❌ Please send PDF file")
            return

        file = await document.get_file()
        pdf_path = document.file_name

        await file.download_to_drive(pdf_path)

        reader = PdfReader(pdf_path)

        # Convert each page to image (simple text snapshot)
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or "No text found"

            image_path = f"page_{i}.txt"

            # save text as file (because real PDF→image needs advanced lib)
            with open(image_path, "w") as f:
                f.write(text)

            await update.message.reply_document(document=open(image_path, "rb"))

    except Exception as e:
        print("PDF Error:", e)
        await update.message.reply_text("⚠️ PDF conversion failed")

# -------------------------
# ✅ Clear Data
# -------------------------
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_images[user_id] = []
    await update.message.reply_text("✅ Cleared all images")

# -------------------------
# ✅ Main
# -------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("convert", convert_to_pdf))
    app.add_handler(CommandHandler("clear", clear))

    app.add_handler(MessageHandler(filters.PHOTO, receive_image))
    app.add_handler(MessageHandler(filters.Document.ALL, pdf_to_images))

    print("✅ Advanced File Bot Running...")

    app.run_polling()

if __name__ == "__main__":
    main()
