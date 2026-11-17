-- Bitácora de trabajo por proyecto; el costo se calcula desde la planilla vigente.
BEGIN;

CREATE TABLE IF NOT EXISTS public.proyecto_horas (
    id BIGSERIAL PRIMARY KEY,
    proyecto_id BIGINT NOT NULL REFERENCES public.proyecto(id) ON DELETE RESTRICT,
    empleado_id INTEGER NOT NULL REFERENCES public.empleado(id) ON DELETE RESTRICT,
    fecha DATE NOT NULL,
    actividad VARCHAR(240) NOT NULL,
    horas NUMERIC(6,2) NOT NULL CHECK (horas > 0 AND horas <= 24),
    creado_por INTEGER REFERENCES public.usuario(id) ON DELETE SET NULL,
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_proyecto_horas_proyecto_fecha
    ON public.proyecto_horas(proyecto_id, fecha DESC);
CREATE INDEX IF NOT EXISTS idx_proyecto_horas_empleado_fecha
    ON public.proyecto_horas(empleado_id, fecha);

COMMIT;
