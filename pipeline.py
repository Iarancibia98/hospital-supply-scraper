import sys
import os
import logging
from processors.alert_engine import AlertEngine

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.fda_scraper import FDAScraper
from database.db import DB

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

def run():
    logger.info("=" * 55)
    logger.info("  HOSPITAL SUPPLY CHAIN — PIPELINE")
    logger.info("=" * 55)

    logger.info("\n[1/3] Ejecutando scraper FDA...")
    scraper = FDAScraper()
    df = scraper.scrape()

    if df.empty:
        logger.error("Sin datos. Abortando pipeline.")
        return

    logger.info("\n[2/3] Guardando CSV de respaldo...")
    csv_path = scraper.save_csv(df)

    logger.info("\n[3/3] Cargando datos en SQLite...")
    db = DB()
    db.load(df)
    logger.info("\n[4/4] Ejecutando motor de alertas...")
    engine = AlertEngine(db)
    total_alertas = engine.run()

    logger.info("\n" + "=" * 55)
    logger.info("  PIPELINE COMPLETADO")
    logger.info(f"  Registros scrapeados : {len(df)}")
    logger.info(f"  CSV guardado en      : {csv_path}")
    logger.info(f"  Total filas en DB    : {db.count()}")
    logger.info(f"  Alertas generadas    : {total_alertas}")
    logger.info("=" * 55)

    print("\n📋 Vista previa:")
    print(df[["product_name", "status", "date_scraped"]].head(10).to_string(index=False))


if __name__ == "__main__":
    run()