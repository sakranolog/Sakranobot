#db.py
from pymongo import MongoClient, DESCENDING
import config
import datetime

# Create a new MongoClient instance
client = MongoClient(config.mongodb_connection_string)

# Connect to your specific database
if config.is_test:
    db = client.sakranobot_test
else:
    db = client.sakranobot

# Connect to your specific collection within the database
collection = db.memories
users_collection = db.users

def save_memory(memory_data):
    collection.insert_one(memory_data)

def get_memories(user_id):
    return list(collection.find({"user_id": user_id, "deleted": False}).sort("timestamp", DESCENDING))

def delete_memory(memory_id):
    collection.update_one({"_id": memory_id}, {"$set": {"deleted": True}})

def create_user(user_data):
    return users_collection.insert_one({
        "user_id": user_data['id'],
        "user_data": user_data,
        "join_date": datetime.datetime.utcnow(),
        "messages_sent": 0,
        "message_limit": 30,
        "api_keys": {},
        "payments": []
    })

def add_payment(user_id, date, amount, currency, units_bought):
    payment_data = {
        "date": date,
        "amount": amount,
        "currency": currency,
        "units_bought": units_bought
    }
    users_collection.update_one(
        {"user_id": user_id}, 
        {"$push": {"payments": payment_data}}
    )


def get_user(user_id):
    return users_collection.find_one({"user_id": user_id})

def update_messages_sent(user_id):
    users_collection.update_one({"user_id": user_id}, {"$inc": {"messages_sent": 1}})
