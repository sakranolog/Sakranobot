from telegram.ext import Application, CommandHandler
import os
from dotenv import load_dotenv

from pymongo import MongoClient


load_dotenv()  # take environment variables from .env.
telegram_api_key = os.getenv("TELEGRAM_API_KEY")

mongodb_connection_string = os.getenv("MONGODB_CONNECTION_STRING")
# Create a new MongoClient instance
client = MongoClient(mongodb_connection_string)

# Connect to your specific database (replace 'your_database' with the name of your database)
db = client.your_database

# Connect to your specific collection within the database (replace 'your_collection' with the name of your collection)
collection = db.your_collection

# Test the connection by saving some data
test_data = {"name": "test", "message": "this is a test"}
collection.insert_one(test_data)

# Fetch the saved data
fetched_data = collection.find_one({"name": "test"})
print(fetched_data)



async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

if __name__ == "__main__":
    application = Application.builder().token(telegram_api_key).build()

    # Register the CommandHandler with the Application
    application.add_handler(CommandHandler('start', start))

    # Start the Application
    application.run_polling(1.0)
