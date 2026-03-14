-- =====================================================
-- ANÁLISIS DE SUPPLY CHAIN — FDA DRUG SHORTAGES
-- =====================================================


-- 1. ¿Cuántos medicamentos hay en escasez activa hoy?
SELECT
    COUNT(*) as total_escasez_activa,
    date_scraped as fecha
FROM medical_products
WHERE status = 'Currently In Shortage'
AND date_scraped = (SELECT MAX(date_scraped) FROM medical_products)
GROUP BY date_scraped;

-- 2. ¿Qué medicamentos llevan más días en escasez?
SELECT
    product_name,
    MIN(date_scraped)                    as primer_registro,
    MAX(date_scraped)                    as ultimo_registro,
    julianday(MAX(date_scraped)) -
    julianday(MIN(date_scraped))         as dias_en_escasez
FROM medical_products
WHERE status = 'Currently In Shortage'
GROUP BY product_name
ORDER BY dias_en_escasez DESC;

-- 3. ¿Qué medicamentos entraron en escasez esta semana?
SELECT
    product_name,
    status,
    date_scraped as fecha_deteccion
FROM medical_products
WHERE status = 'Currently In Shortage'
AND date_scraped >= DATE('now', '-7 days')
ORDER BY date_scraped DESC;


-- 4. ¿Qué escaseces se resolvieron este mes?
SELECT
    product_name,
    date_scraped as fecha_resolucion
FROM medical_products
WHERE status = 'Resolved Shortage'
AND date_scraped >= DATE('now', '-30 days')
ORDER BY date_scraped DESC;


-- 5. ¿Qué medicamentos cambiaron de estado?
SELECT
    a.product_name,
    a.status        as estado_anterior,
    b.status        as estado_actual,
    a.date_scraped  as fecha_anterior,
    b.date_scraped  as fecha_actual
FROM medical_products a
JOIN medical_products b
    ON a.product_name = b.product_name
    AND a.date_scraped < b.date_scraped
    AND a.status != b.status
ORDER BY b.date_scraped DESC;

-- 6. Resumen histórico completo
SELECT
    date_scraped                                    as fecha,
    COUNT(*)                                        as total_registros,
    SUM(CASE WHEN status = 'Currently In Shortage'
        THEN 1 ELSE 0 END)                          as en_escasez,
    SUM(CASE WHEN status = 'Resolved Shortage'
        THEN 1 ELSE 0 END)                          as resueltos
FROM medical_products
GROUP BY date_scraped
ORDER BY date_scraped DESC;


-- 7. Top 10 medicamentos con más apariciones en escasez
SELECT
    product_name,
    COUNT(*) as veces_en_escasez
FROM medical_products
WHERE status = 'Currently In Shortage'
GROUP BY product_name
ORDER BY veces_en_escasez DESC
LIMIT 10;