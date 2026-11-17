-- Separa el importe de horas extra de la mano de obra ordinaria en proyectos.
-- Las asignaciones existentes se separan proporcionalmente por los días ya
-- distribuidos, conservando el costo histórico de cada proyecto.
BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'proyecto_asignacion_categoria_check'
          AND conrelid = 'public.proyecto_asignacion'::regclass
          AND pg_get_constraintdef(oid) LIKE '%HORAS_EXTRA%'
    ) THEN
        ALTER TABLE public.proyecto_asignacion
            DROP CONSTRAINT IF EXISTS proyecto_asignacion_categoria_check;
        ALTER TABLE public.proyecto_asignacion
            DROP CONSTRAINT IF EXISTS proyecto_asignacion_fuente_categoria_check;

        ALTER TABLE public.proyecto_asignacion
            ADD CONSTRAINT proyecto_asignacion_categoria_check
            CHECK (categoria IN ('INGRESO', 'COSTO_DIRECTO', 'MANO_OBRA', 'COSTO_INDIRECTO', 'HORAS_EXTRA'));

        ALTER TABLE public.proyecto_asignacion
            ADD CONSTRAINT proyecto_asignacion_fuente_categoria_check CHECK (
                (fuente_tipo = 'FACTURA' AND categoria = 'INGRESO') OR
                (fuente_tipo = 'COMPRA' AND categoria IN ('COSTO_DIRECTO', 'COSTO_INDIRECTO')) OR
                (fuente_tipo = 'PLANILLA' AND categoria IN ('MANO_OBRA', 'HORAS_EXTRA'))
            );

        ALTER TABLE public.proyecto_asignacion
            DROP CONSTRAINT IF EXISTS proyecto_asignacion_dias_check;
        ALTER TABLE public.proyecto_asignacion
            ADD CONSTRAINT proyecto_asignacion_dias_check CHECK (
                (fuente_tipo = 'PLANILLA' AND categoria = 'MANO_OBRA' AND dias_asignados > 0) OR
                (fuente_tipo = 'PLANILLA' AND categoria = 'HORAS_EXTRA' AND dias_asignados IS NULL) OR
                (fuente_tipo <> 'PLANILLA' AND dias_asignados IS NULL)
            );

        INSERT INTO public.proyecto_asignacion
            (proyecto_id,fuente_tipo,fuente_detalle_id,categoria,monto,creado_por,creado_en)
        SELECT pa.proyecto_id,'PLANILLA',pa.fuente_detalle_id,'HORAS_EXTRA',
            ROUND(pd.horas_extra * pa.dias_asignados / NULLIF(pd.dias_trabajados,0),2),
            pa.creado_por,pa.creado_en
        FROM public.proyecto_asignacion pa
        JOIN public.planilla_detalle pd ON pd.id=pa.fuente_detalle_id
        WHERE pa.fuente_tipo='PLANILLA' AND pa.categoria='MANO_OBRA'
          AND pa.dias_asignados IS NOT NULL AND pd.dias_trabajados>0
          AND pd.horas_extra>0
          AND ROUND(pd.horas_extra * pa.dias_asignados / NULLIF(pd.dias_trabajados,0),2)>0
        ON CONFLICT (proyecto_id,fuente_tipo,fuente_detalle_id,categoria) DO NOTHING;

        UPDATE public.proyecto_asignacion pa
        SET monto = GREATEST(0.01,
            pa.monto - ROUND(pd.horas_extra * pa.dias_asignados / NULLIF(pd.dias_trabajados, 0), 2))
        FROM public.planilla_detalle pd
        WHERE pa.fuente_tipo = 'PLANILLA'
          AND pa.categoria = 'MANO_OBRA'
          AND pa.fuente_detalle_id = pd.id
          AND pa.dias_asignados IS NOT NULL
          AND pd.dias_trabajados > 0
          AND pd.horas_extra > 0;
    END IF;
END;
$$;

COMMIT;
