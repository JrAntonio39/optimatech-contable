-- Distribución contable y aportes patronales para el detalle de planilla.
ALTER TABLE public.planilla_detalle
  ADD COLUMN IF NOT EXISTS cuenta_gasto_codigo VARCHAR(20) NOT NULL DEFAULT '4.1.3.01',
  ADD COLUMN IF NOT EXISTS isss_patronal NUMERIC(14,2) NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS afp_patronal NUMERIC(14,2) NOT NULL DEFAULT 0;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'planilla_detalle_cuenta_gasto_fkey') THEN
    ALTER TABLE public.planilla_detalle
      ADD CONSTRAINT planilla_detalle_cuenta_gasto_fkey
      FOREIGN KEY (cuenta_gasto_codigo) REFERENCES public.catalogo_cuenta(codigo)
      ON UPDATE CASCADE ON DELETE RESTRICT;
  END IF;
END $$;
