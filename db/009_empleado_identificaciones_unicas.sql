-- Evita duplicar DUI o NIT aunque se escriban con o sin guiones.
-- Se detiene con un mensaje claro si hay datos repetidos previos que resolver.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM empleado
        WHERE NULLIF(regexp_replace(dui, '[^0-9]', '', 'g'), '') IS NOT NULL
        GROUP BY regexp_replace(dui, '[^0-9]', '', 'g')
        HAVING COUNT(*) > 1
    ) THEN
        RAISE EXCEPTION 'Hay DUI duplicados en empleado. Corrígelos antes de aplicar esta migración.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM empleado
        WHERE NULLIF(regexp_replace(nit, '[^0-9]', '', 'g'), '') IS NOT NULL
        GROUP BY regexp_replace(nit, '[^0-9]', '', 'g')
        HAVING COUNT(*) > 1
    ) THEN
        RAISE EXCEPTION 'Hay NIT duplicados en empleado. Corrígelos antes de aplicar esta migración.';
    END IF;
END;
$$;

CREATE UNIQUE INDEX IF NOT EXISTS empleado_dui_digitos_unicos_idx
    ON empleado (regexp_replace(dui, '[^0-9]', '', 'g'))
    WHERE NULLIF(regexp_replace(dui, '[^0-9]', '', 'g'), '') IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS empleado_nit_digitos_unicos_idx
    ON empleado (regexp_replace(nit, '[^0-9]', '', 'g'))
    WHERE NULLIF(regexp_replace(nit, '[^0-9]', '', 'g'), '') IS NOT NULL;
