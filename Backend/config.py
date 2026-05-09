import os
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET = os.getenv("JWT_SECRET")
DB_NAME = os.getenv("DB_NAME")

print("MONGO_URI loaded:", MONGO_URI)

try:
    client = MongoClient(MONGO_URI)
    client.server_info()
    print("MongoDB connected successfully")
except Exception as e:
    print("MongoDB connection error:", e)

db = client[DB_NAME]

users_collection = db["users"]
units_collection = db["units_log"]
predictions_collection = db["predictions"]