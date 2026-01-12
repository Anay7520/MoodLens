import pymongo
from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"
MONGO_DB_NAME = "MoodLens"

client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

collection = db["MoodLensData"]
users_collection = db["users"]

def get_collection():
    return collection

def add_data(data: dict):
    collection.insert_one(data)

def get_data(query: dict = {}):
    return list(collection.find(query))

def add_user(user: dict):
    users_collection.insert_one(user)

def get_user(email: str):
    return users_collection.find_one({"email": email})