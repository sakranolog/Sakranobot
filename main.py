from telegram.ext import Application, CommandHandler, MessageHandler
import config
import handlers

if __name__ == "__main__":
    application = Application.builder().token(config.telegram_api_key).build()

    # Register the CommandHandler with the Application
    
    application.add_handler(CommandHandler('remember', handlers.remember))
    application.add_handler(CommandHandler('memories', handlers.memories))
    application.add_handler(CommandHandler('delete', handlers.delete))
    application.add_handler(MessageHandler(None, handlers.handle_text))
    # Start the Application
    application.run_polling(1.0)