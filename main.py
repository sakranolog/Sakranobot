#main.py
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import config
import handlers
import db

if __name__ == "__main__":
    application = Application.builder().token(config.telegram_api_key).build()



    # Register the CommandHandler with the Application
    application.add_handler(CommandHandler('start', handlers.start))
    application.add_handler(CommandHandler('remember', handlers.remember))
    application.add_handler(CommandHandler('memories', handlers.memories))
    application.add_handler(CommandHandler('delete', handlers.delete))
    application.add_handler(CommandHandler('pay', handlers.pay))

    # Register the MessageHandler with the Application

    
    # Start the Application
    application.run_polling(1.0)