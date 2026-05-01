import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json

def chat_loop():
    print("🤖 AI Dost - Interactive Mode")
    print("Type 'exit' or 'quit' to stop.")
    print("-" * 50)
    
    import time
    session_id = f"user_{int(time.time())}"
    url = 'http://localhost:8000/chat'
    
    while True:
        try:
            # Wait for user input
            user_input = input("\nYou: ")
            
            if user_input.lower() in ['exit', 'quit']:
                print("Alvida! 👋")
                break
                
            if not user_input.strip():
                continue
                
            payload = {
                'message': user_input,
                'session_id': session_id
            }
            
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                url, 
                data=data, 
                headers={
                    'Content-Type': 'application/json',
                    'X-API-Key': 'hackathon_super_secret_key_123'
                }
            )
            
            # Show a loading indicator
            print("AI Dost is typing...", end="\r")
            
            response = urllib.request.urlopen(req, timeout=120)
            result = json.loads(response.read().decode('utf-8'))
            
            # Clear the loading indicator
            print(" " * 20, end="\r")
            
            if result.get('scam_detected'):
                print(f"🚨 SCAM WARNING: {result.get('scam_warning')}")
                
            print(f"[AI Dost]: {result.get('reply')}")
            
        except KeyboardInterrupt:
            print("\nAlvida! 👋")
            break
        except Exception as e:
            # Clear the loading indicator
            print(" " * 20, end="\r")
            print(f"[System]: Error connecting to server - {e}")

if __name__ == "__main__":
    chat_loop()
