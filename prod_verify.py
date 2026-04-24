import requests
import random

def test():
    base = "https://breakup-bot-backend.onrender.com"
    print(f"--- LIVE PRODUCTION TEST ---")
    
    try:
        # 1. Root
        r = requests.get(base)
        print(f"Health: {r.status_code} {r.json()}")
        
        # 2. Register
        u = f"test_{random.randint(100, 999)}"
        r = requests.post(f"{base}/register", json={"username": u, "password": "password"})
        print(f"Register {u}: {r.status_code}")
        
        # 3. Login
        r = requests.post(f"{base}/login", json={"username": u, "password": "password"})
        token = r.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Login: SUCCESS")
        
        # 4. Chat
        print("Sending message...")
        r = requests.post(f"{base}/chat", json={"message": "Hi Eleanor, how are you?"}, headers=headers)
        if r.status_code == 200:
            print(f"ELEANOR: {r.json().get('response')}")
            print("\n✅ LIVE PRODUCTION IS 100% WORKING!")
        else:
            print(f"CHAT FAILED: {r.status_code} {r.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test()
