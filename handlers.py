import openai
from telegram import Update
from telegram.ext import CallbackContext
from datetime import datetime
import db
import config
import json


openai.api_key = config.openai_api_key

user_memories = {}


async def handle_text(update: Update, context: CallbackContext):
    if not await handle_user_state(update, context):
        return
    user_id = update.effective_user.id

    # Check if user already has a context
    if 'chat_context' not in context.user_data or 'endchat' in context.user_data:
        # Initialize chat context
        context.user_data['chat_context'] = {
            'messages': [],  # List to hold the last 20 messages
            'timestamp': datetime.now(),  # Timestamp of the last message
            'memories': db.get_memories(user_id)  # Load user's memories from the DB
        }
        # Clear endchat flag
        if 'endchat' in context.user_data:
            del context.user_data['endchat']

        print("Chat context initialized: ", context.user_data['chat_context'])

        # Inform the user about the 15-minute inactivity rule
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Note: If there is no activity for 15 minutes, this chat will end.\nEvery message from that point will start a new context.")

    user_message = update.message.text
    print("User message: ", user_message)

    # Add user's message to the chat context
    context.user_data['chat_context']['messages'].append({
        'role': 'user',
        'content': user_message,
    })

    # If there are more than 20 messages in the chat context, remove the oldest one
    if len(context.user_data['chat_context']['messages']) > 20:
        context.user_data['chat_context']['messages'].pop(0)

    # Update the timestamp of the last message
    context.user_data['chat_context']['timestamp'] = datetime.now()

    # Print chat context for debugging
    #print("Chat context after adding user's message: ", context.user_data['chat_context'])    

    # Check if user already has a system message
    #if not any(message['role'] == 'system' for message in context.user_data['chat_context']['messages']):
    #    context.user_data['chat_context']['messages'].append({
    #        'role': 'system',
    #        'content': 'Loading user\'s memories...'
    #    })

    # Find system message and append memories
    #for message in context.user_data['chat_context']['messages']:
    #    if message['role'] == 'system':
    #        # Append the memories with a brief introduction
    #        memory_texts = [mem['memory_text'] for mem in context.user_data['chat_context']['memories']]
    #        if memory_texts:
    #            memories_intro = "For context, here are some memories related to this user:"
    #            memories_content = '\n'.join(memory_texts)
    #            message['content'] += f'\n{memories_intro}\n{memories_content}'
    #        else:
    #            message['content'] += '\nNo specific memories related to this user are available for context.'
    
    
    # 1. Prepare the message list
    message_list = context.user_data['chat_context']['messages'] + [{'role': 'system', 'content': f"For context, here are some memories related to this user: {mem['memory_text']}"} for mem in context.user_data['chat_context']['memories']]
    print(message_list)
    # 2. Make the request to the OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model=config.openai_gpt_engine,
            messages=message_list,
            temperature=0.8,
            max_tokens=150  # or any other value you deem suitable
        )
    except Exception as e:
        print(f"Error in ChatCompletion: {str(e)}")
        return

    # 3. Handle the response
    ai_message = response['choices'][0]['message']['content']

    # Add AI's message to the chat context
    context.user_data['chat_context']['messages'].append({
        'role': 'assistant',
        'content': ai_message,
    })

    # 4. Send the AI's message back to the user
    await context.bot.send_message(chat_id=update.effective_chat.id, text=ai_message)

    print("AI message: ", ai_message)
    print("Chat context after adding AI's message: ", context.user_data['chat_context'])






async def start(update: Update, context: CallbackContext):
    if not await handle_user_state(update, context):
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=config.start_text)




async def remember(update: Update, context: CallbackContext):
    if not await handle_user_state(update, context):
        return
    # Get the memory text from the user's message
    memory_text = " ".join(context.args)
    # Check if the memory text is empty or has less than two words
    if not memory_text or len(memory_text.split()) < 3:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error: New memories must contain at least three words.")
        return
    # Get the user data
    user_data = update.effective_user.to_dict()
    now=datetime.now(),

    ## Parse the memory for type and date and time
    conversation = [
        {"role": "system", "content": "You are an AI that recieves a memory and needs to decide what categories would this memory fit in to, no more than three. your response is always in the format of a json file with: categories[]."},
        {"role": "user", "content": memory_text}
    ]

    try:
        response = openai.ChatCompletion.create(
            model=config.openai_gpt_engine,
            messages=conversation,
            temperature=1.0
        )
        # Assuming that the GPT model returns the intents in the response
        categories_content = response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error in get_intent: {str(e)}")
        categories_content = "{}"  # default to an empty JSON object

    # Parse the categories from the JSON string
    categories = json.loads(categories_content).get("categories", [])

    # Prepare the memory data to be saved
    memory_data = {
        "user_id": user_data["id"],
        "memory_text": memory_text,
        "timestamp": datetime.now(),
        "categories": categories,
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