import sys
import os
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pipeline import run

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
def job():
    logger.info("Scheduler: iniciando ejecución programada...")
    try:
        run()
        logger.info("Scheduler: ejecución completada exitosamente.")
    except Exception as e:
        logger.error(f"Scheduler: error durante la ejecución: {e}")


if __name__ == "__main__":
    scheduler = BlockingScheduler()

    scheduler.add_job(
        job,
        trigger=CronTrigger(hour=8, minute=0),
        id="pipeline_diario",
        name="Pipeline FDA diario",
        replace_existing=True,
    )

    logger.info("Scheduler iniciado. Pipeline correrá todos los días a las 08:00.")
    logger.info("Presiona Ctrl+C para detener.")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler detenido manualmente.")
        scheduler.shutdown()

