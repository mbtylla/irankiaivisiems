import requests
import os
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

csv_file = f"{folder}/stocks_{today}.csv"

response = requests.get(url, headers=headers, timeout=60)

if response.status_code != 200:
    raise Exception(f"Klaida: {response.status_code}")

data = response.json()

# --- Konvertuojam DICT → CSV
if isinstance(data, dict):

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # header
        writer.writerow(["model", "quantity"])

        # mapping taisyklės
mapping = {
    "OUT OF STOCK": 0,
    "LARGE QUANTITY": 100,
    "MEDIUM QUANTITY": 20,
    "SMALL QUANTITY": 1
}

if isinstance(data, dict):

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow(["model", "quantity"])

        for key, value in data.items():
            stock_text = value.get("stock", "").strip()

            if stock_text not in mapping:
                print("⚠️ Nežinomas stock tipas:", stock_text)

            quantity = mapping.get(stock_text, 0)

            writer.writerow([key, quantity])

    print("✅ CSV sukurtas:", csv_file)

else:
    raise Exception("Netinkamas formatas (tikėtasi dict)")
