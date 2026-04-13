import requests
import os
import json
import csv
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

json_file = f"{folder}/stocks_{today}.json"
csv_file = f"{folder}/stocks_{today}.csv"

response = requests.get(url, headers=headers, timeout=60)

if response.status_code != 200:
    raise Exception(f"Klaida: {response.status_code}")

data = response.json()

# --- Išsaugom JSON (optional, gali ištrinti jei nereikia)
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# --- Konvertuojam į CSV
if isinstance(data, list) and len(data) > 0:
    keys = data[0].keys()

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

    print("✅ CSV sukurtas:", csv_file)

else:
    raise Exception("Netinkamas JSON formatas (ne sąrašas)")
