-- Catálogo inicial de los productos y servicios de OptimaTech.
-- Ejecutar después de db/004_factura_condiciones_pago.sql.

BEGIN;

ALTER TABLE public.cliente
    ADD COLUMN IF NOT EXISTS giro text;

ALTER TABLE public.factura
    ADD COLUMN IF NOT EXISTS nota_remision_numero varchar(30),
    ADD COLUMN IF NOT EXISTS nota_remision_fecha date;

ALTER TABLE public.factura_detalle
    ADD COLUMN IF NOT EXISTS producto_codigo varchar(20),
    ADD COLUMN IF NOT EXISTS unidad_medida varchar(20) NOT NULL DEFAULT 'UNIDAD',
    ADD COLUMN IF NOT EXISTS tipo_venta varchar(12) NOT NULL DEFAULT 'GRAVADA';

ALTER TABLE public.factura_detalle
    DROP CONSTRAINT IF EXISTS factura_detalle_tipo_venta_check;
ALTER TABLE public.factura_detalle
    ADD CONSTRAINT factura_detalle_tipo_venta_check
    CHECK (tipo_venta IN ('GRAVADA', 'EXENTA', 'NO_SUJETA'));

CREATE TABLE IF NOT EXISTS public.catalogo_producto_servicio (
    codigo varchar(20) PRIMARY KEY,
    nombre varchar(180) NOT NULL,
    linea_negocio varchar(80) NOT NULL,
    tipo varchar(12) NOT NULL CHECK (tipo IN ('PRODUCTO', 'SERVICIO')),
    unidad_medida varchar(20) NOT NULL DEFAULT 'UNIDAD',
    cuenta_ingreso_codigo varchar(20) NOT NULL REFERENCES public.catalogo_cuenta(codigo),
    activo boolean NOT NULL DEFAULT true
);

ALTER TABLE public.factura_detalle
    DROP CONSTRAINT IF EXISTS factura_detalle_producto_codigo_fkey;
ALTER TABLE public.factura_detalle
    ADD CONSTRAINT factura_detalle_producto_codigo_fkey
    FOREIGN KEY (producto_codigo)
    REFERENCES public.catalogo_producto_servicio(codigo);

INSERT INTO public.catalogo_producto_servicio
    (codigo, nombre, linea_negocio, tipo, unidad_medida, cuenta_ingreso_codigo)
VALUES
    ('CLOUD-001', 'Alojamiento de sitio web administrado', 'Data Center y nube', 'SERVICIO', 'MES', '5.1.2.02'),
    ('CLOUD-002', 'Servidor virtual en Data Center', 'Data Center y nube', 'SERVICIO', 'MES', '5.1.2.02'),
    ('CLOUD-003', 'Respaldo de bases de datos en nube', 'Data Center y nube', 'SERVICIO', 'MES', '5.1.2.02'),
    ('SOFT-001', 'Desarrollo de software a la medida', 'Software e implementación', 'SERVICIO', 'HORA', '5.1.1.01'),
    ('SOFT-002', 'Implementación y configuración de sistemas', 'Software e implementación', 'SERVICIO', 'SERVICIO', '5.1.1.02'),
    ('SOFT-003', 'Capacitación de usuarios', 'Software e implementación', 'SERVICIO', 'HORA', '5.1.1.02'),
    ('INTEG-001', 'Sistema de videovigilancia inteligente (CCTV)', 'Integración de hardware y software', 'PRODUCTO', 'EQUIPO', '5.1.3.01'),
    ('INTEG-002', 'Instalación y configuración de CCTV', 'Integración de hardware y software', 'SERVICIO', 'SERVICIO', '5.1.1.02'),
    ('INTEG-003', 'Sistema de control de acceso biométrico', 'Integración de hardware y software', 'PRODUCTO', 'EQUIPO', '5.1.3.01'),
    ('INTEG-004', 'Instalación y configuración de control biométrico', 'Integración de hardware y software', 'SERVICIO', 'SERVICIO', '5.1.1.02'),
    ('INTEG-005', 'Sistema de punto de venta (POS)', 'Integración de hardware y software', 'PRODUCTO', 'KIT', '5.1.3.01'),
    ('INTEG-006', 'Instalación y configuración de punto de venta (POS)', 'Integración de hardware y software', 'SERVICIO', 'SERVICIO', '5.1.1.02'),
    ('LIC-001', 'Licencia Microsoft 365 Corporativo', 'Licencias y software empaquetado', 'PRODUCTO', 'LICENCIA', '5.1.2.01'),
    ('LIC-002', 'Licencia de seguridad Endpoint (ESET, Kaspersky o Bitdefender)', 'Licencias y software empaquetado', 'PRODUCTO', 'LICENCIA', '5.1.2.01'),
    ('LIC-003', 'Licencia Adobe Creative Cloud', 'Licencias y software empaquetado', 'PRODUCTO', 'LICENCIA', '5.1.2.01'),
    ('LIC-004', 'Licencia Autodesk AutoCAD', 'Licencias y software empaquetado', 'PRODUCTO', 'LICENCIA', '5.1.2.01'),
    ('LIC-005', 'Licencia Windows Server', 'Licencias y software empaquetado', 'PRODUCTO', 'LICENCIA', '5.1.2.01'),
    ('SUP-001', 'Póliza de soporte y mantenimiento técnico', 'Soporte y mantenimiento', 'SERVICIO', 'MES', '5.1.1.03'),
    ('SUP-002', 'Soporte técnico remoto', 'Soporte y mantenimiento', 'SERVICIO', 'HORA', '5.1.1.04')
ON CONFLICT (codigo) DO UPDATE SET
    nombre = EXCLUDED.nombre,
    linea_negocio = EXCLUDED.linea_negocio,
    tipo = EXCLUDED.tipo,
    unidad_medida = EXCLUDED.unidad_medida,
    cuenta_ingreso_codigo = EXCLUDED.cuenta_ingreso_codigo,
    activo = true;

-- Giro de los clientes de demostración de acuerdo con su actividad ficticia.
UPDATE public.cliente
   SET giro = 'Venta de artículos de ferretería y materiales de construcción'
 WHERE codigo = 'CLI-001' AND (giro IS NULL OR btrim(giro) = '');
UPDATE public.cliente
   SET giro = 'Servicios educativos'
 WHERE codigo = 'CLI-002' AND (giro IS NULL OR btrim(giro) = '');

-- Completa los datos fiscales demostrativos del emisor a partir de la sucursal matriz.
INSERT INTO public.empresa (razon_social, nombre_comercial, nit, nrc, giro)
SELECT 'OptimaTech Empresarial, S.A. de C.V.', 'OptimaTech', s.nit, s.nrc,
       'Servicios de tecnología de información, infraestructura en la nube (Data Center), desarrollo de software a la medida e integración de sistemas'
  FROM public.sucursal s
 WHERE s.es_matriz = true
   AND NOT EXISTS (SELECT 1 FROM public.empresa);

UPDATE public.empresa
   SET giro = COALESCE(NULLIF(btrim(giro), ''),
       'Servicios de tecnología de información, infraestructura en la nube (Data Center), desarrollo de software a la medida e integración de sistemas')
 WHERE nombre_comercial = 'OptimaTech';

UPDATE public.sucursal
   SET direccion = CASE codigo
       WHEN 'MATRIZ' THEN 'San Salvador, El Salvador'
       WHEN 'OCC' THEN 'Santa Ana, El Salvador'
       WHEN 'ORI' THEN 'San Miguel, El Salvador'
       ELSE direccion
   END
 WHERE (es_matriz = true OR codigo IN ('OCC', 'ORI'))
   AND (direccion IS NULL OR btrim(direccion) = '');

COMMIT;
