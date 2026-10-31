-- Distingue el rechazo de un asiento pendiente de la anulacion de uno vigente.
ALTER TABLE public.asiento
    DROP CONSTRAINT IF EXISTS asiento_estado_check;

ALTER TABLE public.asiento
    ADD CONSTRAINT asiento_estado_check
    CHECK (estado IN ('PENDIENTE', 'VIGENTE', 'ANULADO', 'RECHAZADO'));

ALTER TABLE public.asiento
    ADD COLUMN IF NOT EXISTS motivo_rechazo text,
    ADD COLUMN IF NOT EXISTS rechazado_por integer REFERENCES public.usuario(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS rechazado_en timestamp without time zone;

DO $$
BEGIN
    IF to_regclass('public.planilla_pago') IS NOT NULL THEN
        ALTER TABLE public.planilla_pago
            DROP CONSTRAINT IF EXISTS planilla_pago_estado_check;
        ALTER TABLE public.planilla_pago
            ADD CONSTRAINT planilla_pago_estado_check
            CHECK (estado IN ('PENDIENTE', 'PAGADA', 'CANCELADA'));
    END IF;
END $$;
