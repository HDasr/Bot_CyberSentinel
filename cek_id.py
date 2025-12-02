from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# GANTI DENGAN TOKEN ANDA
TOKEN = "8206116683:AAGC2q8ZBmS90OsTAkVB4bStFZlk2pQgWtY"

async def cek_id_grup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ambil ID dan Nama Grup
    chat_id = update.effective_chat.id
    chat_title = update.effective_chat.title
    user = update.effective_user.first_name
    
    print(f"✅ DITEMUKAN!")
    print(f"Nama Grup : {chat_title}")
    print(f"ID Grup   : {chat_id}")  # <--- INI YANG ANDA CARI
    
    # Bot akan membalas di grup agar Anda tahu script berjalan
    await update.message.reply_text(f"🆔 ID Grup ini adalah: `{chat_id}`", parse_mode="Markdown")

if __name__ == '__main__':
    print("Bot Pengecek ID berjalan... Kirim pesan apa saja di grup.")
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Bot akan merespon semua pesan teks
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), cek_id_grup))
    
    app.run_polling()