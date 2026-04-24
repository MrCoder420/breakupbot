import requests
import time
import random

def run():
    base = "http://localhost:8001"
    user = f"nirmal_healing_{random.randint(100, 999)}"
    pwd = "healingpassword123"
    
    print(f"Starting long-form conversation test for user: {user}")
    
    # Register/Login
    requests.post(f"{base}/register", json={"username": user, "password": pwd})
    log = requests.post(f"{base}/login", json={"username": user, "password": pwd})
    token = log.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    prompts = [
        "Hi Eleanor, I feel completely lost and alone today.",
        "It's about Maya. We broke up yesterday after 3 years together.",
        "I can't stop crying. Every corner of my house reminds me of her.",
        "I want to text her so badly. I feel like I need her voice to stop the pain.",
        "You're right about No Contact, but it's like a physical addiction. It hurts.",
        "I keep thinking it's my fault. If I had been more attentive, she would've stayed.",
        "I feel like a total failure. I'm 28 and starting over feels impossible.",
        "The anger is coming now. How could she just throw away 3 years like they were nothing?",
        "I managing to drink some water and eat some soup today. Is that a victory?",
        "I saw a photo of us on my laptop and it broke me all over again.",
        "I'm terrified that she's already moving on or talking to someone else.",
        "Should I throw away all her old gifts and letters? Or is that too drastic?",
        "I tried to walk for 10 minutes like you said. I saw a tree we used to sit under.",
        "Will this pain ever actually go away? It feels like it's permanent.",
        "Thank you for being here, Eleanor. I think I'm going to try to sleep now."
    ]
    
    for i, p in enumerate(prompts):
        print(f"\n[Turn {i+1}/15] USER: {p}")
        try:
            res = requests.post(f"{base}/chat", json={"message": p}, headers=headers)
            res.raise_for_status()
            eleanor = res.json().get("response")
            print(f"ELEANOR: {eleanor}")
            time.sleep(0.5)
        except Exception as e:
            print(f"Error at turn {i+1}: {e}")
            break
            
    print("\n" + "="*40)
    print("FINISHED LONG CONVERSATION TEST")
    print(f"USERNAME FOR YOU: {user}")
    print(f"PASSWORD FOR YOU: {pwd}")
    print("="*40)

if __name__ == "__main__":
    run()
