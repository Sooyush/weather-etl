import requests
import json
from datetime import datetime, timezone
from config.config import WEATHER_API_KEY, CITIES, API_BASE_URL, BRONZE_DIR

def fetch_weather(city: str) -> dict:
    params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
    response = requests.get(API_BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def save_to_bronze(data: dict, city: str) -> str:
    now = datetime.now(timezone.utc)
    folder = BRONZE_DIR / now.strftime("%Y/%m/%d")
    folder.mkdir(parents=True, exist_ok=True)

    filename = f"{city.lower().replace(' ', '_')}_{now.strftime('%Y%m%d_%H%M%S')}.json"
    path = folder / filename
    path.write_text(json.dumps(data, indent=2))
    print(f"  [Bronze] Saved → {path}")
    return str(path)

def run_bronze() -> list[dict]:
    print("\n=== BRONZE: Fetching from Weather API ===")
    results = []
    for city in CITIES:
        try:
            raw = fetch_weather(city)
            save_to_bronze(raw, city)
            results.append({"city": city, "raw": raw})
        except Exception as e:
            print(f"  [Bronze] ERROR for {city}: {e}")
    return results