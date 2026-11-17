BEGIN;

ALTER TABLE public.cliente
    ADD COLUMN IF NOT EXISTS tipo_persona varchar(12) NOT NULL DEFAULT 'NATURAL',
    ADD COLUMN IF NOT EXISTS contribuyente_iva boolean NOT NULL DEFAULT false;

-- Clasifica los registros existentes usando sus identificaciones disponibles.
UPDATE public.cliente
   SET tipo_persona = CASE
       WHEN length(regexp_replace(coalesce(nit, ''), '\D', '', 'g')) = 9 THEN 'NATURAL'
       ELSE 'JURIDICA'
   END,
       contribuyente_iva = (nrc IS NOT NULL AND btrim(nrc) <> '');

ALTER TABLE public.cliente
    DROP CONSTRAINT IF EXISTS cliente_tipo_persona_check;
ALTER TABLE public.cliente
    ADD CONSTRAINT cliente_tipo_persona_check
    CHECK (tipo_persona IN ('NATURAL', 'JURIDICA'));

COMMIT;
