import sqlite3
import pandas as pd
from config.config import DB_PATH

DDL = """
CREATE TABLE IF NOT EXISTS weather_fact (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    city                TEXT,
    country             TEXT,
    latitude            REAL,
    longitude           REAL,
    weather_main        TEXT,
    weather_desc        TEXT,
    temp_c              REAL,
    feels_like_c        REAL,
    temp_min_c          REAL,
    temp_max_c          REAL,
    humidity_pct        INTEGER,
    pressure_hpa        INTEGER,
    wind_speed_ms       REAL,
    wind_deg            INTEGER,
    visibility_m        INTEGER,
    cloudiness_pct      INTEGER,
    sunrise_utc         TEXT,
    sunset_utc          TEXT,
    ingested_at_utc     TEXT,
    api_timestamp_utc   TEXT,
    temp_category       TEXT
);
"""

def run_gold(df: pd.DataFrame):
    print("\n=== GOLD: Loading to SQLite ===")
    conn = sqlite3.connect(DB_PATH)
    conn.execute(DDL)
    df.to_sql("weather_fact", conn, if_exists="append", index=False)
    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM weather_fact").fetchone()[0]
    print(f"  [Gold] Inserted {len(df)} rows — total rows in DB: {count}")
    conn.close()