import openai
from telegram import Update
from telegram.ext import CallbackContext
import datetime
import db
import config


user_memories = {}


openai.api_key = config.openai_api_key
async def handle_text(update: Update, context: CallbackContext):
    if update.message and update.message.text:
        user_id = update.effective_user.id
        text = update.message.text

        # Get user's memories
        memories = db.get_memories(user_id)
        memory_texts = [memory["memory_text"] for memory in memories]

        # Check if the message ends with a question mark
        if text.strip().endswith("?"):
            # Prepare the prompt with the memories
            prompt = f"This is a list of my memories: {', '.join(memory_texts)}. Based on this, I would like to know: {text}"

            # Generate a response from GPT-3
            try:
                completion = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=150)
                response = completion.choices[0].text.strip()
            except Exception:
                response = "The GPT service is currently not available, try again later."
        else:
            # Send the text to GPT-3 without the memories
            try:
                completion = openai.Completion.create(engine="text-davinci-003", prompt=text, max_tokens=150)
                response = completion.choices[0].text.strip()
            except Exception:
                response = "The GPT service is currently not available, try again later."

        # Send the response to the user
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


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

async def memories(update: Update, context: CallbackContext):
    # Fetch the memories
    user_memories = db.get_memories(update.effective_user.id)

    # If there are no memories, inform the user and return
    if not user_memories:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No memories found.")
        return

    # Number the memories and prepare the message
    numbered_memories = [f"{i+1}. {memory['memory_text']}" for i, memory in enumerate(user_memories)]
    message = "\n".join(numbered_memories)

    # Send the message
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

    # Store the memories in context.user_data so we can access them in the /delete handler
    context.user_data['memories'] = user_memories
    context.user_data['awaiting_delete'] = True


async def delete(update: Update, context: CallbackContext):
    # Check if we are awaiting a /delete command
    if not context.user_data.get('awaiting_delete', False):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You can only use /delete immediately after /memories.")
        return

    # Parse the numbers provided by the user
    numbers = context.args
    numbers = [int(num) - 1 for num in numbers]

    # Fetch the memories from context.user_data
    user_memories = context.user_data['memories']

    # Delete the specified memories
    for num in numbers:
        if num < 0 or num >= len(user_memories):
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"No memory with number {num + 1}.")
            continue
        db.delete_memory(user_memories[num]['_id'])

    # Notify the user
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Memories deleted.")

    # We are no longer awaiting a /delete command
    context.user_data['awaiting_delete'] = False

