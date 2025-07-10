import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"
ENDPOINTS = ["/product", "/price"]

# 17 ссылок
urls = [
    "https://www.amazon.com/SANSUI-Monitor-24-Ultra-Slim-Ergonomic-ES-24F1/dp/B0B17KHCQN?th=1",
    "https://www.amazon.com/Amazon-Basics-Compatible-Adaptive-Response/dp/B0CP7SV7XV?th=1",
    "https://www.amazon.com/PHILIPS-Frameless-Replacement-Warranty-241V8LB/dp/B0C8ZKV5R9?th=1",
    "https://www.amazon.com/Amazon-Basics-Monitor-Compatible-Speakers/dp/B0CP7TRZWR?th=1",
    "https://www.amazon.com/Amazon-Basics-Monitor-Compatible-Speakers/dp/B0CP7TRZWR?th=1",
    "https://www.amazon.com/KTC-inch-Monitor-Mountable-Adjustable/dp/B0CHRPB1X9?th=1",
    "https://www.amazon.com/KTC-inch-Monitor-Mountable-Adjustable/dp/B0CHRPB1X9?th=1",
    "https://www.amazon.com/KTC-Computer-Monitor-Adaptive-Sync-H25B7/dp/B0DK3FKSW1?th=1",
    "https://www.amazon.com/acer-Ultra-Slim-Adaptive-Sync-FreeSync-Compatible/dp/B0D2RW526R?th=1",
    "https://www.amazon.com/KTC-Computer-FreeSync-Contrast-Ergonomic/dp/B0DRCXZN53?th=1",
    "https://www.amazon.com/KTC-Computer-FreeSync-Contrast-Ergonomic/dp/B0DRCXZN53?th=1",
    "https://www.amazon.com/AOC-24B2H2-Frameless-1920x1080-Compatible/dp/B0C8ZJP65J?th=1",
    "https://www.amazon.com/Sceptre-Curved-Monitor-Speakers-C248W-1920RN/dp/B07KXSR99Y?th=1",
    "https://www.amazon.com/XGaming-Monitor-100Hz-1080P-Built/dp/B0C6K95SGQ?th=1",
    "https://www.amazon.com/SH242Y-G0bih-Ultra-Thin-Adaptive-Sync-Compatible/dp/B0DFVTVLPH?th=1",
    "https://www.amazon.com/Futuzen-1920x1080-Computer-Monitor-Mountable/dp/B0DQXR49GK?th=1",
    "https://www.amazon.com/SAMSUNG-Essential-Ergonomic-Advanced-LS24D304GANXZA/dp/B0DK468KVS?th=1"
]

for url in urls:
    print(f"\n🟡 Testing URL: {url}\n")

    for endpoint in ENDPOINTS:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", params={"uri": url}, timeout=30)
            response.raise_for_status()

            parsed = response.json()
            print(f"✅ {endpoint} result:")
            print(json.dumps(parsed, indent=4, ensure_ascii=False))
        except requests.RequestException as e:
            print(f"❌ Error for {endpoint} with URL: {url}")
            print(e)

        time.sleep(1.5)  # задержка между запросами, чтобы снизить нагрузку
