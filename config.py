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
openai_gpt_engine = "text-davinci-003"
