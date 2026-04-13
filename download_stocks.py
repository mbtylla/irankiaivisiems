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

# jei ne list, bandome rasti viduje
if isinstance(data, dict):
    # dažniausi variantai
    if "data" in data:
        data = data["data"]
    elif "items" in data:
        data = data["items"]
    else:
        raise Exception(f"Nežinoma JSON struktūra: {list(data.keys())}")

# --- Išsaugom JSON (optional, gali ištrinti jei nereikia)
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# --- Konvertuojam į CSV (DICT variantas)
if isinstance(data, dict):

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # header
        writer.writerow(["model", "quantity"])

        # eilutės
        for key, value in data.items():
            writer.writerow([key, value])

    print("✅ CSV sukurtas:", csv_file)

else:
    raise Exception("Nežinomas formatas (ne dict)")
