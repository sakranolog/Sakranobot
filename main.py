from telegram.ext import Application, CommandHandler
import config
import handlers

if __name__ == "__main__":
    application = Application.builder().token(config.telegram_api_key).build()

    # Register the CommandHandler with the Application
    application.add_handler(CommandHandler('start', handlers.start))
    application.add_handler(CommandHandler('r', handlers.remember))
    application.add_handler(CommandHandler('remember', handlers.remember))

    # Start the Application
    application.run_polling(1.0)