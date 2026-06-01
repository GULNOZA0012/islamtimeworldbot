from telegram.ext import Application, CommandHandler, MessageHandler, filters

async def start(update, context):
    await update.message.reply_text("Salom!")

def main():
    app = Application.builder().token("TOKEN").build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()  # ← bu ichida loop o'zi boshqaradi

if __name__ == "__main__":
    main()
