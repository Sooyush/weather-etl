import sys
import logging
from datetime import datetime, timezone
from bronze.ingest import run_bronze
from silver.transform import run_silver
from gold.load import run_gold

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def run_pipeline():
    start = datetime.now(timezone.utc)
    logging.info(f"Pipeline started at {start.isoformat()}")
    try:
        raw_payloads = run_bronze()
        if not raw_payloads:
            raise RuntimeError("Bronze layer returned no data.")
        df = run_silver(raw_payloads)
        if df.empty:
            raise RuntimeError("Silver layer produced empty DataFrame.")
        run_gold(df)
        elapsed = (datetime.now(timezone.utc) - start).seconds
        logging.info(f"Pipeline completed in {elapsed}s.")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()