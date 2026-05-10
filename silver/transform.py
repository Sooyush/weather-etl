import pandas as pd
from datetime import datetime, timezone
from config.config import SILVER_DIR

def flatten_weather_record(raw: dict) -> dict:
    return {
        "city":             raw.get("name"),
        "country":          raw.get("sys", {}).get("country"),
        "latitude":         raw.get("coord", {}).get("lat"),
        "longitude":        raw.get("coord", {}).get("lon"),
        "weather_main":     raw.get("weather", [{}])[0].get("main"),
        "weather_desc":     raw.get("weather", [{}])[0].get("description"),
        "temp_c":           raw.get("main", {}).get("temp"),
        "feels_like_c":     raw.get("main", {}).get("feels_like"),
        "temp_min_c":       raw.get("main", {}).get("temp_min"),
        "temp_max_c":       raw.get("main", {}).get("temp_max"),
        "humidity_pct":     raw.get("main", {}).get("humidity"),
        "pressure_hpa":     raw.get("main", {}).get("pressure"),
        "wind_speed_ms":    raw.get("wind", {}).get("speed"),
        "wind_deg":         raw.get("wind", {}).get("deg"),
        "visibility_m":     raw.get("visibility"),
        "cloudiness_pct":   raw.get("clouds", {}).get("all"),
        "sunrise_utc":      datetime.fromtimestamp(
                                raw.get("sys", {}).get("sunrise", 0), tz=timezone.utc
                            ).isoformat(),
        "sunset_utc":       datetime.fromtimestamp(
                                raw.get("sys", {}).get("sunset", 0), tz=timezone.utc
                            ).isoformat(),
        "ingested_at_utc":  datetime.now(timezone.utc).isoformat(),
        "api_timestamp_utc": datetime.fromtimestamp(
                                raw.get("dt", 0), tz=timezone.utc
                            ).isoformat(),
    }

def transform_records(raw_payloads: list[dict]) -> pd.DataFrame:
    records = [flatten_weather_record(p["raw"]) for p in raw_payloads]
    df = pd.DataFrame(records)
    df = df.dropna(subset=["city", "temp_c"])
    df["temp_category"] = pd.cut(
        df["temp_c"],
        bins=[-float("inf"), 0, 10, 20, 30, float("inf")],
        labels=["Freezing", "Cold", "Mild", "Warm", "Hot"]
    )
    df["temp_category"] = df["temp_category"].astype(str)
    return df

def run_silver(raw_payloads: list[dict]) -> pd.DataFrame:
    print("\n=== SILVER: Transforming with Pandas ===")
    df = transform_records(raw_payloads)

    now = datetime.now(timezone.utc)
    folder = SILVER_DIR / now.strftime("%Y/%m/%d")
    folder.mkdir(parents=True, exist_ok=True)
    csv_path = folder / f"weather_{now.strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(csv_path, index=False)
    print(f"  [Silver] Saved → {csv_path} ({len(df)} rows)")
    return df