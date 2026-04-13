import requests
import os
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo

url = "https://b2b.toya.pl/api/Multimedia/Stocks"

api_key = os.environ.get("TOYA_API_KEY")
if not api_key:
    raise Exception("TOYA_API_KEY nerastas")

headers = {
    "Accept": "application/json",
    "Accept-Language": "en",
    "api-key": api_key
}

# Lietuvos laikas
lt_time = datetime.now(ZoneInfo("Europe/Vilnius"))
today = lt_time.strftime("%Y-%m-%d_%H-%M")

folder = "STOCKS"
os.makedirs(folder, exist_ok=True)

csv_file = f"{folder}/stocks_{today}.csv"
xml_file = f"{folder}/stocks_{today}.xml"

response = requests.get(url, headers=headers, timeout=60)

if response.status_code != 200:
    raise Exception(f"Klaida: {response.status_code}")

data = response.json()

# mapping taisyklės
mapping = {
    "OUT OF STOCK": 0,
    "LARGE QUANTITY": 100,
    "MEDIUM QUANTITY": 20,
    "SMALL QUANTITY": 1
}

# --- Tik jei dict
if isinstance(data, dict):

    # CSV
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

    # XML
    root = ET.Element("likuciai")

    for key, value in data.items():
        stock_text = value.get("stock", "").strip()
        quantity = mapping.get(stock_text, 0)

        row = ET.SubElement(root, "row")

        kodas = ET.SubElement(row, "kodas")
        kodas.text = str(key)

        kiekis = ET.SubElement(row, "I17_KIEKIS")
        kiekis.text = str(quantity)

    tree = ET.ElementTree(root)
    tree.write(xml_file, encoding="utf-8", xml_declaration=True)

    print("✅ XML sukurtas:", xml_file)

else:
    raise Exception("Netinkamas formatas (tikėtasi dict)")
