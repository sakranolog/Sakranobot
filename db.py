from pymongo import MongoClient
import config

# Create a new MongoClient instance
client = MongoClient(config.mongodb_connection_string)

# Connect to your specific database
db = client.sakranobot

# Connect to your specific collection within the database
collection = db.memories
