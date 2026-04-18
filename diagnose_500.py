import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pymongo import MongoClient

load_dotenv()

print("--- DIAGNOSTIC START ---")

# 1. Check GROQ
try:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        print("[FAIL] GROQ_API_KEY not found in .env")
    else:
        print(f"[OK] GROQ_API_KEY found (starts with {key[:5]})")
        llm = ChatGroq(api_key=key, model="llama3-8b-8192")
        # Just check if we can init, not calling to save tokens
except Exception as e:
    print(f"[FAIL] Groq Init Error: {e}")

# 2. Check MongoDB
try:
    uri = os.getenv("MONGO_URI")
    if not uri:
        print("[FAIL] MONGO_URI not found in .env")
    else:
        print(f"[OK] MONGO_URI found")
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("[OK] MongoDB Connection Successful")
except Exception as e:
    print(f"[FAIL] MongoDB Error: {e}")

# 3. Check Knowledge data
if os.path.exists("knowledge.json"):
    print(f"[OK] knowledge.json exists ({os.path.getsize('knowledge.json')} bytes)")
else:
    print("[FAIL] knowledge.json is missing! Run scraper.py first.")

# 4. Check Chroma/Embeddings
try:
    from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
    print("[OK] HuggingFaceEmbeddings library found")
    # embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
except Exception as e:
    print(f"[FAIL] Embeddings library error: {e}")

print("--- DIAGNOSTIC END ---")
