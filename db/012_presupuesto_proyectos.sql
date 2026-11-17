-- Presupuesto estimado por proyecto para comparar con ingresos y costos reales asignados.
-- No modifica asientos ni recalcula las fuentes contables.
BEGIN;

ALTER TABLE public.proyecto
    ADD COLUMN IF NOT EXISTS ingreso_estimado NUMERIC(14,2),
    ADD COLUMN IF NOT EXISTS costo_directo_estimado NUMERIC(14,2),
    ADD COLUMN IF NOT EXISTS mano_obra_estimada NUMERIC(14,2),
    ADD COLUMN IF NOT EXISTS costo_indirecto_estimado NUMERIC(14,2);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'proyecto_presupuesto_no_negativo'
          AND conrelid = 'public.proyecto'::regclass
    ) THEN
        ALTER TABLE public.proyecto ADD CONSTRAINT proyecto_presupuesto_no_negativo CHECK (
            (ingreso_estimado IS NULL OR ingreso_estimado >= 0) AND
            (costo_directo_estimado IS NULL OR costo_directo_estimado >= 0) AND
            (mano_obra_estimada IS NULL OR mano_obra_estimada >= 0) AND
            (costo_indirecto_estimado IS NULL OR costo_indirecto_estimado >= 0)
        );
    END IF;
END;
$$;

COMMIT;
