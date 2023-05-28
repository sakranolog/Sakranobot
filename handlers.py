import openai
from telegram import Update
from telegram.ext import CallbackContext
import datetime
import db
import config
from datetime import datetime, timedelta

openai.api_key = config.openai_api_key

user_memories = {}
chat_contexts = {}

async def get_intent(user_id: str, message: str):
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": message}
    ]

    try:
        response = openai.ChatCompletion.create(
            model=config.openai_gpt_engine,
            messages=conversation
        )
        response_text = response['choices'][0]['message']['content']
        return response_text
    except Exception as e:
        print(f"Error in get_intent: {str(e)}")
        return None


async def handle_text(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    text = update.message.text

    # Get user's memories
    memories = db.get_memories(user_id)
    memory_texts = [memory["memory_text"] for memory in memories]

    # Create the conversation history for the chat model
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"This is a list of my memories: {', '.join(memory_texts)}"},
        {"role": "user", "content": text}
    ]

    # Generate a response from GPT
    try:
        response = openai.ChatCompletion.create(
          model=config.openai_gpt_engine,
          messages=conversation
        )
        response_text = response['choices'][0]['message']['content']

        # Get the intent
        intent = await get_intent(user_id, response_text)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"I think you want to: {intent}. Is that correct?")
    except Exception as e:
        response_text = f"The GPT service is currently not available, try again later. Error: {str(e)}"

    # Add message to context
    if user_id in chat_contexts:
        chat_contexts[user_id]['messages'].append(text)
        chat_contexts[user_id]['last_activity'] = datetime.now()
        chat_contexts[user_id]['pending_intent'] = intent if 'intent' in locals() else None

    # Check if the context should be reset
    if len(chat_contexts[user_id]['messages']) >= 5:
        await reset_context(user_id)


async def reset_context(user_id):
    chat_contexts[user_id]['messages'] = []
    chat_contexts[user_id]['pending_intent'] = None
    # Send a message to the user stating it started a new chat context
    await context.bot.send_message(chat_id=user_id, text="Starting a new chat context.")









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

