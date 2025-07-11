import requests
import time

url = "https://www.amazon.com/dp/B0B17KHCQN"
api_base = "http://127.0.0.1:8000"

num_requests = 100  # Можем увеличить до 50–100 при стабильной работе


def test_endpoint(endpoint: str):
    errors = 0
    print(f"\nTesting {endpoint}...")
    for i in range(num_requests):
        start = time.time()
        try:
            response = requests.get(f"{api_base}/{endpoint}/", params={"uri": url}, timeout=30)
            duration = time.time() - start
            if response.status_code == 200 and "error" not in response.text:
                print(f"[{i+1}] OK ({duration:.2f}s)")
            else:
                print(f"[{i+1}] ❌ Response error: {response.status_code} / {response.text}")
                errors += 1
        except Exception as e:
            print(f"[{i+1}] ❌ Exception: {e}")
            errors += 1
    print(f"Done. {num_requests - errors} success / {errors} errors.")


if __name__ == "__main__":
    test_endpoint("price")
    test_endpoint("product")
