-- Proyectos y rentabilidad: enlaza ingresos y costos ya contabilizados con trabajos.
-- No crea asientos ni modifica importes contables; solo registra asignaciones analíticas.
BEGIN;

CREATE TABLE IF NOT EXISTS public.proyecto (
    id BIGSERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE,
    nombre VARCHAR(160) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(30) NOT NULL DEFAULT 'OTRO',
    cliente_id INTEGER REFERENCES public.cliente(id) ON DELETE SET NULL,
    fecha_inicio DATE,
    fecha_fin DATE,
    estado VARCHAR(20) NOT NULL DEFAULT 'ABIERTO',
    creado_por INTEGER REFERENCES public.usuario(id) ON DELETE SET NULL,
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    actualizado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    CONSTRAINT proyecto_tipo_check CHECK (tipo IN ('CCTV', 'DESARROLLO', 'HOSTING', 'SOPORTE', 'LICENCIAS', 'EQUIPO', 'OTRO')),
    CONSTRAINT proyecto_estado_check CHECK (estado IN ('ABIERTO', 'COMPLETADO', 'CANCELADO')),
    CONSTRAINT proyecto_fechas_check CHECK (fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin >= fecha_inicio)
);

CREATE TABLE IF NOT EXISTS public.proyecto_asignacion (
    id BIGSERIAL PRIMARY KEY,
    proyecto_id BIGINT NOT NULL REFERENCES public.proyecto(id) ON DELETE RESTRICT,
    fuente_tipo VARCHAR(20) NOT NULL,
    fuente_detalle_id INTEGER NOT NULL,
    categoria VARCHAR(24) NOT NULL,
    monto NUMERIC(14,2) NOT NULL CHECK (monto > 0),
    creado_por INTEGER REFERENCES public.usuario(id) ON DELETE SET NULL,
    creado_en TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    CONSTRAINT proyecto_asignacion_fuente_check CHECK (fuente_tipo IN ('FACTURA', 'COMPRA', 'PLANILLA')),
    CONSTRAINT proyecto_asignacion_categoria_check CHECK (categoria IN ('INGRESO', 'COSTO_DIRECTO', 'MANO_OBRA', 'COSTO_INDIRECTO')),
    CONSTRAINT proyecto_asignacion_fuente_categoria_check CHECK (
        (fuente_tipo = 'FACTURA' AND categoria = 'INGRESO') OR
        (fuente_tipo = 'COMPRA' AND categoria IN ('COSTO_DIRECTO', 'COSTO_INDIRECTO')) OR
        (fuente_tipo = 'PLANILLA' AND categoria = 'MANO_OBRA')
    ),
    CONSTRAINT proyecto_asignacion_unica_por_categoria UNIQUE (proyecto_id, fuente_tipo, fuente_detalle_id, categoria)
);

CREATE INDEX IF NOT EXISTS idx_proyecto_estado ON public.proyecto(estado, nombre);
CREATE INDEX IF NOT EXISTS idx_proyecto_asignacion_proyecto ON public.proyecto_asignacion(proyecto_id, categoria);
CREATE INDEX IF NOT EXISTS idx_proyecto_asignacion_fuente ON public.proyecto_asignacion(fuente_tipo, fuente_detalle_id);

COMMIT;
