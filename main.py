from telegram.ext import Application, CommandHandler, CallbackContext
from telegram import Update
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import datetime

load_dotenv()  # take environment variables from .env.

telegram_api_key = os.getenv("TELEGRAM_API_KEY")
mongodb_connection_string = os.getenv("MONGODB_CONNECTION_STRING")

# Create a new MongoClient instance
client = MongoClient(mongodb_connection_string)

# Connect to your specific database
db = client.sakranobot

# Connect to your specific collection within the database
collection = db.memories

async def remember(update: Update, context: CallbackContext):
    # Get the memory text from the user's message
    memory_text = " ".join(context.args)

    # Get the user data
    user_data = update.effective_user.to_dict()

    # Prepare the memory data to be saved
    # Prepare the memory data to be saved
    memory_data = {
        "user_id": user_data["id"],
        "user_data": user_data,
        "memory_text": memory_text,
        "timestamp": datetime.datetime.now(),
        "deleted": False
    }


    # Save the memory data to the database
    collection.insert_one(memory_data)

    # Respond to the user
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Memory saved!")

if __name__ == "__main__":
    application = Application.builder().token(telegram_api_key).build()

    # Register the CommandHandler with the Application
    application.add_handler(CommandHandler('r', remember))
    application.add_handler(CommandHandler('remember', remember))

    # Start the Application
    application.run_polling(1.0)
