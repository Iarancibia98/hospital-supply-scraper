import os
import sqlite3
import pandas as pd
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "healthcare.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

class DB:

    def __init__(self, db_path=DB_PATH):
        self.db_path = os.path.abspath(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_schema()

    def _init_schema(self):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            sql = f.read()

        with sqlite3.connect(self.db_path) as conn:
            for statement in sql.split(";"):
                stmt = statement.strip()
                if stmt and not stmt.startswith("--"):
                    try:
                        conn.execute(stmt)
                    except sqlite3.Error as e:
                        logger.debug(f"Schema ignorado: {e}")
            conn.commit()

        logger.info(f"Base de datos lista: {self.db_path}")
    
    def load(self, df, table="medical_products"):
        if df.empty:
            logger.warning("DataFrame vacío, nada que cargar.")
            return 0

        valid_cols = self._get_columns(table)
        cols_to_insert = [c for c in df.columns if c in valid_cols]
        df_clean = df[cols_to_insert].copy()

        with sqlite3.connect(self.db_path) as conn:
            df_clean.to_sql(table, conn, if_exists="append", index=False)

        logger.info(f"Insertadas {len(df_clean)} filas en '{table}'")
        return len(df_clean)
    
    def _get_columns(self, table):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(f"PRAGMA table_info({table})")
            return [row[1] for row in cursor.fetchall()]

    def count(self, table="medical_products"):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
            return cursor.fetchone()[0]

    def query(self, sql):
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(sql, conn)

