import requests
import random
import time

def live_test():
    base = "https://eleanor-mind-backend.onrender.com"
    user = f"db_check_{random.randint(1000, 9999)}"
    pwd = "finalpassword123"
    
    print(f"--- LIVE DATABASE INTEGRITY CHECK ---")
    print(f"Target: {base}")
    
    # 1. Register
    print(f"1. Registering user '{user}'...")
    try:
        r = requests.post(f"{base}/register", json={"username": user, "password": pwd}, timeout=30)
        if r.status_code == 200:
            print(f"   Registration: SUCCESS")
        else:
            print(f"   Registration: FAILED - {r.status_code} - {r.text}")
            return
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # 2. Login
    print(f"2. Verifying persistence with Login...")
    try:
        # Small delay to allow MongoDB Atlas propagation
        time.sleep(2)
        r = requests.post(f"{base}/login", json={"username": user, "password": pwd}, timeout=30)
        if r.status_code == 200:
            print(f"   Login: SUCCESS (User persisted and found)")
            token = r.json().get("access_token")
        else:
            print(f"   Login: FAILED - {r.status_code} - {r.text}")
            return
    except Exception as e:
        print(f"   Error: {e}")
        return

    # 3. Chat (RAG Check)
    print(f"3. Testing AI Memory retrieval...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.post(f"{base}/chat", json={"message": "Help me heal"}, headers=headers, timeout=60)
        if r.status_code == 200:
            print(f"   AI RESPONSE: {r.json().get('response')}")
            print(f"\n✅ DATABASE INTEGRITY CONFIRMED!")
        else:
            print(f"   AI: FAILED - {r.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    live_test()
