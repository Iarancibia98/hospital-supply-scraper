# 🏥 Hospital Supply Chain Intelligence

Monitor automatizado de escasez de medicamentos hospitalarios con análisis y dashboard.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automatizado-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Problema de negocio

Los hospitales necesitan monitorear constantemente la disponibilidad de medicamentos críticos. Una escasez no detectada a tiempo puede afectar directamente la atención de pacientes. Este sistema automatiza ese monitoreo extrayendo datos oficiales de la FDA diariamente.

---

## 🏗️ Arquitectura
```
FDA Drug Shortages (fda.gov)
         ↓
   Scraper Python
   requests + BeautifulSoup
         ↓
   Limpieza de datos
   Pandas
         ↓
   Base de datos
   SQLite
         ↓
   Motor de alertas
   Detección de cambios
         ↓
   Dashboard Streamlit
```

---

## 🛠️ Stack tecnológico

| Capa | Herramienta |
|------|-------------|
| Scraping | Python · requests · BeautifulSoup4 |
| Limpieza | Pandas |
| Base de datos | SQLite |
| Automatización local | APScheduler |
| Automatización nube | GitHub Actions |
| Dashboard | Streamlit · Plotly |

---

## 📁 Estructura del proyecto
```
hospital-supply-scraper/
├── .github/
│   └── workflows/
│       └── pipeline.yml      ← automatización en la nube
├── scraper/
│   ├── base_scraper.py       ← clase base con rate limiting y reintentos
│   └── fda_scraper.py        ← scraper FDA Drug Shortages
├── database/
│   ├── schema.sql            ← diseño de tablas e índices
│   ├── db.py                 ← conexión y carga a SQLite
│   └── analysis.sql          ← queries de análisis supply chain
├── processors/
│   └── alert_engine.py       ← motor de detección de cambios
├── dashboard/
│   └── app.py                ← dashboard Streamlit
├── data/
│   └── *.csv                 ← datos históricos por fecha
├── pipeline.py               ← orquesta el flujo completo
├── scheduler.py              ← ejecución local automática diaria
└── requirements.txt
```

---

## 🚀 Instalación y uso
```bash
# 1. Clonar el repositorio
git clone https://github.com/Iarancibia98/hospital-supply-scraper.git
cd hospital-supply-scraper

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar el pipeline
python pipeline.py

# 5. Lanzar el dashboard
streamlit run dashboard/app.py

# 6. Automatización diaria
python scheduler.py
```

---

## 📊 Insights encontrados
- **71 medicamentos** en escasez activa al 16 de marzo 2026
- **5 medicamentos** con escasez recientemente resuelta
- Medicamentos críticos en escasez: anestésicos, soluciones IV, oncológicos
- Sistema acumulando historial desde el 13 de marzo 2026

---

## ⚙️ Automatización

El pipeline corre automáticamente de dos formas.

**Local** con APScheduler todos los días a las 08:00 AM mientras el computador esté encendido.

**Nube** con GitHub Actions todos los días a las 11:00 UTC independientemente del estado del computador.

---

## ⚖️ Ética y legalidad

- Solo fuentes públicas y oficiales (FDA.gov)
- Rate limiting implementado para no saturar servidores
- Sin almacenamiento de información personal ni sensible

---

## 👤 Autor

**Ivan Arancibia** — [@Iarancibia98](https://github.com/Iarancibia98)
