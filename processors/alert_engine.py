import logging
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)


class AlertEngine:

    def __init__(self, db):
        self.db = db

    def run(self):
        logger.info("=== Motor de Alertas ===")
        alertas = []

        alertas += self._detectar_nuevas_escaseces()
        alertas += self._detectar_escaseces_resueltas()

        if not alertas:
            logger.info("Sin alertas nuevas hoy.")
            return 0

        self._guardar_alertas(alertas)
        logger.info(f"Alertas generadas: {len(alertas)}")
        return len(alertas)

    def _get_fecha_anterior(self):
        hoy = datetime.today().strftime("%Y-%m-%d")
        resultado = self.db.query(f"""
            SELECT MAX(date_scraped) as fecha
            FROM medical_products
            WHERE date_scraped < '{hoy}'
        """)
        if resultado.empty or resultado["fecha"][0] is None:
            return None
        return resultado["fecha"][0]

    def _detectar_nuevas_escaseces(self):
        hoy = datetime.today().strftime("%Y-%m-%d")
        ayer = self._get_fecha_anterior()

        if ayer is None:
            logger.info("Sin datos anteriores para comparar.")
            return []

        logger.info(f"Comparando {hoy} vs {ayer}")

        query_hoy = f"""
            SELECT product_name FROM medical_products
            WHERE status = 'Currently in Shortage'
            AND date_scraped = '{hoy}'
        """

        query_ayer = f"""
            SELECT product_name FROM medical_products
            WHERE date_scraped = '{ayer}'
        """

        df_hoy  = self.db.query(query_hoy)
        df_ayer = self.db.query(query_ayer)

        if df_ayer.empty:
            logger.info("Sin datos anteriores para comparar.")
            return []

        nuevos = set(df_hoy["product_name"]) - set(df_ayer["product_name"])

        alertas = []
        for producto in nuevos:
            alertas.append({
                "product_name": producto,
                "alert_type":   "nueva_escasez",
                "message":      f"{producto} entró en escasez el {hoy}",
                "triggered_at": hoy,
            })
            logger.warning(f"ALERTA nueva escasez: {producto}")

        return alertas

    def _detectar_escaseces_resueltas(self):
        hoy = datetime.today().strftime("%Y-%m-%d")
        ayer = self._get_fecha_anterior()

        if ayer is None:
            return []

        query_hoy = f"""
            SELECT product_name FROM medical_products
            WHERE status = 'Resolved Shortage'
            AND date_scraped = '{hoy}'
        """

        query_ayer = f"""
            SELECT product_name FROM medical_products
            WHERE status = 'Currently in Shortage'
            AND date_scraped = '{ayer}'
        """

        df_hoy  = self.db.query(query_hoy)
        df_ayer = self.db.query(query_ayer)

        if df_ayer.empty or df_hoy.empty:
            return []

        resueltos = set(df_hoy["product_name"]) & set(df_ayer["product_name"])

        alertas = []
        for producto in resueltos:
            alertas.append({
                "product_name": producto,
                "alert_type":   "escasez_resuelta",
                "message":      f"{producto} resolvió su escasez el {hoy}",
                "triggered_at": hoy,
            })
            logger.info(f"ALERTA escasez resuelta: {producto}")

        return alertas

    def _guardar_alertas(self, alertas):
        if not alertas:
            return

        df_alertas = pd.DataFrame(alertas)

        with __import__('sqlite3').connect(self.db.db_path) as conn:
            df_alertas.to_sql("alerts", conn, if_exists="append", index=False)

        logger.info(f"Guardadas {len(df_alertas)} alertas en la base de datos.")


if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from database.db import DB

    db = DB()
    engine = AlertEngine(db)
    total = engine.run()
    print(f"\n✅ Motor de alertas completado: {total} alertas generadas")
