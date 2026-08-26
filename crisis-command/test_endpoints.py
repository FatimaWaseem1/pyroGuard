import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FLWR_MODEL_API_KEY", "DEMO_KEY")

ENDPOINTS = {
    "Ground Coordinator (GLM-5.2)": os.getenv("COORDINATOR_URL"),
    "Resource Allocator (Kimi-K2.7)": os.getenv("ALLOCATOR_URL"),
    "Safety Guard (Qwen3.5)": os.getenv("SAFETY_URL")
}


def test_single_endpoint(name: str, url: str) -> bool:
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"input": "Ping test", "stream": False}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        if response.status_code == 200:
            print(f"[SUCCESS] {name} is ONLINE (HTTP 200)")
            return True
        else:
            print(f"[WARNING] {name} returned HTTP {response.status_code}. Using Fallback.")
            return False
    except requests.exceptions.RequestException:
        print(f"[OFFLINE] {name} unreachable. Using Fallback Engine.")
        return False


def run_health_check():
    print("=" * 60)
    print("CRISIS COMMAND: ENDPOINT AUDIT")
    print("=" * 60)
    for name, url in ENDPOINTS.items():
        test_single_endpoint(name, url)
    print("=" * 60)


if __name__ == "__main__":
    run_health_check()