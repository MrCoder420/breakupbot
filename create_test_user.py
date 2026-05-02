import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()

async def create_admin():
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client.breakup_bot
    users_collection = db.users
    
    username = "admin"
    password = "123" # Razorpay team usually prefers simple ones
    
    # Check if exists
    existing = await users_collection.find_one({"username": username})
    if existing:
        print("Admin user already exists!")
        return

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user_data = {
        "username": username,
        "hashed_password": hashed_password,
        "free_messages_left": 0, # Set to 0 so they see the paywall instantly
        "is_subscribed": False,
        "subscription_expiry": None
    }
    
    await users_collection.insert_one(user_data)
    print(f"Test user created: {username} / {password}")

if __name__ == "__main__":
    asyncio.run(create_admin())
