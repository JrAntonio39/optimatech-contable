-- Clasificación fiscal por línea de compra.
-- Las líneas existentes se consideran gravadas para conservar el cálculo anterior.
ALTER TABLE compra_detalle
    ADD COLUMN IF NOT EXISTS tipo_iva varchar(20) NOT NULL DEFAULT 'GRAVADA';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'compra_detalle_tipo_iva_check'
          AND conrelid = 'compra_detalle'::regclass
    ) THEN
        ALTER TABLE compra_detalle
            ADD CONSTRAINT compra_detalle_tipo_iva_check
            CHECK (tipo_iva IN ('GRAVADA', 'EXENTA', 'NO_SUJETA'));
    END IF;
END;
$$;

CREATE OR REPLACE VIEW v_compra_detalle_total AS
SELECT id, compra_id, descripcion, cantidad, precio_unitario,
       cantidad * precio_unitario AS total_linea,
       cuenta_activo_codigo, tipo_iva
FROM compra_detalle;

CREATE OR REPLACE VIEW v_compra_totales AS
SELECT c.id, c.numero,
       COALESCE(SUM(d.cantidad * d.precio_unitario), 0) AS subtotal,
       COALESCE(SUM(CASE WHEN d.tipo_iva = 'GRAVADA'
                         THEN d.cantidad * d.precio_unitario ELSE 0 END), 0) * 0.13 AS iva,
       COALESCE(SUM(d.cantidad * d.precio_unitario), 0)
       + COALESCE(SUM(CASE WHEN d.tipo_iva = 'GRAVADA'
                            THEN d.cantidad * d.precio_unitario ELSE 0 END), 0) * 0.13 AS total
FROM compra c
LEFT JOIN compra_detalle d ON d.compra_id = c.id
GROUP BY c.id, c.numero;
