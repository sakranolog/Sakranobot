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


payment_page_url = os.getenv("PAYMENT_PAGE_URL")
payment_massage_addition_amount = os.getenv("PAYMENT_MASSAGE_ADDITION_AMOUNT")