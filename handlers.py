
from telegram import Update
from telegram.ext import CallbackContext
import datetime
import db

async def start(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Here will be text about the bot and how it functions, for now ise /help to see the commands.")

async def remember(update: Update, context: CallbackContext):
    # Get the memory text from the user's message
    memory_text = " ".join(context.args)

    # Get the user data
    user_data = update.effective_user.to_dict()

    # Prepare the memory data to be saved
    memory_data = {
        "user_id": user_data["id"],
        "user_data": user_data,
        "memory_text": memory_text,
        "timestamp": datetime.datetime.now(),
        "deleted": False
    }

    # Save the memory data to the database
    db.collection.insert_one(memory_data)

    # Respond to the user
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Memory saved!")
