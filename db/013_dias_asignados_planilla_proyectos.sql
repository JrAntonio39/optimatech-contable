-- Permite asignar a cada proyecto solo los días que le corresponden de una planilla.
BEGIN;

ALTER TABLE public.proyecto_asignacion
    ADD COLUMN IF NOT EXISTS dias_asignados NUMERIC(8,2);

-- Convierte asignaciones de planilla existentes a días proporcionales al costo asignado.
UPDATE public.proyecto_asignacion pa
SET dias_asignados = GREATEST(0.01, ROUND(
    pd.dias_trabajados * pa.monto /
    NULLIF(ROUND(pd.salario_base * pd.dias_trabajados / 30 + pd.horas_extra + pd.bonificaciones + pd.comisiones, 2)
        + pd.isss_patronal + pd.afp_patronal, 0),
    2
))
FROM public.planilla_detalle pd
WHERE pa.fuente_tipo = 'PLANILLA'
  AND pa.fuente_detalle_id = pd.id
  AND pa.dias_asignados IS NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'proyecto_asignacion_dias_check'
          AND conrelid = 'public.proyecto_asignacion'::regclass
    ) THEN
        ALTER TABLE public.proyecto_asignacion
        ADD CONSTRAINT proyecto_asignacion_dias_check CHECK (
            (fuente_tipo = 'PLANILLA' AND dias_asignados > 0) OR
            (fuente_tipo <> 'PLANILLA' AND dias_asignados IS NULL)
        );
    END IF;
END;
$$;

COMMIT;
