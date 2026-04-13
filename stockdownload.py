import requests

# API nustatymai
url = "https://b2b.toya.pl/api/Multimedia/Stocks"
headers = {
    "accept": "text/plain",
    "Accept-Language": "en",
    "api-key": "99264a45c572c1c9697dda1270f3320cc936b5d9d5add9e2de519e18ff460e88"
}

# Kur saugoti failą
output_file = "stocks.json"  # gali keisti į .xml ar .txt jei reikia

try:
    response = requests.get(url, headers=headers, timeout=60)

    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        print("✅ Failas sėkmingai išsaugotas:", output_file)
    else:
        print(f"❌ Klaida: {response.status_code}")
        print(response.text)

except Exception as e:
    print("❌ Klaida:", e)
