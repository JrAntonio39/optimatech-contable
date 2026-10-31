-- Datos de condiciones y forma de pago para la representación de facturas.
-- Estos campos no convierten el comprobante de la aplicación en un DTE autorizado.
BEGIN;

ALTER TABLE public.factura
    ADD COLUMN IF NOT EXISTS condicion_operacion VARCHAR(10) NOT NULL DEFAULT 'CONTADO',
    ADD COLUMN IF NOT EXISTS forma_pago VARCHAR(30),
    ADD COLUMN IF NOT EXISTS plazo_pago INTEGER,
    ADD COLUMN IF NOT EXISTS cuenta_pago_codigo VARCHAR(20)
        REFERENCES public.catalogo_cuenta(codigo);

ALTER TABLE public.factura DROP CONSTRAINT IF EXISTS factura_condicion_operacion_check;
ALTER TABLE public.factura ADD CONSTRAINT factura_condicion_operacion_check
    CHECK (condicion_operacion IN ('CONTADO', 'CREDITO', 'OTRO'));

ALTER TABLE public.factura DROP CONSTRAINT IF EXISTS factura_plazo_pago_check;
ALTER TABLE public.factura ADD CONSTRAINT factura_plazo_pago_check
    CHECK (plazo_pago IS NULL OR plazo_pago BETWEEN 1 AND 365);

COMMIT;
