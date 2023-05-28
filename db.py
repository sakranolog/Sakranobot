#db.py
from pymongo import MongoClient, DESCENDING
import config

# Create a new MongoClient instance
client = MongoClient(config.mongodb_connection_string)

# Connect to your specific database
if config.is_test:
    db = client.sakranobot_test
else:
    db = client.sakranobot

# Connect to your specific collection within the database
collection = db.memories

def save_memory(memory_data):
    collection.insert_one(memory_data)

def get_memories(user_id):
    return list(collection.find({"user_id": user_id, "deleted": False}).sort("timestamp", DESCENDING))

def delete_memory(memory_id):
    collection.update_one({"_id": memory_id}, {"$set": {"deleted": True}})
