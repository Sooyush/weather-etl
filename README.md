# Weather ETL Pipeline 🌦️

A fully automated data pipeline that fetches live weather data every day, processes it through three layers (Bronze → Silver → Gold), stores it in a database, and visualises it in Power BI — all for **$0**, using GitHub Actions as the scheduler.

---

## What it does (simple version)

Every day at 6AM UTC, GitHub automatically runs a Python script that:

1. **Fetches** live weather data for 5 cities from a free API
2. **Saves** the raw data as JSON files *(Bronze)*
3. **Cleans** the data into a tidy table *(Silver)*
4. **Stores** it in a database *(Gold)*
5. **Commits** all the new files back to this repo automatically

You then open Power BI, click Refresh, and your dashboard updates with the latest data.

---

## Tech Stack

| Tool | Role | Cost |
|---|---|---|
| OpenWeatherMap API | Live weather data source | Free |
| Python + Pandas | Data ingestion & transformation | Free |
| GitHub Actions | Daily pipeline scheduler | Free |
| SQLite | Gold layer database | Free |
| Power BI Desktop | Dashboard & visualisation | Free |

**Total cost: $0 forever.**

---

## Project Structure

```
weather-etl/
├── .github/
│   └── workflows/
│       └── etl_pipeline.yml   # GitHub Actions — runs pipeline daily
├── data/
│   ├── bronze/                # Raw JSON files from the API
│   ├── silver/                # Cleaned CSV files
│   └── weather.db             # SQLite Gold database (auto-updated daily)
├── config/
│   └── config.py              # API keys, file paths, city list
├── bronze/
│   └── ingest.py              # Layer 1: fetch & save raw JSON
├── silver/
│   └── transform.py           # Layer 2: clean & flatten with Pandas
├── gold/
│   └── load.py                # Layer 3: load into SQLite
├── pipeline.py                # Orchestrator — runs all 3 layers
├── generate_sample.py         # Generates 30 days of sample data for Power BI
├── refresh.ps1                # PowerShell script to git pull before opening Power BI
└── requirements.txt           # Python dependencies
```

---

## Architecture — Medallion Pattern

```
OpenWeatherMap API
       │
       ▼
  BRONZE LAYER
  Raw JSON files
  data/bronze/YYYY/MM/DD/
       │
       ▼
  SILVER LAYER
  Cleaned CSV files
  data/silver/YYYY/MM/DD/
       │
       ▼
  GOLD LAYER
  SQLite database
  data/weather.db
       │
       ▼
  Power BI Dashboard
  KPIs, trends, map
```

The **Medallion Architecture** is an industry-standard data engineering pattern where data flows through three quality layers:

- **Bronze** — raw, unmodified source data (JSON as returned by the API)
- **Silver** — cleaned, flattened, and enriched (nulls removed, columns renamed, categories derived)
- **Gold** — structured and query-ready for reporting tools

---

## Detailed Explanation

### 1. Data Source — OpenWeatherMap API

The pipeline calls the [OpenWeatherMap Current Weather API](https://openweathermap.org/api) for 5 cities: London, Dubai, New York, Tokyo, and Sydney. The free tier allows 1,000 calls/day — far more than needed. Each call returns a nested JSON object containing temperature, humidity, wind speed, pressure, visibility, sunrise/sunset times, and weather conditions.

### 2. Bronze Layer — `bronze/ingest.py`

The raw API response is saved as-is to `data/bronze/YYYY/MM/DD/city_timestamp.json`. No transformations are applied — the goal is to preserve the original source data exactly as received. This is critical for auditability: if a bug is found in the transformation logic later, the raw data can be reprocessed without re-calling the API.

### 3. Silver Layer — `silver/transform.py`

The nested JSON is flattened into a clean tabular structure using Pandas. Key transformations applied:

- Nested fields extracted (e.g. `main.temp` → `temp_c`, `sys.country` → `country`)
- Unix timestamps converted to readable ISO 8601 UTC strings
- Rows with missing city or temperature dropped (data quality check)
- A derived `temp_category` column added (`Freezing / Cold / Mild / Warm / Hot`) using `pd.cut()`
- Output saved as a CSV partitioned by date: `data/silver/YYYY/MM/DD/weather_timestamp.csv`

### 4. Gold Layer — `gold/load.py`

The cleaned DataFrame is appended into a SQLite database (`data/weather.db`) in a table called `weather_fact`. SQLite was chosen over Azure SQL Server to keep the project completely free — it is a single file, requires no server, and is directly readable by Power BI via ODBC or Python connector. The table uses `AUTOINCREMENT` primary keys and accumulates all historical runs, enabling time-series analysis.

### 5. Orchestration — GitHub Actions

The pipeline is scheduled via a GitHub Actions cron workflow (`.github/workflows/etl_pipeline.yml`) that runs daily at 06:00 UTC on a free GitHub-hosted Ubuntu runner. After the pipeline completes, the workflow automatically commits and pushes the updated `weather.db`, silver CSVs, and bronze JSONs back to the repository using the built-in `GITHUB_TOKEN`. The `WEATHER_API_KEY` is stored as an encrypted GitHub Secret and injected as an environment variable at runtime — it is never exposed in the codebase.

### 6. Power BI Dashboard

Power BI Desktop connects to the local cloned repo's `data/silver/` folder using the **Folder connector**, which combines all CSVs into a single unified table automatically. Three report pages are built:

- **Overview** — KPI cards (avg temp, humidity, wind), bar chart of temp by city, donut chart of weather conditions, city slicer
- **Trends** — line charts showing temperature and humidity over time per city, scatter plot of temp vs humidity
- **Map** — bubble map using latitude/longitude with bubble size representing temperature

To refresh data, run `refresh.ps1` (which does a `git pull`) then click Refresh in Power BI Desktop.

---

## Setup Instructions

### Prerequisites

- Python 3.11+
- Git
- Power BI Desktop (free download from Microsoft)
- Free API key from [openweathermap.org](https://openweathermap.org/api)

### Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/Sooyush/weather-etl.git
cd weather-etl

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create a .env file (never commit this)
echo WEATHER_API_KEY=your_key_here > .env

# 4. Run the pipeline
python pipeline.py

# 5. Verify output
ls data/weather.db
ls data/silver/
```

### GitHub Actions Setup

1. Go to your repo → **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `WEATHER_API_KEY`, Value: your OpenWeatherMap key
4. Push code to `main` — the workflow runs automatically every day at 06:00 UTC
5. To trigger manually: **Actions tab → Weather ETL Pipeline → Run workflow**

### Power BI Setup

1. Generate sample data first (optional):
   ```bash
   python generate_sample.py
   ```
2. Open Power BI Desktop → **Get Data → Folder**
3. Point to your local `data/silver/` directory
4. Click **Combine Files** when prompted
5. Add the DAX measures listed below
6. Build visuals across 3 pages (Overview, Trends, Map)

### DAX Measures

```dax
Avg Temp (°C) = AVERAGE(weather_sample[temp_c])
Max Temp (°C) = MAX(weather_sample[temp_c])
Min Temp (°C) = MIN(weather_sample[temp_c])
Avg Humidity (%) = AVERAGE(weather_sample[humidity_pct])
Avg Wind (m/s) = AVERAGE(weather_sample[wind_speed_ms])
Hottest City =
CALCULATE(
    FIRSTNONBLANK(weather_sample[city], 1),
    FILTER(
        ALL(weather_sample),
        weather_sample[temp_c] = CALCULATE(MAX(weather_sample[temp_c]), ALL(weather_sample))
    )
)
```

---

## Daily Refresh Workflow

```
06:00 UTC — GitHub Actions triggers automatically
          → pipeline.py runs on Ubuntu runner
          → Bronze JSON files written
          → Silver CSV written
          → Gold SQLite updated
          → All files committed & pushed to repo

Your local machine (whenever you want to view):
          → Run refresh.ps1  (does git pull)
          → Open Power BI Desktop
          → Click Refresh
          → Dashboard shows latest data
```

---

## Key Concepts Demonstrated

- **Medallion Architecture** (Bronze / Silver / Gold) — industry-standard lakehouse pattern
- **REST API ingestion** — authenticated HTTP requests, JSON parsing
- **Data transformation** — flattening nested JSON, type casting, null handling, derived columns
- **Pipeline orchestration** — automated scheduling without a paid orchestration tool
- **CI/CD for data** — using GitHub Actions as a lightweight data scheduler
- **Secrets management** — environment variables via GitHub Secrets, never hardcoded
- **Incremental loading** — appending new rows to SQLite on each run, preserving history
- **Data visualisation** — KPI cards, time-series trends, geographic map in Power BI
