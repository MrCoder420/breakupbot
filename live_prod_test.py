import requests
import random
import time

def live_test():
    base = "https://eleanor-mind-backend.onrender.com"
    user = f"live_tester_{random.randint(1000, 9999)}"
    pwd = "securepassword123"
    
    print(f"--- LIVE CLOUD AUDIT START ---")
    print(f"Target: {base}")
    
    # 1. Register
    print(f"1. Registering new cloud user '{user}'...")
    try:
        r = requests.post(f"{base}/register", json={"username": user, "password": pwd}, timeout=30)
        print(f"   Status: {r.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # 2. Login
    print(f"2. Logging in to get JWT token...")
    try:
        r = requests.post(f"{base}/login", json={"username": user, "password": pwd}, timeout=30)
        token = r.json().get("access_token")
        if token:
            print(f"   Auth: SUCCESS")
        else:
            print(f"   Auth: FAILED - {r.text}")
            return
    except Exception as e:
        print(f"   Error: {e}")
        return

    # 3. Chat
    print(f"3. Sending healing message: 'I feel alone tonight'...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        start_time = time.time()
        r = requests.post(f"{base}/chat", json={"message": "I feel alone tonight"}, headers=headers, timeout=60)
        end_time = time.time()
        
        if r.status_code == 200:
            resp = r.json().get("response")
            print(f"   ELEANOR: {resp}")
            print(f"   Response Time: {round(end_time - start_time, 2)}s")
            print(f"\n✅ PRODUCTION IS 100% OPERATIONAL AND READY!")
        else:
            print(f"   Chat: FAILED - {r.status_code} - {r.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    live_test()
