
import json
import os
import requests

# os.system("curl  http://localhost:4040/api/tunnels > tunnels.json")

r = requests.get("http://localhost:4040/api/tunnels")
data = r.json()
ngrok_public_url = None

for tunnel in data["tunnels"]:
    if tunnel["proto"] == "http": ngrok_public_url = tunnel["public_url"]

print(ngrok_public_url)

