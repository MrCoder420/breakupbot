import os
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

def check():
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client.breakup_bot_db
    users = db.users
    
    count = users.count_documents({})
    print(f"Total Users in DB: {count}")
    
    latest = list(users.find().sort("created_at", -1).limit(3))
    print("\nLatest Users:")
    for u in latest:
        print(f"- {u.get('username')} (Fields: {list(u.keys())})")

if __name__ == "__main__":
    check()
