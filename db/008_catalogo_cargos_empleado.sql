-- Catálogo inicial de puestos de OptimaTech para el registro de empleados.
-- Se conserva empleado.cargo como texto para permitir puestos personalizados.
CREATE TABLE IF NOT EXISTS public.cargo_empleado (
    codigo VARCHAR(30) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    orden SMALLINT NOT NULL DEFAULT 100
);

INSERT INTO public.cargo_empleado (codigo, nombre, orden) VALUES
    ('GERENCIA', 'Gerente general', 10),
    ('ADMINISTRACION', 'Administrador/a de empresa', 20),
    ('CONTABILIDAD', 'Contador/a', 30),
    ('ASISTENTE_CONTABLE', 'Asistente contable', 40),
    ('DESARROLLO', 'Desarrollador/a de software', 50),
    ('ANALISTA_SISTEMAS', 'Analista de sistemas', 60),
    ('SOPORTE_TECNICO', 'Técnico/a de soporte', 70),
    ('REDES_INFRAESTRUCTURA', 'Técnico/a de redes e infraestructura', 80),
    ('CIBERSEGURIDAD', 'Especialista en ciberseguridad', 90),
    ('CCTV_BIOMETRIA_POS', 'Técnico/a de CCTV, biometría y POS', 100),
    ('IMPLEMENTACION', 'Especialista en implementación de sistemas', 110),
    ('VENTAS', 'Ejecutivo/a de ventas', 120),
    ('ASESORIA_COMERCIAL', 'Asesor/a comercial', 130),
    ('MARKETING_DIGITAL', 'Marketing digital', 140),
    ('AUXILIAR_ADMIN', 'Auxiliar administrativo/a', 150),
    ('COMPRAS_LOGISTICA', 'Compras y logística', 160)
ON CONFLICT (codigo) DO UPDATE
SET nombre = EXCLUDED.nombre,
    orden = EXCLUDED.orden;
