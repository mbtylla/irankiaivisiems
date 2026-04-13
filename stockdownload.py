import requests
import os
from datetime import datetime

url = "https://b2b.toya.pl/api/Multimedia/Stocks"

api_key = os.environ.get("TOYA_API_KEY")
if not api_key:
    raise Exception("TOYA_API_KEY nerastas")

headers = {
    "Accept": "application/json",
    "Accept-Language": "en",
    "api-key": api_key
}

today = datetime.utcnow().strftime("%Y-%m-%d")
folder = "STOCKS"
os.makedirs(folder, exist_ok=True)

tmp_file = f"{folder}/stocks_{today}.tmp"
final_file = f"{folder}/stocks_{today}.json"

response = requests.get(url, headers=headers, timeout=60)

if response.status_code == 200 and response.content:
    with open(tmp_file, "wb") as f:
        f.write(response.content)

    os.replace(tmp_file, final_file)
    print("OK:", final_file)

elif response.status_code == 401:
    raise Exception("401 Unauthorized (API key problema)")

else:
    raise Exception(f"Klaida: {response.status_code}")
