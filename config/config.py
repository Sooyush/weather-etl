import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Weather API
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
CITIES = ["London", "Dubai", "New York", "Tokyo", "Sydney"]
API_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Local paths (work both locally and in GitHub Actions runner)
BASE_DIR    = Path(__file__).resolve().parent.parent
BRONZE_DIR  = BASE_DIR / "data" / "bronze"
SILVER_DIR  = BASE_DIR / "data" / "silver"
DB_PATH     = BASE_DIR / "data" / "weather.db"

# Create dirs if they don't exist
BRONZE_DIR.mkdir(parents=True, exist_ok=True)
SILVER_DIR.mkdir(parents=True, exist_ok=True)