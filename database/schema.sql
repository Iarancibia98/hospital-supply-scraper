CREATE TABLE IF NOT EXISTS medical_products (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name  TEXT    NOT NULL,
    status        TEXT,
    date_scraped  TEXT    NOT NULL,
    source        TEXT,
    created_at    TEXT    DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_product_name  ON medical_products (product_name);
CREATE INDEX IF NOT EXISTS idx_date_scraped  ON medical_products (date_scraped);
CREATE INDEX IF NOT EXISTS idx_status        ON medical_products (status);
CREATE TABLE IF NOT EXISTS alerts (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name  TEXT    NOT NULL,
    alert_type    TEXT    NOT NULL,
    message       TEXT,
    triggered_at  TEXT    DEFAULT (datetime('now'))
);

-- =============================================================
-- QUERIES DE ANÁLISIS
-- =============================================================

-- 1. Total de medicamentos en escasez activa hoy
-- SELECT COUNT(*) as total_escasez
-- FROM medical_products
-- WHERE status = 'Currently in Shortage'
-- AND date_scraped = DATE('now');

-- 2. Medicamentos que llevan más de 7 días en escasez
-- SELECT product_name, MIN(date_scraped) as primer_registro
-- FROM medical_products
-- WHERE status = 'Currently in Shortage'
-- GROUP BY product_name
-- HAVING MIN(date_scraped) <= DATE('now', '-7 days');

-- 3. Medicamentos nuevos en escasez esta semana
-- SELECT product_name, date_scraped
-- FROM medical_products
-- WHERE status = 'Currently in Shortage'
-- AND date_scraped >= DATE('now', '-7 days')
-- ORDER BY date_scraped DESC;

-- 4. Historial de un medicamento específico
-- SELECT product_name, status, date_scraped
-- FROM medical_products
-- WHERE product_name = 'Albuterol Sulfate Solution'
-- ORDER BY date_scraped ASC;

-- 5. Escaseces resueltas este mes
-- SELECT product_name, date_scraped
-- FROM medical_products
-- WHERE status = 'Resolved Shortage'
-- AND date_scraped >= DATE('now', '-30 days')
-- ORDER BY date_scraped DESC;