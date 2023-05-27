import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

telegram_api_key = os.getenv("TELEGRAM_API_KEY")
mongodb_connection_string = os.getenv("MONGODB_CONNECTION_STRING")
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_gpt_engine = "text-davinci-003"