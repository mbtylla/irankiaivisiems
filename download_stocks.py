import requests
import os
import csv
import json
import xml.etree.ElementTree as ET

url = "https://b2b.toya.pl/api/Multimedia/Stocks"

api_key = os.environ.get("TOYA_API_KEY")
if not api_key:
    raise Exception("TOYA_API_KEY nerastas")

headers = {
    "Accept": "application/json",
    "Accept-Language": "en",
    "api-key": api_key
}

folder = "STOCKS"
os.makedirs(folder, exist_ok=True)

csv_file = f"{folder}/toya_stocks.csv"
xml_file = f"{folder}/toya_stocks.xml"
delta_xml_file = f"{folder}/toya_stocks_delta.xml"

previous_snapshot_file = f"{folder}/previous_snapshot.json"
current_snapshot_file = f"{folder}/current_snapshot.json"

response = requests.get(url, headers=headers, timeout=60)

if response.status_code != 200:
    raise Exception(f"Klaida: {response.status_code}")

data = response.json()

mapping = {
    "OUT OF STOCK": 0,
    "LARGE QUANTITY": 100,
    "MEDIUM QUANTITY": 20,
    "SMALL QUANTITY": 0
}

if not isinstance(data, dict):
    raise Exception("Netinkamas formatas (tikėtasi dict)")


def normalize_data(api_data, mapping_dict):
    """
    API atsakymą paverčia tik į YT- prekes:
    {
        "YT-123": 20,
        "YT-999": 0
    }
    """
    result = {}

    for key, value in api_data.items():
        model = str(key).strip()

        # Imam tik TOYA YT- prekes
        if not model.startswith("YT-"):
            continue

        stock_text = value.get("stock", "").strip()

        if stock_text not in mapping_dict:
            print("⚠️ Nežinomas stock tipas:", stock_text)

        quantity = mapping_dict.get(stock_text, 0)
        result[model] = int(quantity)

    return result

def save_csv(snapshot, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["model", "quantity"])

        for model, quantity in snapshot.items():
            writer.writerow([model, quantity])

    print("✅ CSV sukurtas:", path)


def save_xml(snapshot, path):
    root = ET.Element("likuciai")

    for model, quantity in snapshot.items():
        row = ET.SubElement(root, "row")

        kodas = ET.SubElement(row, "kodas")
        kodas.text = str(model)

        kiekis = ET.SubElement(row, "I17_KIEKIS")
        kiekis.text = str(quantity)

    tree = ET.ElementTree(root)
    tree.write(path, encoding="utf-8", xml_declaration=True)

    print("✅ XML sukurtas:", path)


def load_previous_snapshot(path):
    if not os.path.exists(path):
        print("ℹ️ Ankstesnio snapshot nėra, laikom kad tai pirmas paleidimas")
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_snapshot(snapshot, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2, sort_keys=True)

    print("✅ Snapshot išsaugotas:", path)


def build_delta(previous_snapshot, current_snapshot):
    """
    Grąžina tik pasikeitimus.
    Taip pat jei modelis buvo anksčiau, o dabar dingo,
    į delta dedam su kiekiu 0.
    """
    delta = {}

    all_models = set(previous_snapshot.keys()) | set(current_snapshot.keys())

    for model in sorted(all_models):
        old_qty = int(previous_snapshot.get(model, 0))
        new_qty = int(current_snapshot.get(model, 0))

        if old_qty != new_qty:
            delta[model] = new_qty

    return delta


current_snapshot = normalize_data(data, mapping)

# 1. išsaugom full CSV
save_csv(current_snapshot, csv_file)

# 2. išsaugom full XML
save_xml(current_snapshot, xml_file)

# 3. užkraunam ankstesnį snapshot
previous_snapshot = load_previous_snapshot(previous_snapshot_file)

# 4. pastatom delta
delta_snapshot = build_delta(previous_snapshot, current_snapshot)

# 5. išsaugom delta XML
save_xml(delta_snapshot, delta_xml_file)

print(f"✅ Delta įrašų kiekis: {len(delta_snapshot)}")

# 6. išsaugom current snapshot
save_snapshot(current_snapshot, current_snapshot_file)

# 7. perrašom previous snapshot nauja būsena kitam paleidimui
save_snapshot(current_snapshot, previous_snapshot_file)
