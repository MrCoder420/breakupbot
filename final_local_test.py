import requests
import random
import time

def test():
    base = "http://127.0.0.1:8000"
    user = f"test_user_{random.randint(100, 999)}"
    pwd = "testpassword123"
    
    print(f"--- LOCAL SYSTEM TEST ---")
    
    # 1. Register
    print(f"1. Registering user '{user}'...")
    r = requests.post(f"{base}/register", json={"username": user, "password": pwd})
    print(f"   Status: {r.status_code}")
    
    # 2. Login
    print(f"2. Logging in...")
    r = requests.post(f"{base}/login", json={"username": user, "password": pwd})
    token = r.json().get("access_token")
    if token:
        print(f"   Auth: SUCCESS (JWT received)")
    else:
        print(f"   Auth: FAILED")
        return

    # 3. Chat
    print(f"3. Sending test message: 'I feel a bit sad today'...")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(f"{base}/chat", json={"message": "I feel a bit sad today"}, headers=headers)
    if r.status_code == 200:
        resp = r.json().get("response")
        print(f"   ELEANOR: {resp}")
        print(f"\n✅ LOCAL TEST 100% SUCCESSFUL!")
    else:
        print(f"   Chat: FAILED - {r.text}")

if __name__ == "__main__":
    time.sleep(5) # Give server time to start
    test()
