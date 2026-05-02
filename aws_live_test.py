import requests
import random
import time

def aws_live_test():
    base = "http://52.66.203.85:8000"
    user = f"aws_tester_{random.randint(1000, 9999)}"
    pwd = "securepassword123"
    
    print(f"--- AWS LIVE PRODUCTION AUDIT START ---")
    print(f"Target: {base}")
    
    # 1. Register
    print(f"1. Registering new cloud user '{user}'...")
    try:
        r = requests.post(f"{base}/register", json={"username": user, "password": pwd}, timeout=30)
        print(f"   Status: {r.status_code}")
        if r.status_code != 200:
            print(f"   Error Detail: {r.text}")
            return
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # 2. Login
    print(f"2. Logging in to get JWT token...")
    try:
        r = requests.post(f"{base}/login", json={"username": user, "password": pwd}, timeout=30)
        token = r.json().get("access_token")
        if token:
            print(f"   Auth: SUCCESS (Token Received)")
        else:
            print(f"   Auth: FAILED - {r.text}")
            return
    except Exception as e:
        print(f"   Error: {e}")
        return

    # 3. Chat
    print(f"3. Sending message to AWS Eleanor: 'I feel so alone today'...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        start_time = time.time()
        r = requests.post(f"{base}/chat", json={"message": "I feel so alone today"}, headers=headers, timeout=60)
        end_time = time.time()
        
        if r.status_code == 200:
            resp = r.json().get("response")
            print(f"   ELEANOR: {resp}")
            print(f"   Response Time: {round(end_time - start_time, 2)}s")
            print(f"\n[SUCCESS] AWS PRODUCTION IS 100% OPERATIONAL AND READY!")
        else:
            print(f"   Chat: FAILED - {r.status_code} - {r.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    aws_live_test()
