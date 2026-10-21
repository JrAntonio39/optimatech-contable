-- Controles operativos aditivos: auditoría, aprobación y anulaciones trazables.
BEGIN;

CREATE TABLE IF NOT EXISTS public.audit_event (
    id BIGSERIAL PRIMARY KEY,
    actor_user_id INTEGER REFERENCES public.usuario(id) ON DELETE SET NULL,
    action VARCHAR(40) NOT NULL,
    entity_type VARCHAR(40) NOT NULL,
    entity_id VARCHAR(60),
    reason TEXT,
    before_data JSONB,
    after_data JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_audit_event_created_at ON public.audit_event(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_event_entity ON public.audit_event(entity_type, entity_id);

ALTER TABLE public.asiento ADD COLUMN IF NOT EXISTS creado_por INTEGER REFERENCES public.usuario(id) ON DELETE SET NULL;
ALTER TABLE public.asiento ADD COLUMN IF NOT EXISTS aprobado_por INTEGER REFERENCES public.usuario(id) ON DELETE SET NULL;
ALTER TABLE public.asiento ADD COLUMN IF NOT EXISTS aprobado_en TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE public.asiento ADD COLUMN IF NOT EXISTS anulado_por INTEGER REFERENCES public.usuario(id) ON DELETE SET NULL;
ALTER TABLE public.asiento ADD COLUMN IF NOT EXISTS anulado_en TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE public.asiento ADD COLUMN IF NOT EXISTS motivo_anulacion TEXT;
ALTER TABLE public.asiento ADD COLUMN IF NOT EXISTS reverso_de_id INTEGER REFERENCES public.asiento(id) ON DELETE RESTRICT;

ALTER TABLE public.asiento DROP CONSTRAINT IF EXISTS asiento_estado_check;
ALTER TABLE public.asiento ADD CONSTRAINT asiento_estado_check
    CHECK (estado IN ('PENDIENTE', 'VIGENTE', 'ANULADO'));
CREATE UNIQUE INDEX IF NOT EXISTS idx_asiento_reverso_unico
    ON public.asiento(reverso_de_id) WHERE reverso_de_id IS NOT NULL;

ALTER TABLE public.factura ADD COLUMN IF NOT EXISTS creado_por INTEGER REFERENCES public.usuario(id) ON DELETE SET NULL;
ALTER TABLE public.factura ADD COLUMN IF NOT EXISTS aprobado_por INTEGER REFERENCES public.usuario(id) ON DELETE SET NULL;
ALTER TABLE public.factura ADD COLUMN IF NOT EXISTS aprobado_en TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE public.factura ADD COLUMN IF NOT EXISTS motivo_anulacion TEXT;
ALTER TABLE public.factura DROP CONSTRAINT IF EXISTS factura_estado_check;
ALTER TABLE public.factura ADD CONSTRAINT factura_estado_check
    CHECK (estado IN ('BORRADOR', 'PENDIENTE', 'VIGENTE', 'ANULADA'));

ALTER TABLE public.compra ADD COLUMN IF NOT EXISTS creado_por INTEGER REFERENCES public.usuario(id) ON DELETE SET NULL;
ALTER TABLE public.compra ADD COLUMN IF NOT EXISTS aprobado_por INTEGER REFERENCES public.usuario(id) ON DELETE SET NULL;
ALTER TABLE public.compra ADD COLUMN IF NOT EXISTS aprobado_en TIMESTAMP WITHOUT TIME ZONE;
ALTER TABLE public.compra ADD COLUMN IF NOT EXISTS motivo_anulacion TEXT;
ALTER TABLE public.compra DROP CONSTRAINT IF EXISTS compra_estado_check;
ALTER TABLE public.compra ADD CONSTRAINT compra_estado_check
    CHECK (estado IN ('BORRADOR', 'PENDIENTE', 'VIGENTE', 'ANULADA'));

ALTER TABLE public.planilla ADD COLUMN IF NOT EXISTS creado_por INTEGER REFERENCES public.usuario(id) ON DELETE SET NULL;
ALTER TABLE public.planilla ADD COLUMN IF NOT EXISTS aprobado_por INTEGER REFERENCES public.usuario(id) ON DELETE SET NULL;
ALTER TABLE public.planilla ADD COLUMN IF NOT EXISTS aprobado_en TIMESTAMP WITHOUT TIME ZONE;

COMMIT;
