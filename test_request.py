import os
import json
from dotenv import load_dotenv
from app import app
from fastapi.testclient import TestClient

load_dotenv()

client = TestClient(app)

print("--- TESTING CHAT ENDPOINT ---")
try:
    response = client.post("/chat", json={
        "session_id": "diag_test_123",
        "user_id": "Amit",
        "message": "Hello, I am feeling sad."
    })
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")
except Exception as e:
    # This will print the actual error happening inside app.py
    import traceback
    traceback.print_exc()
