import openai
from telegram import Update
from telegram.ext import CallbackContext
import datetime
import db
import config
import datetime

openai.api_key = config.openai_api_key

user_memories = {}
chat_contexts = {}

def get_intents(message: str, intent_list: list):
    intent_list_str = ', '.join(intent_list)
    conversation = [
        {"role": "system", "content": f"You are a bot helping understand the intents of the user. Answer only with the intents, no extra text or description. The only possible intents are: {intent_list_str}. if it's not in the list return none"},
        {"role": "user", "content": message}
    ]

    try:
        response = openai.ChatCompletion.create(
            model=config.openai_gpt_engine,
            messages=conversation,
            temperature=1.0
        )
        # Assuming that the GPT model returns the intents in the response
        intents = response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error in get_intent: {str(e)}")
        intents = ""

    return intents

async def handle_text(update: Update, context: CallbackContext):
    if not await handle_user_state(update, context):
        return
    text = update.message.text
    intents = get_intents(text, config.intents_list)
    # assuming intents are separated by some delimiter like a comma
    intents = intents.split(",") if intents else [None]
    # add a second None if only one intent (or none) was returned
    if len(intents) == 1:
        intents.append(None)

    intent1, intent2 = intents
    response_text = f"I think your intent is {intent1} or {intent2}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)
















async def start(update: Update, context: CallbackContext):
    if not await handle_user_state(update, context):
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=config.start_text)

async def remember(update: Update, context: CallbackContext):
    if not await handle_user_state(update, context):
        return
    # Get the memory text from the user's message
    memory_text = " ".join(context.args)

    # Get the user data
    user_data = update.effective_user.to_dict()

    # Prepare the memory data to be saved
    memory_data = {
        "user_id": user_data["id"],
        "memory_text": memory_text,
        "timestamp": datetime.datetime.now(),
        "deleted": False
    }

    # Save the memory data to the database
    db.collection.insert_one(memory_data)

    # Respond to the user
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Memory saved!")

async def memories(update: Update, context: CallbackContext):
    if not await handle_user_state(update, context):
        return
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
    if not await handle_user_state(update, context):
        return
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







async def handle_user_state(update, context):
    user_data = update.message.from_user  # this is the user data object from the Telegram bot
    print(f"User {user_data.id} registered a message. has sent total: {db.get_messages_sent(user_data.id)} and bought: {db.get_message_limit(user_data.id)}")
    # Check if the user exists in the database
    if db.get_messages_sent(user_data.id) > db.get_message_limit(user_data.id):
        print(f"User {user_data.id} over message limit! has sent: {db.get_messages_sent(user_data.id)} and bought: {db.get_message_limit(user_data.id)}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"You don't have any message credits left! (sent: {db.get_messages_sent(user_data.id)} payed for: {db.get_message_limit(user_data.id)}).\nPlease use /pay to buy more message credits")
        return False
    if not db.get_user(user_data.id):
        # If the user doesn't exist, create a new user
        print(f"Creating new user {user_data.id}")
        db.create_user(user_data.to_dict())
    # Update the count of messages sent by the user
    db.update_messages_sent(user_data.id)


    
    return True


async def pay(update: Update, context: CallbackContext):
    # Get the user's ID
    user_id = update.effective_user.id

    # Construct the URL
    url = config.payment_page_url + "?m__userid=" + str(user_id)

    # Send a message to the user with the URL
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"To add 500 messages to your quota, please click the following link to pay: {url}")