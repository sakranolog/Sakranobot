#config.py
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
is_test = os.getenv("IS_TEST")

if is_test:
    telegram_api_key = os.getenv("TEST_TELEGRAM_API_KEY")
else:
    telegram_api_key = os.getenv("TELEGRAM_API_KEY")

mongodb_connection_string = os.getenv("MONGODB_CONNECTION_STRING")
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_gpt_engine = "gpt-3.5-turbo"
#TODO add gpt configuration defaults

payment_page_url = os.getenv("PAYMENT_PAGE_URL")
payment_message_addition_amount = os.getenv("PAYMENT_MESSAGE_ADDITION_AMOUNT")
default_message_limit = 30

start_text="Here will be text about the bot and how it functions, for now ise /help to see the commands."

intents_list = ["Eat", "Check weather", "Set alarm", "Play music", "Ask for a joke", "Search information", "Make a phone call", "Send email", "Navigate to a place", "Translate text"]
