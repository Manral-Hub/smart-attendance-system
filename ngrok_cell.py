from pyngrok import ngrok
import threading
import time
import subprocess
import os

# Set ngrok auth token
ngrok.set_auth_token("YOUR_NGROK_AUTH_TOKEN_HERE")

# Kill all existing ngrok tunnels first
ngrok.kill()

# Kill any existing Flask processes on port 5000
os.system("fuser -k 5000/tcp 2>/dev/null")

# Start Flask in background
def run_flask():
    os.system("python app.py")

flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

# Wait a moment for Flask to start
time.sleep(3)

# Create ngrok tunnel
public_url = ngrok.connect(5000)
print("=" * 60)
print("Flask app is running!")
print("=" * 60)
print(f"Public URL: {public_url}")
print("=" * 60)
print("\nOpen this URL in your browser to access the app.")
print("Share this URL with judges for the demo.")
print("\nNote: The URL will be active as long as this cell is running.")

print("=" * 60)
