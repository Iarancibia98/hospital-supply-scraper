import sys
import os
import pandas as pd
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper.base_scraper import BaseScraper, logger
FDA_URL = "https://www.accessdata.fda.gov/scripts/drugshortages/dsp_SearchResults.cfm?T=N&ST=C"
OUTPUT_DIR = "data"

class FDAScraper(BaseScraper):

    def __init__(self):
        super().__init__(delay=3.0, max_retries=3)

    def scrape(self):
        logger.info("=== Iniciando FDA Drug Shortages Scraper ===")
        records = self._extraer_tabla()

        if not records:
            logger.warning("No se obtuvieron datos.")
            return pd.DataFrame()

        df = pd.DataFrame(records)
        df = self._limpiar(df)

        logger.info(f"Total de registros obtenidos: {len(df)}")
        return df
    
    def _extraer_tabla(self):
        response = self.get(FDA_URL)
        if response is None:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        tabla = soup.find("table", {"id": "cont"})

        if tabla is None:
            logger.error("No se encontró la tabla en la página.")
            return []

        filas = tabla.find_all("tr")[1:]
        logger.info(f"Filas encontradas: {len(filas)}")

        records = []

        for fila in filas:
            celdas = fila.find_all("td")
            if len(celdas) < 2:
                continue

            links = celdas[0].find_all("a")
            if len(links) < 2:
                continue

            nombre = links[1].get_text(strip=True)
            estado = celdas[1].get_text(strip=True)

            records.append({
                "product_name": nombre,
                "status":       estado,
                "date_scraped": self.today(),
                "source":       FDA_URL,
            })

        return records
    
    def _limpiar(self, df):
        df["product_name"] = df["product_name"].str.strip().str.title()
        df["status"]       = df["status"].str.strip()
        df = df.dropna(subset=["product_name"])
        df = df[df["product_name"] != ""]
        df = df.drop_duplicates(subset=["product_name", "date_scraped"])
        return df.reset_index(drop=True)
    
    def save_csv(self, df):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filename = f"{OUTPUT_DIR}/fda_shortages_{self.today()}.csv"
        df.to_csv(filename, index=False, encoding="utf-8")
        logger.info(f"Datos guardados en: {filename}")
        return filename


if __name__ == "__main__":
    scraper = FDAScraper()
    df = scraper.scrape()

    if not df.empty:
        path = scraper.save_csv(df)
        print(f"\n✅ Scraping completado: {len(df)} registros")
        print(f"📁 Archivo guardado en: {path}")
        print("\n📋 Primeras 5 filas:")
        print(df.head())
    else:
        print("\n❌ No se obtuvieron datos.")