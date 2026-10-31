--
-- PostgreSQL database dump
--

\restrict MJRlvMcCLV4AVCra0WQYSHj5bM4ac4QdrcFRAAMAqTkNKIeRLcXs3vcvqKumXr7

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.usuario DROP CONSTRAINT IF EXISTS usuario_sucursal_id_fkey;
ALTER TABLE IF EXISTS ONLY public.usuario_rol DROP CONSTRAINT IF EXISTS usuario_rol_usuario_id_fkey;
ALTER TABLE IF EXISTS ONLY public.usuario_rol DROP CONSTRAINT IF EXISTS usuario_rol_rol_id_fkey;
ALTER TABLE IF EXISTS ONLY public.rol_permiso DROP CONSTRAINT IF EXISTS rol_permiso_rol_id_fkey;
ALTER TABLE IF EXISTS ONLY public.rol_permiso DROP CONSTRAINT IF EXISTS rol_permiso_permiso_id_fkey;
ALTER TABLE IF EXISTS ONLY public.proveedor DROP CONSTRAINT IF EXISTS proveedor_sucursal_id_fkey;
ALTER TABLE IF EXISTS ONLY public.proveedor DROP CONSTRAINT IF EXISTS proveedor_cuenta_codigo_fkey;
ALTER TABLE IF EXISTS ONLY public.planilla DROP CONSTRAINT IF EXISTS planilla_sucursal_id_fkey;
ALTER TABLE IF EXISTS ONLY public.planilla DROP CONSTRAINT IF EXISTS planilla_periodo_id_fkey;
ALTER TABLE IF EXISTS ONLY public.planilla_detalle DROP CONSTRAINT IF EXISTS planilla_detalle_planilla_id_fkey;
ALTER TABLE IF EXISTS ONLY public.planilla_detalle DROP CONSTRAINT IF EXISTS planilla_detalle_empleado_id_fkey;
ALTER TABLE IF EXISTS ONLY public.planilla_detalle DROP CONSTRAINT IF EXISTS planilla_detalle_cuenta_gasto_fkey;
ALTER TABLE IF EXISTS ONLY public.planilla DROP CONSTRAINT IF EXISTS planilla_creado_por_fkey;
ALTER TABLE IF EXISTS ONLY public.planilla DROP CONSTRAINT IF EXISTS planilla_asiento_id_fkey;
ALTER TABLE IF EXISTS ONLY public.planilla DROP CONSTRAINT IF EXISTS planilla_aprobado_por_fkey;
ALTER TABLE IF EXISTS ONLY public.factura DROP CONSTRAINT IF EXISTS factura_sucursal_id_fkey;
ALTER TABLE IF EXISTS ONLY public.factura DROP CONSTRAINT IF EXISTS factura_periodo_id_fkey;
ALTER TABLE IF EXISTS ONLY public.factura_detalle DROP CONSTRAINT IF EXISTS factura_detalle_factura_id_fkey;
ALTER TABLE IF EXISTS ONLY public.factura_detalle DROP CONSTRAINT IF EXISTS factura_detalle_cuenta_ingreso_codigo_fkey;
ALTER TABLE IF EXISTS ONLY public.factura DROP CONSTRAINT IF EXISTS factura_creado_por_fkey;
ALTER TABLE IF EXISTS ONLY public.factura DROP CONSTRAINT IF EXISTS factura_cliente_id_fkey;
ALTER TABLE IF EXISTS ONLY public.factura DROP CONSTRAINT IF EXISTS factura_asiento_id_fkey;
ALTER TABLE IF EXISTS ONLY public.factura DROP CONSTRAINT IF EXISTS factura_aprobado_por_fkey;
ALTER TABLE IF EXISTS ONLY public.empleado DROP CONSTRAINT IF EXISTS empleado_sucursal_id_fkey;
ALTER TABLE IF EXISTS ONLY public.empleado DROP CONSTRAINT IF EXISTS empleado_cuenta_anticipo_codigo_fkey;
ALTER TABLE IF EXISTS ONLY public.detalle_asiento DROP CONSTRAINT IF EXISTS detalle_asiento_cuenta_codigo_fkey;
ALTER TABLE IF EXISTS ONLY public.detalle_asiento DROP CONSTRAINT IF EXISTS detalle_asiento_asiento_id_fkey;
ALTER TABLE IF EXISTS ONLY public.compra DROP CONSTRAINT IF EXISTS compra_sucursal_id_fkey;
ALTER TABLE IF EXISTS ONLY public.compra DROP CONSTRAINT IF EXISTS compra_proveedor_id_fkey;
ALTER TABLE IF EXISTS ONLY public.compra DROP CONSTRAINT IF EXISTS compra_periodo_id_fkey;
ALTER TABLE IF EXISTS ONLY public.compra_detalle DROP CONSTRAINT IF EXISTS compra_detalle_cuenta_activo_codigo_fkey;
ALTER TABLE IF EXISTS ONLY public.compra_detalle DROP CONSTRAINT IF EXISTS compra_detalle_compra_id_fkey;
ALTER TABLE IF EXISTS ONLY public.compra DROP CONSTRAINT IF EXISTS compra_creado_por_fkey;
ALTER TABLE IF EXISTS ONLY public.compra DROP CONSTRAINT IF EXISTS compra_asiento_id_fkey;
ALTER TABLE IF EXISTS ONLY public.compra DROP CONSTRAINT IF EXISTS compra_aprobado_por_fkey;
ALTER TABLE IF EXISTS ONLY public.cliente DROP CONSTRAINT IF EXISTS cliente_sucursal_id_fkey;
ALTER TABLE IF EXISTS ONLY public.cliente DROP CONSTRAINT IF EXISTS cliente_cuenta_codigo_fkey;
ALTER TABLE IF EXISTS ONLY public.catalogo_cuenta DROP CONSTRAINT IF EXISTS catalogo_cuenta_codigo_padre_fkey;
ALTER TABLE IF EXISTS ONLY public.auditoria DROP CONSTRAINT IF EXISTS auditoria_usuario_id_fkey;
ALTER TABLE IF EXISTS ONLY public.asiento DROP CONSTRAINT IF EXISTS asiento_sucursal_id_fkey;
ALTER TABLE IF EXISTS ONLY public.asiento DROP CONSTRAINT IF EXISTS asiento_reverso_de_id_fkey;
ALTER TABLE IF EXISTS ONLY public.asiento DROP CONSTRAINT IF EXISTS asiento_periodo_id_fkey;
ALTER TABLE IF EXISTS ONLY public.asiento DROP CONSTRAINT IF EXISTS asiento_creado_por_fkey;
ALTER TABLE IF EXISTS ONLY public.asiento DROP CONSTRAINT IF EXISTS asiento_aprobado_por_fkey;
ALTER TABLE IF EXISTS ONLY public.asiento DROP CONSTRAINT IF EXISTS asiento_anulado_por_fkey;
DROP INDEX IF EXISTS public.ix_usuario_username;
DROP INDEX IF EXISTS public.ix_usuario_email;
DROP INDEX IF EXISTS public.ix_rol_codigo;
DROP INDEX IF EXISTS public.ix_permiso_modulo;
DROP INDEX IF EXISTS public.ix_permiso_codigo;
DROP INDEX IF EXISTS public.idx_planilla_periodo;
DROP INDEX IF EXISTS public.idx_planilla_detalle_planilla;
DROP INDEX IF EXISTS public.idx_factura_detalle_factura;
DROP INDEX IF EXISTS public.idx_factura_cliente;
DROP INDEX IF EXISTS public.idx_detalle_cuenta;
DROP INDEX IF EXISTS public.idx_detalle_asiento;
DROP INDEX IF EXISTS public.idx_cuenta_padre;
DROP INDEX IF EXISTS public.idx_cuenta_nivel;
DROP INDEX IF EXISTS public.idx_compra_proveedor;
DROP INDEX IF EXISTS public.idx_compra_fecha;
DROP INDEX IF EXISTS public.idx_compra_detalle_compra;
DROP INDEX IF EXISTS public.idx_auditoria_usuario;
DROP INDEX IF EXISTS public.idx_auditoria_registro;
DROP INDEX IF EXISTS public.idx_auditoria_modulo_accion;
DROP INDEX IF EXISTS public.idx_auditoria_fecha;
DROP INDEX IF EXISTS public.idx_asiento_reverso_unico;
DROP INDEX IF EXISTS public.idx_asiento_periodo;
DROP INDEX IF EXISTS public.idx_asiento_fecha;
ALTER TABLE IF EXISTS ONLY public.usuario_rol DROP CONSTRAINT IF EXISTS usuario_rol_pkey;
ALTER TABLE IF EXISTS ONLY public.usuario DROP CONSTRAINT IF EXISTS usuario_pkey;
ALTER TABLE IF EXISTS ONLY public.sucursal DROP CONSTRAINT IF EXISTS sucursal_pkey;
ALTER TABLE IF EXISTS ONLY public.sucursal DROP CONSTRAINT IF EXISTS sucursal_codigo_key;
ALTER TABLE IF EXISTS ONLY public.rol DROP CONSTRAINT IF EXISTS rol_pkey;
ALTER TABLE IF EXISTS ONLY public.rol_permiso DROP CONSTRAINT IF EXISTS rol_permiso_pkey;
ALTER TABLE IF EXISTS ONLY public.proveedor DROP CONSTRAINT IF EXISTS proveedor_pkey;
ALTER TABLE IF EXISTS ONLY public.proveedor DROP CONSTRAINT IF EXISTS proveedor_codigo_key;
ALTER TABLE IF EXISTS ONLY public.planilla DROP CONSTRAINT IF EXISTS planilla_pkey;
ALTER TABLE IF EXISTS ONLY public.planilla_detalle DROP CONSTRAINT IF EXISTS planilla_detalle_planilla_id_empleado_id_key;
ALTER TABLE IF EXISTS ONLY public.planilla_detalle DROP CONSTRAINT IF EXISTS planilla_detalle_pkey;
ALTER TABLE IF EXISTS ONLY public.planilla DROP CONSTRAINT IF EXISTS planilla_codigo_key;
ALTER TABLE IF EXISTS ONLY public.permiso DROP CONSTRAINT IF EXISTS permiso_pkey;
ALTER TABLE IF EXISTS ONLY public.periodo_contable DROP CONSTRAINT IF EXISTS periodo_contable_pkey;
ALTER TABLE IF EXISTS ONLY public.periodo_contable DROP CONSTRAINT IF EXISTS periodo_contable_anio_key;
ALTER TABLE IF EXISTS ONLY public.factura DROP CONSTRAINT IF EXISTS factura_pkey;
ALTER TABLE IF EXISTS ONLY public.factura DROP CONSTRAINT IF EXISTS factura_numero_key;
ALTER TABLE IF EXISTS ONLY public.factura_detalle DROP CONSTRAINT IF EXISTS factura_detalle_pkey;
ALTER TABLE IF EXISTS ONLY public.empresa DROP CONSTRAINT IF EXISTS empresa_pkey;
ALTER TABLE IF EXISTS ONLY public.empleado DROP CONSTRAINT IF EXISTS empleado_pkey;
ALTER TABLE IF EXISTS ONLY public.empleado DROP CONSTRAINT IF EXISTS empleado_dui_key;
ALTER TABLE IF EXISTS ONLY public.empleado DROP CONSTRAINT IF EXISTS empleado_codigo_key;
ALTER TABLE IF EXISTS ONLY public.detalle_asiento DROP CONSTRAINT IF EXISTS detalle_asiento_pkey;
ALTER TABLE IF EXISTS ONLY public.compra DROP CONSTRAINT IF EXISTS compra_pkey;
ALTER TABLE IF EXISTS ONLY public.compra DROP CONSTRAINT IF EXISTS compra_numero_key;
ALTER TABLE IF EXISTS ONLY public.compra_detalle DROP CONSTRAINT IF EXISTS compra_detalle_pkey;
ALTER TABLE IF EXISTS ONLY public.cliente DROP CONSTRAINT IF EXISTS cliente_pkey;
ALTER TABLE IF EXISTS ONLY public.cliente DROP CONSTRAINT IF EXISTS cliente_codigo_key;
ALTER TABLE IF EXISTS ONLY public.catalogo_cuenta DROP CONSTRAINT IF EXISTS catalogo_cuenta_pkey;
ALTER TABLE IF EXISTS ONLY public.auditoria DROP CONSTRAINT IF EXISTS auditoria_pkey;
ALTER TABLE IF EXISTS ONLY public.asiento DROP CONSTRAINT IF EXISTS asiento_pkey;
ALTER TABLE IF EXISTS ONLY public.asiento DROP CONSTRAINT IF EXISTS asiento_codigo_key;
ALTER TABLE IF EXISTS public.usuario ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.sucursal ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.rol ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.proveedor ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.planilla_detalle ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.planilla ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.permiso ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.periodo_contable ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.factura_detalle ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.factura ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.empresa ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.empleado ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.detalle_asiento ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.compra_detalle ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.compra ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.cliente ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.auditoria ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.asiento ALTER COLUMN id DROP DEFAULT;
DROP VIEW IF EXISTS public.v_subcuenta;
DROP VIEW IF EXISTS public.v_planilla_totales;
DROP VIEW IF EXISTS public.v_planilla_liquido;
DROP VIEW IF EXISTS public.v_libro_mayor;
DROP VIEW IF EXISTS public.v_grupo_cuenta;
DROP VIEW IF EXISTS public.v_factura_totales;
DROP VIEW IF EXISTS public.v_factura_detalle_total;
DROP VIEW IF EXISTS public.v_cuenta_mayor;
DROP VIEW IF EXISTS public.v_compra_totales;
DROP VIEW IF EXISTS public.v_compra_detalle_total;
DROP VIEW IF EXISTS public.v_catalogo_es_mayor;
DROP VIEW IF EXISTS public.v_balanza_comprobacion;
DROP VIEW IF EXISTS public.v_asiento_totales;
DROP TABLE IF EXISTS public.usuario_rol;
DROP SEQUENCE IF EXISTS public.usuario_id_seq;
DROP TABLE IF EXISTS public.usuario;
DROP SEQUENCE IF EXISTS public.sucursal_id_seq;
DROP TABLE IF EXISTS public.sucursal;
DROP TABLE IF EXISTS public.rol_permiso;
DROP SEQUENCE IF EXISTS public.rol_id_seq;
DROP TABLE IF EXISTS public.rol;
DROP SEQUENCE IF EXISTS public.proveedor_id_seq;
DROP TABLE IF EXISTS public.proveedor;
DROP SEQUENCE IF EXISTS public.planilla_id_seq;
DROP SEQUENCE IF EXISTS public.planilla_detalle_id_seq;
DROP TABLE IF EXISTS public.planilla_detalle;
DROP TABLE IF EXISTS public.planilla;
DROP SEQUENCE IF EXISTS public.permiso_id_seq;
DROP TABLE IF EXISTS public.permiso;
DROP SEQUENCE IF EXISTS public.periodo_contable_id_seq;
DROP TABLE IF EXISTS public.periodo_contable;
DROP SEQUENCE IF EXISTS public.factura_id_seq;
DROP SEQUENCE IF EXISTS public.factura_detalle_id_seq;
DROP TABLE IF EXISTS public.factura_detalle;
DROP TABLE IF EXISTS public.factura;
DROP SEQUENCE IF EXISTS public.empresa_id_seq;
DROP TABLE IF EXISTS public.empresa;
DROP TABLE IF EXISTS public.cargo_empleado;
DROP SEQUENCE IF EXISTS public.empleado_id_seq;
DROP TABLE IF EXISTS public.empleado;
DROP SEQUENCE IF EXISTS public.detalle_asiento_id_seq;
DROP TABLE IF EXISTS public.detalle_asiento;
DROP SEQUENCE IF EXISTS public.compra_id_seq;
DROP SEQUENCE IF EXISTS public.compra_detalle_id_seq;
DROP TABLE IF EXISTS public.compra_detalle;
DROP TABLE IF EXISTS public.compra;
DROP SEQUENCE IF EXISTS public.cliente_id_seq;
DROP TABLE IF EXISTS public.cliente;
DROP TABLE IF EXISTS public.catalogo_cuenta;
DROP SEQUENCE IF EXISTS public.auditoria_id_seq;
DROP TABLE IF EXISTS public.auditoria;
DROP SEQUENCE IF EXISTS public.asiento_id_seq;
DROP TABLE IF EXISTS public.asiento;
-- *not* dropping schema, since initdb creates it
--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS '';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: asiento; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.asiento (
    id integer NOT NULL,
    codigo character varying(20) NOT NULL,
    fecha date NOT NULL,
    concepto text NOT NULL,
    tipo character varying(20) NOT NULL,
    periodo_id integer NOT NULL,
    sucursal_id integer,
    estado character varying(20) DEFAULT 'VIGENTE'::character varying NOT NULL,
    creado_en timestamp without time zone DEFAULT now(),
    creado_por integer,
    aprobado_por integer,
    aprobado_en timestamp without time zone,
    anulado_por integer,
    anulado_en timestamp without time zone,
    motivo_anulacion text,
    motivo_rechazo text,
    rechazado_por integer,
    rechazado_en timestamp without time zone,
    reverso_de_id integer,
    CONSTRAINT asiento_estado_check CHECK (((estado)::text = ANY ((ARRAY['PENDIENTE'::character varying, 'VIGENTE'::character varying, 'ANULADO'::character varying, 'RECHAZADO'::character varying])::text[]))),
    CONSTRAINT asiento_tipo_check CHECK (((tipo)::text = ANY ((ARRAY['APERTURA'::character varying, 'DIARIO'::character varying, 'AJUSTE'::character varying, 'CIERRE'::character varying])::text[])))
);


ALTER TABLE public.asiento OWNER TO postgres;

--
-- Name: asiento_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.asiento_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.asiento_id_seq OWNER TO postgres;

--
-- Name: asiento_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.asiento_id_seq OWNED BY public.asiento.id;


--
-- Name: auditoria; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auditoria (
    id integer NOT NULL,
    fecha timestamp without time zone DEFAULT now() NOT NULL,
    usuario_id integer,
    usuario_nombre character varying(150) NOT NULL,
    modulo character varying(30) NOT NULL,
    entidad character varying(30) NOT NULL,
    registro_id integer,
    registro_codigo character varying(40),
    accion character varying(20) NOT NULL,
    descripcion text,
    datos_antes text,
    datos_despues text,
    ip character varying(45)
);


ALTER TABLE public.auditoria OWNER TO postgres;

--
-- Name: auditoria_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auditoria_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.auditoria_id_seq OWNER TO postgres;

--
-- Name: auditoria_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auditoria_id_seq OWNED BY public.auditoria.id;


--
-- Name: catalogo_cuenta; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.catalogo_cuenta (
    codigo character varying(20) NOT NULL,
    nombre character varying(150) NOT NULL,
    naturaleza character varying(25) NOT NULL,
    nivel integer NOT NULL,
    codigo_padre character varying(20),
    CONSTRAINT catalogo_cuenta_naturaleza_check CHECK (((naturaleza)::text = ANY ((ARRAY['Deudora'::character varying, 'Acreedora'::character varying, 'Deudora o Acreedora'::character varying])::text[]))),
    CONSTRAINT catalogo_cuenta_nivel_check CHECK (((nivel >= 1) AND (nivel <= 5)))
);


ALTER TABLE public.catalogo_cuenta OWNER TO postgres;

--
-- Name: cliente; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cliente (
    id integer NOT NULL,
    codigo character varying(20) NOT NULL,
    nombre character varying(150) NOT NULL,
    nit character varying(20),
    nrc character varying(20),
    direccion text,
    telefono character varying(20),
    email character varying(100),
    cuenta_codigo character varying(20),
    sucursal_id integer,
    estado character varying(20) DEFAULT 'ACTIVO'::character varying
);


ALTER TABLE public.cliente OWNER TO postgres;

--
-- Name: cliente_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cliente_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cliente_id_seq OWNER TO postgres;

--
-- Name: cliente_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cliente_id_seq OWNED BY public.cliente.id;


--
-- Name: compra; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.compra (
    id integer NOT NULL,
    numero character varying(30) NOT NULL,
    tipo_doc character varying(10) DEFAULT 'CCF'::character varying NOT NULL,
    fecha date NOT NULL,
    proveedor_id integer NOT NULL,
    sucursal_id integer NOT NULL,
    periodo_id integer NOT NULL,
    estado character varying(20) DEFAULT 'VIGENTE'::character varying NOT NULL,
    asiento_id integer,
    dte_json text,
    creado_en timestamp without time zone DEFAULT now(),
    creado_por integer,
    aprobado_por integer,
    aprobado_en timestamp without time zone,
    motivo_anulacion text,
    CONSTRAINT compra_estado_check CHECK (((estado)::text = ANY ((ARRAY['BORRADOR'::character varying, 'PENDIENTE'::character varying, 'VIGENTE'::character varying, 'ANULADA'::character varying])::text[]))),
    CONSTRAINT compra_tipo_doc_check CHECK (((tipo_doc)::text = ANY ((ARRAY['CCF'::character varying, 'FCON'::character varying, 'NCR'::character varying, 'TICKET'::character varying])::text[])))
);


ALTER TABLE public.compra OWNER TO postgres;

--
-- Name: compra_detalle; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.compra_detalle (
    id integer NOT NULL,
    compra_id integer NOT NULL,
    descripcion text NOT NULL,
    cantidad numeric(10,2) DEFAULT 1 NOT NULL,
    precio_unitario numeric(14,2) NOT NULL,
    cuenta_activo_codigo character varying(20) NOT NULL,
    tipo_iva character varying(20) DEFAULT 'GRAVADA'::character varying NOT NULL,
    CONSTRAINT compra_detalle_tipo_iva_check CHECK (((tipo_iva)::text = ANY ((ARRAY['GRAVADA'::character varying, 'EXENTA'::character varying, 'NO_SUJETA'::character varying])::text[])))
);


ALTER TABLE public.compra_detalle OWNER TO postgres;

--
-- Name: compra_detalle_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.compra_detalle_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.compra_detalle_id_seq OWNER TO postgres;

--
-- Name: compra_detalle_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.compra_detalle_id_seq OWNED BY public.compra_detalle.id;


--
-- Name: compra_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.compra_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.compra_id_seq OWNER TO postgres;

--
-- Name: compra_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.compra_id_seq OWNED BY public.compra.id;


--
-- Name: detalle_asiento; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.detalle_asiento (
    id integer NOT NULL,
    asiento_id integer NOT NULL,
    cuenta_codigo character varying(20) NOT NULL,
    debe numeric(14,2) DEFAULT 0 NOT NULL,
    haber numeric(14,2) DEFAULT 0 NOT NULL,
    descripcion text,
    CONSTRAINT detalle_asiento_check CHECK ((((debe > (0)::numeric) AND (haber = (0)::numeric)) OR ((haber > (0)::numeric) AND (debe = (0)::numeric)) OR ((debe = (0)::numeric) AND (haber = (0)::numeric)))),
    CONSTRAINT detalle_asiento_debe_check CHECK ((debe >= (0)::numeric)),
    CONSTRAINT detalle_asiento_haber_check CHECK ((haber >= (0)::numeric))
);


ALTER TABLE public.detalle_asiento OWNER TO postgres;

--
-- Name: detalle_asiento_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.detalle_asiento_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.detalle_asiento_id_seq OWNER TO postgres;

--
-- Name: detalle_asiento_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.detalle_asiento_id_seq OWNED BY public.detalle_asiento.id;


--
-- Name: empleado; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.empleado (
    id integer NOT NULL,
    codigo character varying(20) NOT NULL,
    nombres character varying(100) NOT NULL,
    apellidos character varying(100) NOT NULL,
    dui character varying(10),
    nit character varying(20),
    cargo character varying(100) NOT NULL,
    salario_base numeric(14,2) NOT NULL,
    fecha_ingreso date NOT NULL,
    sucursal_id integer,
    cuenta_anticipo_codigo character varying(20),
    estado character varying(20) DEFAULT 'ACTIVO'::character varying,
    CONSTRAINT empleado_estado_check CHECK (((estado)::text = ANY ((ARRAY['ACTIVO'::character varying, 'INACTIVO'::character varying])::text[])))
);


ALTER TABLE public.empleado OWNER TO postgres;

-- Catálogo de puestos de la empresa; empleado.cargo conserva el texto elegido.
CREATE TABLE public.cargo_empleado (
    codigo character varying(30) NOT NULL PRIMARY KEY,
    nombre character varying(100) NOT NULL UNIQUE,
    activo boolean NOT NULL DEFAULT TRUE,
    orden smallint NOT NULL DEFAULT 100
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
    ('COMPRAS_LOGISTICA', 'Compras y logística', 160);

--
-- Name: empleado_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.empleado_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.empleado_id_seq OWNER TO postgres;

--
-- Name: empleado_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.empleado_id_seq OWNED BY public.empleado.id;


--
-- Name: empresa; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.empresa (
    id integer NOT NULL,
    razon_social character varying(150) NOT NULL,
    nombre_comercial character varying(100) NOT NULL,
    nit character varying(20),
    nrc character varying(20),
    giro text
);


ALTER TABLE public.empresa OWNER TO postgres;

--
-- Name: empresa_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.empresa_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.empresa_id_seq OWNER TO postgres;

--
-- Name: empresa_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.empresa_id_seq OWNED BY public.empresa.id;


--
-- Name: factura; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.factura (
    id integer NOT NULL,
    numero character varying(30) NOT NULL,
    tipo_dte character varying(10) DEFAULT 'CCF'::character varying NOT NULL,
    fecha date NOT NULL,
    cliente_id integer NOT NULL,
    sucursal_id integer NOT NULL,
    periodo_id integer NOT NULL,
    estado character varying(20) DEFAULT 'VIGENTE'::character varying NOT NULL,
    asiento_id integer,
    dte_json text,
    creado_en timestamp without time zone DEFAULT now(),
    creado_por integer,
    aprobado_por integer,
    aprobado_en timestamp without time zone,
    motivo_anulacion text,
    CONSTRAINT factura_estado_check CHECK (((estado)::text = ANY ((ARRAY['BORRADOR'::character varying, 'PENDIENTE'::character varying, 'VIGENTE'::character varying, 'ANULADA'::character varying])::text[]))),
    CONSTRAINT factura_tipo_dte_check CHECK (((tipo_dte)::text = ANY ((ARRAY['CCF'::character varying, 'FCON'::character varying, 'NCR'::character varying])::text[])))
);


ALTER TABLE public.factura OWNER TO postgres;

--
-- Name: factura_detalle; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.factura_detalle (
    id integer NOT NULL,
    factura_id integer NOT NULL,
    descripcion text NOT NULL,
    cantidad numeric(10,2) DEFAULT 1 NOT NULL,
    precio_unitario numeric(14,2) NOT NULL,
    cuenta_ingreso_codigo character varying(20) NOT NULL
);


ALTER TABLE public.factura_detalle OWNER TO postgres;

--
-- Name: factura_detalle_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.factura_detalle_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.factura_detalle_id_seq OWNER TO postgres;

--
-- Name: factura_detalle_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.factura_detalle_id_seq OWNED BY public.factura_detalle.id;


--
-- Name: factura_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.factura_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.factura_id_seq OWNER TO postgres;

--
-- Name: factura_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.factura_id_seq OWNED BY public.factura.id;


--
-- Name: periodo_contable; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.periodo_contable (
    id integer NOT NULL,
    anio integer NOT NULL,
    fecha_inicio date NOT NULL,
    fecha_fin date NOT NULL,
    estado character varying(20) DEFAULT 'ABIERTO'::character varying NOT NULL,
    CONSTRAINT periodo_contable_check CHECK ((fecha_fin > fecha_inicio)),
    CONSTRAINT periodo_contable_estado_check CHECK (((estado)::text = ANY ((ARRAY['ABIERTO'::character varying, 'CERRADO'::character varying])::text[])))
);


ALTER TABLE public.periodo_contable OWNER TO postgres;

--
-- Name: periodo_contable_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.periodo_contable_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.periodo_contable_id_seq OWNER TO postgres;

--
-- Name: periodo_contable_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.periodo_contable_id_seq OWNED BY public.periodo_contable.id;


--
-- Name: permiso; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permiso (
    id integer NOT NULL,
    codigo character varying(50) NOT NULL,
    nombre character varying(100) NOT NULL,
    modulo character varying(30) NOT NULL,
    accion character varying(20) NOT NULL,
    descripcion character varying(255)
);


ALTER TABLE public.permiso OWNER TO postgres;

--
-- Name: permiso_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.permiso_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.permiso_id_seq OWNER TO postgres;

--
-- Name: permiso_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.permiso_id_seq OWNED BY public.permiso.id;


--
-- Name: planilla; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.planilla (
    id integer NOT NULL,
    codigo character varying(20) NOT NULL,
    periodo character varying(7) NOT NULL,
    fecha_pago date NOT NULL,
    sucursal_id integer,
    tipo character varying(20) DEFAULT 'MENSUAL'::character varying NOT NULL,
    estado character varying(20) DEFAULT 'BORRADOR'::character varying NOT NULL,
    asiento_id integer,
    periodo_id integer NOT NULL,
    creado_en timestamp without time zone DEFAULT now(),
    creado_por integer,
    aprobado_por integer,
    aprobado_en timestamp without time zone,
    CONSTRAINT planilla_estado_check CHECK (((estado)::text = ANY ((ARRAY['BORRADOR'::character varying, 'APROBADA'::character varying, 'CONTABILIZADA'::character varying, 'PAGADA'::character varying])::text[]))),
    CONSTRAINT planilla_tipo_check CHECK (((tipo)::text = ANY ((ARRAY['MENSUAL'::character varying, 'QUINCENAL'::character varying, 'AGUINALDO'::character varying])::text[])))
);


ALTER TABLE public.planilla OWNER TO postgres;

--
-- Name: planilla_detalle; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.planilla_detalle (
    id integer NOT NULL,
    planilla_id integer NOT NULL,
    empleado_id integer NOT NULL,
    dias_trabajados integer DEFAULT 30 NOT NULL,
    salario_base numeric(14,2) NOT NULL,
    horas_extra numeric(14,2) DEFAULT 0,
    bonificaciones numeric(14,2) DEFAULT 0,
    comisiones numeric(14,2) DEFAULT 0,
    deduccion_isss numeric(14,2) DEFAULT 0,
    deduccion_afp numeric(14,2) DEFAULT 0,
    deduccion_renta numeric(14,2) DEFAULT 0,
    otras_deducciones numeric(14,2) DEFAULT 0,
    cuenta_gasto_codigo character varying(20) DEFAULT '4.1.3.01'::character varying NOT NULL,
    isss_patronal numeric(14,2) DEFAULT 0 NOT NULL,
    afp_patronal numeric(14,2) DEFAULT 0 NOT NULL
);


ALTER TABLE public.planilla_detalle OWNER TO postgres;

--
-- Name: planilla_detalle_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.planilla_detalle_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.planilla_detalle_id_seq OWNER TO postgres;

--
-- Name: planilla_detalle_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.planilla_detalle_id_seq OWNED BY public.planilla_detalle.id;


--
-- Name: planilla_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.planilla_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.planilla_id_seq OWNER TO postgres;

--
-- Name: planilla_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.planilla_id_seq OWNED BY public.planilla.id;


--
-- Name: proveedor; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.proveedor (
    id integer NOT NULL,
    codigo character varying(20) NOT NULL,
    nombre character varying(150) NOT NULL,
    nit character varying(20),
    nrc character varying(20),
    direccion text,
    telefono character varying(20),
    email character varying(100),
    cuenta_codigo character varying(20),
    sucursal_id integer,
    estado character varying(20) DEFAULT 'ACTIVO'::character varying,
    CONSTRAINT proveedor_estado_check CHECK (((estado)::text = ANY ((ARRAY['ACTIVO'::character varying, 'INACTIVO'::character varying])::text[])))
);


ALTER TABLE public.proveedor OWNER TO postgres;

--
-- Name: proveedor_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.proveedor_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.proveedor_id_seq OWNER TO postgres;

--
-- Name: proveedor_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.proveedor_id_seq OWNED BY public.proveedor.id;


--
-- Name: rol; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rol (
    id integer NOT NULL,
    codigo character varying(30) NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion character varying(255),
    activo boolean
);


ALTER TABLE public.rol OWNER TO postgres;

--
-- Name: rol_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rol_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.rol_id_seq OWNER TO postgres;

--
-- Name: rol_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rol_id_seq OWNED BY public.rol.id;


--
-- Name: rol_permiso; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rol_permiso (
    rol_id integer NOT NULL,
    permiso_id integer NOT NULL
);


ALTER TABLE public.rol_permiso OWNER TO postgres;

--
-- Name: sucursal; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sucursal (
    id integer NOT NULL,
    codigo character varying(10) NOT NULL,
    nombre character varying(100) NOT NULL,
    direccion text,
    es_matriz boolean DEFAULT false,
    razon_social character varying(150),
    nit character varying(20),
    nrc character varying(20)
);


ALTER TABLE public.sucursal OWNER TO postgres;

--
-- Name: sucursal_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sucursal_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sucursal_id_seq OWNER TO postgres;

--
-- Name: sucursal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sucursal_id_seq OWNED BY public.sucursal.id;


--
-- Name: usuario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    nombre_completo character varying(150) NOT NULL,
    activo boolean,
    fecha_creacion timestamp without time zone,
    ultimo_acceso timestamp without time zone,
    sucursal_id integer
);


ALTER TABLE public.usuario OWNER TO postgres;

--
-- Name: usuario_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuario_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuario_id_seq OWNER TO postgres;

--
-- Name: usuario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuario_id_seq OWNED BY public.usuario.id;


--
-- Name: usuario_rol; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario_rol (
    usuario_id integer NOT NULL,
    rol_id integer NOT NULL
);


ALTER TABLE public.usuario_rol OWNER TO postgres;

--
-- Name: v_asiento_totales; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_asiento_totales AS
 SELECT a.id,
    a.codigo,
    COALESCE(sum(d.debe), (0)::numeric) AS total_debe,
    COALESCE(sum(d.haber), (0)::numeric) AS total_haber,
        CASE
            WHEN (COALESCE(sum(d.debe), (0)::numeric) = COALESCE(sum(d.haber), (0)::numeric)) THEN 'CUADRADO'::text
            ELSE 'DESCUADRADO'::text
        END AS estado_partida
   FROM (public.asiento a
     LEFT JOIN public.detalle_asiento d ON ((d.asiento_id = a.id)))
  GROUP BY a.id, a.codigo;


ALTER VIEW public.v_asiento_totales OWNER TO postgres;

--
-- Name: v_balanza_comprobacion; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_balanza_comprobacion AS
 SELECT c.codigo,
    c.nombre,
    COALESCE(sum(d.debe), (0)::numeric) AS sumas_debe,
    COALESCE(sum(d.haber), (0)::numeric) AS sumas_haber,
        CASE
            WHEN (COALESCE(sum((d.debe - d.haber)), (0)::numeric) > (0)::numeric) THEN COALESCE(sum((d.debe - d.haber)), (0)::numeric)
            ELSE (0)::numeric
        END AS saldo_deudor,
        CASE
            WHEN (COALESCE(sum((d.debe - d.haber)), (0)::numeric) < (0)::numeric) THEN abs(COALESCE(sum((d.debe - d.haber)), (0)::numeric))
            ELSE (0)::numeric
        END AS saldo_acreedor
   FROM ((public.catalogo_cuenta c
     JOIN public.detalle_asiento d ON (((d.cuenta_codigo)::text = (c.codigo)::text)))
     JOIN public.asiento a ON (((a.id = d.asiento_id) AND ((a.estado)::text = 'VIGENTE'::text))))
  WHERE (c.nivel = 3)
  GROUP BY c.codigo, c.nombre
  ORDER BY c.codigo;


ALTER VIEW public.v_balanza_comprobacion OWNER TO postgres;

--
-- Name: v_catalogo_es_mayor; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_catalogo_es_mayor AS
 SELECT codigo,
    nombre,
    (nivel = 3) AS es_cuenta_mayor,
    (NOT (EXISTS ( SELECT 1
           FROM public.catalogo_cuenta c2
          WHERE ((c2.codigo_padre)::text = (c.codigo)::text)))) AS permite_movimiento
   FROM public.catalogo_cuenta c;


ALTER VIEW public.v_catalogo_es_mayor OWNER TO postgres;

--
-- Name: v_compra_detalle_total; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_compra_detalle_total AS
 SELECT id,
    compra_id,
    descripcion,
    cantidad,
    precio_unitario,
    (cantidad * precio_unitario) AS total_linea,
    cuenta_activo_codigo,
    tipo_iva
   FROM public.compra_detalle;


ALTER VIEW public.v_compra_detalle_total OWNER TO postgres;

--
-- Name: v_compra_totales; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_compra_totales AS
 SELECT c.id,
    c.numero,
    COALESCE(sum((cd.cantidad * cd.precio_unitario)), (0)::numeric) AS subtotal,
    (COALESCE(sum(CASE WHEN cd.tipo_iva = 'GRAVADA'::character varying THEN (cd.cantidad * cd.precio_unitario) ELSE (0)::numeric END), (0)::numeric) * 0.13) AS iva,
    (COALESCE(sum((cd.cantidad * cd.precio_unitario)), (0)::numeric) + (COALESCE(sum(CASE WHEN cd.tipo_iva = 'GRAVADA'::character varying THEN (cd.cantidad * cd.precio_unitario) ELSE (0)::numeric END), (0)::numeric) * 0.13)) AS total
   FROM (public.compra c
     LEFT JOIN public.compra_detalle cd ON ((cd.compra_id = c.id)))
  GROUP BY c.id, c.numero;


ALTER VIEW public.v_compra_totales OWNER TO postgres;

--
-- Name: v_cuenta_mayor; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_cuenta_mayor AS
 SELECT codigo,
    nombre,
    naturaleza,
    nivel,
    codigo_padre
   FROM public.catalogo_cuenta
  WHERE (nivel = 3)
  ORDER BY codigo;


ALTER VIEW public.v_cuenta_mayor OWNER TO postgres;

--
-- Name: v_factura_detalle_total; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_factura_detalle_total AS
 SELECT id,
    factura_id,
    descripcion,
    cantidad,
    precio_unitario,
    (cantidad * precio_unitario) AS total_linea,
    cuenta_ingreso_codigo
   FROM public.factura_detalle;


ALTER VIEW public.v_factura_detalle_total OWNER TO postgres;

--
-- Name: v_factura_totales; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_factura_totales AS
 SELECT f.id,
    f.numero,
    COALESCE(sum((fd.cantidad * fd.precio_unitario)), (0)::numeric) AS subtotal,
    (COALESCE(sum((fd.cantidad * fd.precio_unitario)), (0)::numeric) * 0.13) AS iva,
    (COALESCE(sum((fd.cantidad * fd.precio_unitario)), (0)::numeric) * 1.13) AS total
   FROM (public.factura f
     LEFT JOIN public.factura_detalle fd ON ((fd.factura_id = f.id)))
  GROUP BY f.id, f.numero;


ALTER VIEW public.v_factura_totales OWNER TO postgres;

--
-- Name: v_grupo_cuenta; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_grupo_cuenta AS
 SELECT codigo,
    nombre,
    naturaleza,
    nivel
   FROM public.catalogo_cuenta
  WHERE (nivel = 1)
  ORDER BY codigo;


ALTER VIEW public.v_grupo_cuenta OWNER TO postgres;

--
-- Name: v_libro_mayor; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_libro_mayor AS
 SELECT c.codigo,
    c.nombre,
    c.naturaleza,
    COALESCE(sum(d.debe), (0)::numeric) AS total_debe,
    COALESCE(sum(d.haber), (0)::numeric) AS total_haber,
    COALESCE(sum((d.debe - d.haber)), (0)::numeric) AS saldo
   FROM ((public.catalogo_cuenta c
     LEFT JOIN public.detalle_asiento d ON (((d.cuenta_codigo)::text = (c.codigo)::text)))
     LEFT JOIN public.asiento a ON (((a.id = d.asiento_id) AND ((a.estado)::text = 'VIGENTE'::text))))
  GROUP BY c.codigo, c.nombre, c.naturaleza
  ORDER BY c.codigo;


ALTER VIEW public.v_libro_mayor OWNER TO postgres;

--
-- Name: v_planilla_liquido; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_planilla_liquido AS
 SELECT id,
    planilla_id,
    empleado_id,
    (((((((salario_base + COALESCE(horas_extra, (0)::numeric)) + COALESCE(bonificaciones, (0)::numeric)) + COALESCE(comisiones, (0)::numeric)) - COALESCE(deduccion_isss, (0)::numeric)) - COALESCE(deduccion_afp, (0)::numeric)) - COALESCE(deduccion_renta, (0)::numeric)) - COALESCE(otras_deducciones, (0)::numeric)) AS liquido_pagar
   FROM public.planilla_detalle;


ALTER VIEW public.v_planilla_liquido OWNER TO postgres;

--
-- Name: v_planilla_totales; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_planilla_totales AS
 SELECT p.id,
    p.codigo,
    COALESCE(sum((((pd.salario_base + COALESCE(pd.horas_extra, (0)::numeric)) + COALESCE(pd.bonificaciones, (0)::numeric)) + COALESCE(pd.comisiones, (0)::numeric))), (0)::numeric) AS total_bruto,
    COALESCE(sum((((COALESCE(pd.deduccion_isss, (0)::numeric) + COALESCE(pd.deduccion_afp, (0)::numeric)) + COALESCE(pd.deduccion_renta, (0)::numeric)) + COALESCE(pd.otras_deducciones, (0)::numeric))), (0)::numeric) AS total_deducciones,
    COALESCE(sum((((((((pd.salario_base + COALESCE(pd.horas_extra, (0)::numeric)) + COALESCE(pd.bonificaciones, (0)::numeric)) + COALESCE(pd.comisiones, (0)::numeric)) - COALESCE(pd.deduccion_isss, (0)::numeric)) - COALESCE(pd.deduccion_afp, (0)::numeric)) - COALESCE(pd.deduccion_renta, (0)::numeric)) - COALESCE(pd.otras_deducciones, (0)::numeric))), (0)::numeric) AS total_neto
   FROM (public.planilla p
     LEFT JOIN public.planilla_detalle pd ON ((pd.planilla_id = p.id)))
  GROUP BY p.id, p.codigo;


ALTER VIEW public.v_planilla_totales OWNER TO postgres;

--
-- Name: v_subcuenta; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_subcuenta AS
 SELECT codigo,
    nombre,
    naturaleza,
    nivel,
    codigo_padre
   FROM public.catalogo_cuenta
  WHERE (nivel = ANY (ARRAY[4, 5]))
  ORDER BY codigo;


ALTER VIEW public.v_subcuenta OWNER TO postgres;

--
-- Name: asiento id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asiento ALTER COLUMN id SET DEFAULT nextval('public.asiento_id_seq'::regclass);


--
-- Name: auditoria id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditoria ALTER COLUMN id SET DEFAULT nextval('public.auditoria_id_seq'::regclass);


--
-- Name: cliente id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente ALTER COLUMN id SET DEFAULT nextval('public.cliente_id_seq'::regclass);


--
-- Name: compra id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra ALTER COLUMN id SET DEFAULT nextval('public.compra_id_seq'::regclass);


--
-- Name: compra_detalle id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra_detalle ALTER COLUMN id SET DEFAULT nextval('public.compra_detalle_id_seq'::regclass);


--
-- Name: detalle_asiento id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_asiento ALTER COLUMN id SET DEFAULT nextval('public.detalle_asiento_id_seq'::regclass);


--
-- Name: empleado id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.empleado ALTER COLUMN id SET DEFAULT nextval('public.empleado_id_seq'::regclass);


--
-- Name: empresa id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.empresa ALTER COLUMN id SET DEFAULT nextval('public.empresa_id_seq'::regclass);


--
-- Name: factura id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.factura ALTER COLUMN id SET DEFAULT nextval('public.factura_id_seq'::regclass);


--
-- Name: factura_detalle id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.factura_detalle ALTER COLUMN id SET DEFAULT nextval('public.factura_detalle_id_seq'::regclass);


--
-- Name: periodo_contable id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.periodo_contable ALTER COLUMN id SET DEFAULT nextval('public.periodo_contable_id_seq'::regclass);


--
-- Name: permiso id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permiso ALTER COLUMN id SET DEFAULT nextval('public.permiso_id_seq'::regclass);


--
-- Name: planilla id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planilla ALTER COLUMN id SET DEFAULT nextval('public.planilla_id_seq'::regclass);


--
-- Name: planilla_detalle id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planilla_detalle ALTER COLUMN id SET DEFAULT nextval('public.planilla_detalle_id_seq'::regclass);


--
-- Name: proveedor id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proveedor ALTER COLUMN id SET DEFAULT nextval('public.proveedor_id_seq'::regclass);


--
-- Name: rol id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rol ALTER COLUMN id SET DEFAULT nextval('public.rol_id_seq'::regclass);


--
-- Name: sucursal id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sucursal ALTER COLUMN id SET DEFAULT nextval('public.sucursal_id_seq'::regclass);


--
-- Name: usuario id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario ALTER COLUMN id SET DEFAULT nextval('public.usuario_id_seq'::regclass);


--
-- Data for Name: asiento; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.asiento (id, codigo, fecha, concepto, tipo, periodo_id, sucursal_id, estado, creado_en, creado_por, aprobado_por, aprobado_en, anulado_por, anulado_en, motivo_anulacion, reverso_de_id) FROM stdin;
1	AST-2026-0001	2026-01-01	Asiento de Apertura - Balance Inicial	APERTURA	1	1	VIGENTE	2026-08-30 21:41:57.185242	\N	\N	\N	\N	\N	\N	\N
2	AST-2026-0002	2026-03-10	Venta Factura F-001-00001 a Ferretería El Perno	DIARIO	1	1	VIGENTE	2026-08-30 21:41:57.188257	\N	\N	\N	\N	\N	\N	\N
3	AST-2026-0003	2026-03-31	Planilla Marzo 2026 - Sueldos y deducciones	DIARIO	1	1	VIGENTE	2026-08-30 21:41:57.19021	\N	\N	\N	\N	\N	\N	\N
\.


--
-- Data for Name: auditoria; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auditoria (id, fecha, usuario_id, usuario_nombre, modulo, entidad, registro_id, registro_codigo, accion, descripcion, datos_antes, datos_despues, ip) FROM stdin;
\.


--
-- Data for Name: catalogo_cuenta; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.catalogo_cuenta (codigo, nombre, naturaleza, nivel, codigo_padre) FROM stdin;
1.0	ACTIVO	Deudora	1	\N
1.1	Activo Corriente	Deudora	2	1.0
1.1.1	Efectivo y Equivalentes de Efectivo	Deudora	3	1.1
1.1.1.01	Caja General	Deudora	4	1.1.1
1.1.1.02	Caja Chica	Deudora	4	1.1.1
1.1.1.03	Bancos Moneda Nacional	Deudora	4	1.1.1
1.1.1.03.01	Bancos - Casa Matriz	Deudora	5	1.1.1.03
1.1.1.03.02	Bancos - Sucursal Occidente	Deudora	5	1.1.1.03
1.1.1.03.03	Bancos - Sucursal Oriente	Deudora	5	1.1.1.03
1.1.2	Inversiones Temporales	Deudora	3	1.1
1.1.2.01	Depositos a Plazo Fijo	Deudora	4	1.1.2
1.1.2.02	Bonos y Titulos Valores	Deudora	4	1.1.2
1.1.3	Cuentas y Documentos por Cobrar	Deudora	3	1.1
1.1.3.01	Clientes Locales	Deudora	4	1.1.3
1.1.3.01.01	Clientes por Suscripciones (Cloud y Soporte)	Deudora	5	1.1.3.01
1.1.3.01.02	Clientes por Proyectos (Desarrollo e Instalación)	Deudora	5	1.1.3.01
1.1.3.01.03	Clientes por Venta de Hardware y Licencias	Deudora	5	1.1.3.01
1.1.3.02	Clientes del Exterior	Deudora	4	1.1.3
1.1.3.03	Documentos por Cobrar	Deudora	4	1.1.3
1.1.3.04	Prestamos o Anticipos a Empleados	Deudora	4	1.1.3
1.1.4	Estimacion para Cuentas Incobrables	Acreedora	3	1.1
1.1.4.01	Estimacion para Cuentas Incobrables de Clientes	Acreedora	4	1.1.4
1.1.5	Inventarios	Deudora	3	1.1
1.1.5.01	Inventario de Equipo Tecnologico	Deudora	4	1.1.5
1.1.5.02	Inventario de Materiales y Suministros	Deudora	4	1.1.5
1.1.5.03	Mercaderia en Transito	Deudora	4	1.1.5
1.1.5.04	Licencias de software Para Ventas	Deudora	4	1.1.5
1.1.6	Reserva para Obsolescencia de Equipo Tecnológico y Licencias	Acreedora	3	1.1
1.1.6.01	Reserva para Obsolescencia de Equipo Tecnológico y Licencias	Acreedora	4	1.1.6
1.1.7	Pagos Anticipados	Deudora	3	1.1
1.1.7.01	Seguros Pagados por Anticipado	Deudora	4	1.1.7
1.1.7.02	Alquileres Pagados por Anticipado	Deudora	4	1.1.7
1.1.7.03	Suscripciones Pagadas por Anticipado	Deudora	4	1.1.7
1.1.8	IVA Credito Fiscal	Deudora	3	1.1
1.1.8.01	IVA por Compras Locales	Deudora	4	1.1.8
1.1.8.02	IVA por Importaciones	Deudora	4	1.1.8
1.1.8.03	IVA Retenido	Deudora	4	1.1.8
1.1.9	Pago a Cuenta de Impuestos	Deudora	3	1.1
1.1.9.01	Anticipo de Impuesto sobre la Renta	Deudora	4	1.1.9
1.1.9.02	Retenciones de Impuesto sobre la Renta	Deudora	4	1.1.9
1.2	Activo No Corriente	Deudora	2	1.0
1.2.1	Cuentas por Cobrar a Largo Plazo	Deudora	3	1.2
1.2.1.01	Clientes a Largo Plazo	Deudora	4	1.2.1
1.2.1.02	Prestamos a Empleados a Largo Plazo	Deudora	4	1.2.1
1.2.2	Inversiones Permanentes	Deudora	3	1.2
1.2.2.01	Acciones en Otras Sociedades	Deudora	4	1.2.2
1.2.3	Propiedad, Planta y Equipo	Deudora	3	1.2
1.2.3.01	Terrenos	Deudora	4	1.2.3
1.2.3.02	Edificios e Instalaciones	Deudora	4	1.2.3
1.2.3.03	Mobiliario y Equipo de Oficina	Deudora	4	1.2.3
1.2.3.04	Equipo de Computacion y Comunicacion	Deudora	4	1.2.3
1.2.3.05	Servidores y Equipamiento de Data Center.	Deudora	4	1.2.3
1.2.3.06	Vehiculos	Deudora	4	1.2.3
1.2.4	Depreciacion Acumulada de Propiedad, Planta y Equipo	Acreedora	3	1.2
1.2.4.01	Depreciacion Acumulada de Edificios	Acreedora	4	1.2.4
1.2.4.02	Depreciacion Acumulada de Mobiliario y Equipo	Acreedora	4	1.2.4
1.2.4.03	Depreciacion Acumulada de Equipo de Computacion	Acreedora	4	1.2.4
1.2.4.04	Depreciacion Acumulada de Vehiculos	Acreedora	4	1.2.4
1.2.4.05	Depreciacion Acumulada de Servidores y Data Center.	Acreedora	4	1.2.4
1.2.5	Activos por Derecho de Uso	Deudora	3	1.2
1.2.5.01	Locales y Oficinas.	Deudora	4	1.2.5
1.2.5.02	Equipos y Vehiculos.	Deudora	4	1.2.5
1.2.6	Depreciacion Acumulada de Activos por Derecho de Uso	Acreedora	3	1.2
1.2.6.01	Dep. Acum. Locales y Oficinas	Acreedora	4	1.2.6
1.2.6.02	Dep. Acum. Equipos y Vehiculos	Acreedora	4	1.2.6
1.2.7	Activos Intangibles	Deudora	3	1.2
1.2.7.01	Software Desarrollado (Propiedad de la empresa)	Deudora	4	1.2.7
1.2.7.02	Marcas, Patentes y Licencias	Deudora	4	1.2.7
1.2.8	Amortizacion Acumulada de Activos Intangibles	Acreedora	3	1.2
1.2.8.01	Amortizacion Acumulada de Software	Acreedora	4	1.2.8
1.2.8.02	Amortizacion Acumulada de Marcas y Patentes	Acreedora	4	1.2.8
1.2.9	Depositos en Garantia	Deudora	3	1.2
1.2.9.01	Depositos en Garantia por Arrendamientos (Alquiler de local)	Deudora	4	1.2.9
1.2.9.02	Depositos en Garantia por Servicios (Luz, agua, internet)	Deudora	4	1.2.9
1.2.10	Activo por Impuestos Diferidos	Deudora	3	1.2
1.2.10.01	Impuestos Diferidos por Diferencias Temporarias	Deudora	4	1.2.10
2.0	PASIVO	Acreedora	1	\N
2.1	Pasivo Corriente	Acreedora	2	2.0
2.1.1	Proveedores	Acreedora	3	2.1
2.1.1.01	Proveedores Nacionales	Acreedora	4	2.1.1
2.1.1.02	Proveedores Internacionales	Acreedora	4	2.1.1
2.1.2	Préstamos Bancarios	Acreedora	3	2.1
2.1.3	Retenciones Laborales	Acreedora	3	2.1
2.1.3.01	Retenciones de Impuesto sobre la Renta	Acreedora	4	2.1.3
2.1.3.02	Retenciones de Seguridad Social	Acreedora	4	2.1.3
2.1.3.03	Otras Retenciones Laborales	Acreedora	4	2.1.3
2.1.4	Beneficios a Empleados a Corto Plazo	Acreedora	3	2.1
2.1.4.01	Vacaciones Por Pagar	Acreedora	4	2.1.4
2.1.4.02	Aginaldos Por Pagar	Acreedora	4	2.1.4
2.1.4.03	Sueldos y Salarios Por Pagar	Acreedora	4	2.1.4
2.1.4.04	Bonificaciones Por Pagar	Acreedora	4	2.1.4
2.1.4.05	Comisiones Por Pagar	Acreedora	4	2.1.4
2.1.5	Seguridad Social	Acreedora	3	2.1
2.1.5.01	Seguridad Social Por Pagar	Acreedora	4	2.1.5
2.1.5.02	Aportes Patronales Por Pagar	Acreedora	4	2.1.5
2.1.6	Servicios Por Pagar	Acreedora	3	2.1
2.1.6.01	Servicios Básicos	Acreedora	4	2.1.6
2.1.6.02	Servicios de Infraestructura Tecnológica	Acreedora	4	2.1.6
2.1.6.03	Internet y Telecomunicaciones	Acreedora	4	2.1.6
2.1.6.04	Servicios de Mantenimiento	Acreedora	4	2.1.6
2.1.6.05	Servicios de Soporte Técnico	Acreedora	4	2.1.6
2.1.6.06	Servicios Profesionales	Acreedora	4	2.1.6
2.1.7	Suscripciones y Licencias Por Pagar	Acreedora	3	2.1
2.1.7.01	Licencias de Software	Acreedora	4	2.1.7
2.1.7.02	Servicios Cloud	Acreedora	4	2.1.7
2.1.7.03	Suscripciones Tecnológicas	Acreedora	4	2.1.7
2.1.8	Documentos Por Pagar a Corto Plazo	Acreedora	3	2.1
2.1.8.01	Documentos Por Pagar a Proveedores	Acreedora	4	2.1.8
2.1.8.02	Otros Documentos Por Pagar	Acreedora	4	2.1.8
2.1.9	Impuestos Por Pagar	Acreedora	3	2.1
2.1.9.01	Impuesto Sobre la Renta Por Pagar	Acreedora	4	2.1.9
2.1.9.02	Otros Impuestos Por Pagar	Acreedora	4	2.1.9
2.1.10	Débito Fiscal - IVA	Acreedora	3	2.1
2.1.10.01	IVA por Ventas Locales	Acreedora	4	2.1.10
2.1.10.02	IVA Retenido	Acreedora	4	2.1.10
2.1.10.03	IVA por Otras Operaciones Gravadas	Acreedora	4	2.1.10
2.2	Pasivo No Corriente	Acreedora	2	2.0
2.2.1	Préstamos a Largo Plazo	Acreedora	3	2.2
2.2.1.01	Préstamos Prendarios	Acreedora	4	2.2.1
2.2.1.02	Préstamos HIpotecarios	Acreedora	4	2.2.1
2.2.1.03	Préstamos Personales	Acreedora	4	2.2.1
2.2.1.04	Préstamos Bancarios a Largo Plazo	Acreedora	4	2.2.1
2.2.2	Beneficios a Empleados a Largo Plazo	Acreedora	3	2.2
2.2.3	Documentos Por Pagar a Largo Plazo	Acreedora	3	2.2
2.2.3.01	Documentos Por Pagar a Proveedores a Largo Plazo	Acreedora	4	2.2.3
2.2.3.02	Otros Documentos Por Pagar a Largo Plazo	Acreedora	4	2.2.3
2.2.4	Arrendamientos Financieros	Acreedora	3	2.2
2.2.4.01	Arrendamientos Financieros Por Pagar	Acreedora	4	2.2.4
2.3	Pasivo Diferido	Acreedora	2	2.0
2.3.1	Impuestos Diferidos	Acreedora	3	2.3
2.3.2	Ingresos Recibidos por Adelantado	Acreedora	3	2.3
2.3.2.01	Anticipos de Clientes	Acreedora	4	2.3.2
2.3.2.02	Servicios Recibidos por Adelantado	Acreedora	4	2.3.2
2.3.2.03	Suscripciones Cobradas por Adelantado	Acreedora	4	2.3.2
3.0	PATRIMONIO	Acreedora	1	\N
3.1	Capital y Reservas	Acreedora	2	3.0
3.1.1	Capital Social	Acreedora	3	3.1
3.1.1.01	Capital Social Fijo	Acreedora	4	3.1.1
3.1.1.02	Capital Social Variable	Acreedora	4	3.1.1
3.1.2	Reserva Legal	Acreedora	3	3.1
3.1.2.01	Reserva Legal	Acreedora	4	3.1.2
3.1.3	Utilidades (Perdidas) Acumuladas	Acreedora	3	3.1
3.1.3.01	Utilidades Acumuladas de Ejercicios Anteriores	Acreedora	4	3.1.3
3.1.3.02	(Perdidas) Acumuladas de Ejercicios Anteriores	Acreedora	4	3.1.3
3.1.4	Resultado del Ejercicio	Acreedora	3	3.1
3.1.4.01	Utilidad del Ejercicio	Acreedora	4	3.1.4
3.1.4.02	(Perdida) del Ejercicio	Acreedora	4	3.1.4
4.0	CUENTAS DE RESULTADO DEUDORAS	Deudora	1	\N
4.1	Costos y Gastos	Deudora	2	4.0
4.1.1	Costos de Operación	Deudora	3	4.1
4.1.1.01	Costos de Servicios Tecnológicos	Deudora	4	4.1.1
4.1.1.02	Costos de Desarrollo de Software	Deudora	4	4.1.1
4.1.1.03	Costos de Implementación de Sistemas	Deudora	4	4.1.1
4.1.1.04	Costos de Mantenimiento de Software	Deudora	4	4.1.1
4.1.1.05	Costos de Licencias Utilizadas en Proyectos	Deudora	4	4.1.1
4.1.1.06	Costos de Soporte Técnico	Deudora	4	4.1.1
4.1.1.07	Costos de Infraestructura Tecnológica	Deudora	4	4.1.1
4.1.1.08	Costos de Servicios Cloud	Deudora	4	4.1.1
4.1.1.09	Costos de Personal Técnico	Deudora	4	4.1.1
4.1.1.10	Costos de Materiales de Soporte Técnico	Deudora	4	4.1.1
4.1.2	Costos de Venta de Dispositivos de Hardware	Deudora	3	4.1
4.1.3	Gastos de Operación	Deudora	3	4.1
4.1.3.01	Gastos Administrativos	Deudora	4	4.1.3
4.1.3.02	Gastos de Servicios Básicos	Deudora	4	4.1.3
4.1.3.03	Arrendamientos	Deudora	4	4.1.3
4.1.3.04	Mantenimiento	Deudora	4	4.1.3
4.1.3.05	Depreciación	Deudora	4	4.1.3
4.1.3.06	Amortización de Software	Deudora	4	4.1.3
4.1.3.07	Seguros	Deudora	4	4.1.3
4.1.3.08	Licencias y Suscripciones	Deudora	4	4.1.3
4.1.3.09	Honorarios Profesionales	Deudora	4	4.1.3
4.1.4	Gastos de Venta	Deudora	3	4.1
4.1.4.01	Sueldos del Personal de Ventas	Deudora	4	4.1.4
4.1.4.02	Comisiones sobre Ventas	Deudora	4	4.1.4
4.1.4.03	Publicidad	Deudora	4	4.1.4
4.1.4.04	Transporte y Entrega	Deudora	4	4.1.4
4.1.4.05	Promociones	Deudora	4	4.1.4
4.1.4.06	Garantías y Devoluciones de Clientes	Deudora	4	4.1.4
4.1.5	Gastos Financieros	Deudora	3	4.1
4.1.5.01	Intereses sobre Préstamos	Deudora	4	4.1.5
4.1.5.02	Comisiones Bancarias	Deudora	4	4.1.5
4.1.5.03	Gastos por Financiamento	Deudora	4	4.1.5
4.1.6	Otros Gastos	Deudora	3	4.1
4.1.6.01	Otros Gastos de Operación	Deudora	4	4.1.6
4.1.6.02	Pérdida en Venta de Activos	Deudora	4	4.1.6
5.0	CUENTAS DE RESULTADO ACREEDORAS	Acreedora	1	\N
5.1	Ingresos de Operación	Acreedora	2	5.0
5.1.1	Ingresos por Servicios Tecnológicos	Acreedora	3	5.1
5.1.1.01	Ingresos por Desarrollo de Software	Acreedora	4	5.1.1
5.1.1.02	Ingresos por Implementación de Sistemas	Acreedora	4	5.1.1
5.1.1.03	Ingresos por Mantenimiento de Software	Acreedora	4	5.1.1
5.1.1.04	Ingresos por Soporte Técnico	Acreedora	4	5.1.1
5.1.2	Ingresos por Licencias y Suscripciones	Acreedora	3	5.1
5.1.2.01	Ingresos por Venta de Licencias	Acreedora	4	5.1.2
5.1.2.02	Ingresos por Suscripciones Cloud y Soporte	Acreedora	4	5.1.2
5.1.3	Ingresos por Venta de Hardware	Acreedora	3	5.1
5.1.3.01	Venta de Equipo Tecnológico	Acreedora	4	5.1.3
5.2	Otros Ingresos	Acreedora	2	5.0
5.2.1	Ingresos Financieros	Acreedora	3	5.2
5.2.1.01	Intereses Ganados	Acreedora	4	5.2.1
5.2.2	Otros Ingresos No Operacionales	Acreedora	3	5.2
5.2.2.01	Otros Ingresos Diversos	Acreedora	4	5.2.2
6.0	CUENTAS LIQUIDADORAS	Deudora o Acreedora	1	\N
6.1	Liquidación de Resultados	Deudora o Acreedora	2	6.0
6.1.1	Pérdidas y Ganancias	Deudora o Acreedora	3	6.1
6.1.1.01	Liquidación de Cuentas de Resultado	Deudora o Acreedora	4	6.1.1
7.0	CUENTAS DE ORDEN	Acreedora	1	\N
7.1	Cuentas de Orden Deudoras	Deudora	2	7.0
7.1.1	Bienes en Custodia	Deudora	3	7.1
7.1.1.01	Bienes Recibidos en Custodia	Deudora	4	7.1.1
7.1.2	Documentos en Garantía	Deudora	3	7.1
7.1.2.01	Documentos Recibidos en Garantía	Deudora	4	7.1.2
7.2	Cuentas de Orden Acreedoras	Acreedora	2	7.0
7.2.1	Contracuenta de Bienes en Custodia	Acreedora	3	7.2
7.2.1.01	Responsabilidad por Bienes en Custodia	Acreedora	4	7.2.1
7.2.2	Contracuenta de Documentos en Garantía	Acreedora	3	7.2
7.2.2.01	Responsabilidad por Documentos en Garantía	Acreedora	4	7.2.2
\.


--
-- Data for Name: cliente; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cliente (id, codigo, nombre, nit, nrc, direccion, telefono, email, cuenta_codigo, sucursal_id, estado) FROM stdin;
1	CLI-001	Ferretería El Perno S.A. de C.V.	0614-010199-001-1	123456-0	San Salvador, Col. Escalón	2222-1111	compras@elperno.com	1.1.3.01.02	1	ACTIVO
2	CLI-002	Colegio Salesiano San José	0614-020300-002-2	234567-1	Santa Ana, Centro	2440-2222	admin@salesiano.edu.sv	1.1.3.01.01	2	ACTIVO
\.


--
-- Data for Name: compra; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.compra (id, numero, tipo_doc, fecha, proveedor_id, sucursal_id, periodo_id, estado, asiento_id, dte_json, creado_en, creado_por, aprobado_por, aprobado_en, motivo_anulacion) FROM stdin;
\.


--
-- Data for Name: compra_detalle; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.compra_detalle (id, compra_id, descripcion, cantidad, precio_unitario, cuenta_activo_codigo) FROM stdin;
\.


--
-- Data for Name: detalle_asiento; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.detalle_asiento (id, asiento_id, cuenta_codigo, debe, haber, descripcion) FROM stdin;
1	1	1.1.1.01	5000.00	0.00	Caja General inicial
2	1	1.1.1.03.01	25000.00	0.00	Bancos Casa Matriz inicial
3	1	1.1.5.01	10000.00	0.00	Inventario Equipo Tecnológico inicial
4	1	1.2.3.05	15000.00	0.00	Servidores Data Center
5	1	2.1.1.01	0.00	10000.00	Proveedores Nacionales
6	1	3.1.1.01	0.00	40000.00	Capital Social Fijo
7	1	3.1.2.01	0.00	5000.00	Reserva Legal
8	2	1.1.3.01.02	3955.00	0.00	Clientes por Proyectos - Factura F-001
9	2	5.1.1.01	0.00	3000.00	Ingresos por Desarrollo de Software
10	2	5.1.2.01	0.00	500.00	Ingresos por Venta de Licencias
11	2	2.1.10.01	0.00	455.00	IVA Débito Fiscal 13%
12	3	4.1.1.09	2200.00	0.00	Costos de Personal Técnico (1200+800+150 extras)
14	3	2.1.5.01	0.00	60.00	Seguridad Social por Pagar ISSS (36+24)
15	3	2.1.5.02	0.00	146.25	Aportes Patronales AFP (87.75+58.50)
16	3	2.1.3.01	0.00	115.00	Retenciones Renta por Pagar (85+30)
13	3	2.1.4.03	0.00	1878.75	Sueldos y Salarios por Pagar (líquido: 1126.25+737.50)
\.


--
-- Data for Name: empleado; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.empleado (id, codigo, nombres, apellidos, dui, nit, cargo, salario_base, fecha_ingreso, sucursal_id, cuenta_anticipo_codigo, estado) FROM stdin;
1	EMP-001	Carlos	Rivas	01234567-1	0614-150195-101-1	Desarrollador Senior	1200.00	2024-03-01	1	\N	ACTIVO
2	EMP-002	Ana	Torres	07654321-2	0614-220198-102-2	Soporte Técnico	800.00	2025-01-15	2	\N	ACTIVO
\.


--
-- Data for Name: empresa; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.empresa (id, razon_social, nombre_comercial, nit, nrc, giro) FROM stdin;
\.


--
-- Data for Name: factura; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.factura (id, numero, tipo_dte, fecha, cliente_id, sucursal_id, periodo_id, estado, asiento_id, dte_json, creado_en, creado_por, aprobado_por, aprobado_en, motivo_anulacion) FROM stdin;
1	F-001-00001	CCF	2026-03-10	1	1	1	VIGENTE	2	{"dte":"ejemplo"}	2026-08-30 21:41:57.179001	\N	\N	\N	\N
\.


--
-- Data for Name: factura_detalle; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.factura_detalle (id, factura_id, descripcion, cantidad, precio_unitario, cuenta_ingreso_codigo) FROM stdin;
1	1	Desarrollo Sistema Inventario a la medida (40 horas)	1.00	3000.00	5.1.1.01
2	1	Licencias Microsoft 365 Corporativo x 5 usuarios	5.00	100.00	5.1.2.01
\.


--
-- Data for Name: periodo_contable; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.periodo_contable (id, anio, fecha_inicio, fecha_fin, estado) FROM stdin;
1	2026	2026-01-01	2026-12-31	ABIERTO
\.


--
-- Data for Name: permiso; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.permiso (id, codigo, nombre, modulo, accion, descripcion) FROM stdin;
99	cuentas.ver	Cuentas · Ver	cuentas	ver	Ver el catálogo de cuentas
100	cuentas.crear	Cuentas · Crear	cuentas	crear	Agregar cuentas al catálogo
101	cuentas.editar	Cuentas · Editar	cuentas	editar	Modificar cuentas del catálogo
102	cuentas.eliminar	Cuentas · Eliminar	cuentas	eliminar	Eliminar cuentas del catálogo
103	asientos.ver	Asientos · Ver	asientos	ver	Ver asientos y libro diario
104	asientos.crear	Asientos · Crear	asientos	crear	Registrar asientos contables
105	asientos.editar	Asientos · Editar	asientos	editar	Modificar asientos en borrador
106	asientos.eliminar	Asientos · Eliminar	asientos	eliminar	Eliminar asientos en borrador
107	asientos.aprobar	Asientos · Aprobar	asientos	aprobar	Aprobar asientos para contabilizar
108	asientos.anular	Asientos · Anular	asientos	anular	Anular asientos contabilizados
109	periodos.ver	Periodos · Ver	periodos	ver	Ver períodos contables
110	periodos.crear	Periodos · Crear	periodos	crear	Abrir nuevos períodos
111	periodos.editar	Periodos · Editar	periodos	editar	Modificar datos de períodos
112	periodos.cerrar	Periodos · Cerrar	periodos	cerrar	Cerrar períodos contables
113	sucursales.ver	Sucursales · Ver	sucursales	ver	Ver sucursales
114	sucursales.crear	Sucursales · Crear	sucursales	crear	Crear sucursales
115	sucursales.editar	Sucursales · Editar	sucursales	editar	Editar sucursales
116	facturas.ver	Facturas · Ver	facturas	ver	Ver facturas
117	facturas.crear	Facturas · Crear	facturas	crear	Emitir facturas electrónicas
118	facturas.editar	Facturas · Editar	facturas	editar	Editar facturas en borrador
119	facturas.eliminar	Facturas · Eliminar	facturas	eliminar	Eliminar facturas en borrador
120	facturas.aprobar	Facturas · Aprobar	facturas	aprobar	Aprobar facturas para contabilizar
121	facturas.anular	Facturas · Anular	facturas	anular	Anular facturas emitidas
122	compras.ver	Compras · Ver	compras	ver	Ver compras y proveedores
123	compras.crear	Compras · Crear	compras	crear	Registrar compras
124	compras.editar	Compras · Editar	compras	editar	Editar compras en borrador
125	compras.aprobar	Compras · Aprobar	compras	aprobar	Aprobar compras para contabilizar
126	planilla.ver	Planilla · Ver	planilla	ver	Ver planilla de salarios
127	planilla.crear	Planilla · Crear	planilla	crear	Crear planilla de salarios
128	planilla.editar	Planilla · Editar	planilla	editar	Editar planilla de salarios
129	planilla.aprobar	Planilla · Aprobar	planilla	aprobar	Aprobar planilla para contabilizar
130	reportes.ver	Reportes · Ver	reportes	ver	Ver reportes contables
131	reportes.crear	Reportes · Crear	reportes	crear	Exportar reportes
132	usuarios.ver	Usuarios · Ver	usuarios	ver	Ver usuarios del sistema
133	usuarios.crear	Usuarios · Crear	usuarios	crear	Crear usuarios
134	usuarios.editar	Usuarios · Editar	usuarios	editar	Editar usuarios y roles
135	usuarios.eliminar	Usuarios · Eliminar	usuarios	eliminar	Desactivar usuarios
136	auditoria.ver	Auditoria · Ver	auditoria	ver	Ver bitácora de auditoría
\.


--
-- Data for Name: planilla; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.planilla (id, codigo, periodo, fecha_pago, sucursal_id, tipo, estado, asiento_id, periodo_id, creado_en, creado_por, aprobado_por, aprobado_en) FROM stdin;
1	PLA-2026-03	2026-03	2026-03-31	1	MENSUAL	CONTABILIZADA	3	1	2026-08-30 21:41:57.182341	\N	\N	\N
\.


--
-- Data for Name: planilla_detalle; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.planilla_detalle (id, planilla_id, empleado_id, dias_trabajados, salario_base, horas_extra, bonificaciones, comisiones, deduccion_isss, deduccion_afp, deduccion_renta, otras_deducciones) FROM stdin;
1	1	1	30	1200.00	50.00	100.00	0.00	36.00	87.75	85.00	0.00
2	1	2	30	800.00	0.00	50.00	0.00	24.00	58.50	30.00	0.00
\.


--
-- Data for Name: proveedor; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.proveedor (id, codigo, nombre, nit, nrc, direccion, telefono, email, cuenta_codigo, sucursal_id, estado) FROM stdin;
\.


--
-- Data for Name: rol; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rol (id, codigo, nombre, descripcion, activo) FROM stdin;
8	admin	Administrador	Acceso total	t
9	contador	Contador	Gestión contable	t
10	auxiliar	Auxiliar Contable	Registro operaciones	t
11	ventas	Ventas	Facturación	t
12	compras	Compras	Compras	t
13	planilla	Planilla	Nómina	t
14	auditor	Auditor	Solo lectura	t
\.


--
-- Data for Name: rol_permiso; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rol_permiso (rol_id, permiso_id) FROM stdin;
8	100
9	100
8	121
11	121
8	101
9	101
8	122
9	122
12	122
14	122
8	102
8	123
12	123
8	103
9	103
10	103
14	103
8	124
12	124
8	104
9	104
10	104
8	125
12	125
8	105
9	105
10	105
8	126
9	126
13	126
14	126
8	106
9	106
8	127
13	127
8	107
9	107
8	128
13	128
8	108
9	108
8	129
13	129
8	109
9	109
10	109
14	109
8	130
9	130
10	130
11	130
12	130
13	130
14	130
8	110
9	110
8	131
9	131
8	111
9	111
8	132
14	132
8	112
9	112
8	133
8	113
9	113
10	113
14	113
8	134
8	114
9	114
8	135
8	115
9	115
8	136
9	136
14	136
8	116
9	116
11	116
14	116
8	117
11	117
8	118
11	118
8	119
11	119
8	120
11	120
8	99
9	99
10	99
11	99
12	99
13	99
14	99
\.


--
-- Data for Name: sucursal; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sucursal (id, codigo, nombre, direccion, es_matriz, razon_social, nit, nrc) FROM stdin;
1	MATRIZ	Casa Matriz - San Salvador	\N	t	OptimaTech Empresarial, S.A. de C.V.	0614-290826-001-5	123456-7
2	OCC	Sucursal Occidente - Santa Ana	\N	f	\N	\N	\N
3	ORI	Sucursal Oriente - San Miguel	\N	f	\N	\N	\N
\.


--
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuario (id, username, email, password_hash, nombre_completo, activo, fecha_creacion, ultimo_acceso, sucursal_id) FROM stdin;
9	compras	compras@optimatech.com	$pbkdf2-sha256$29000$ck7J.d87J6Q0BoAwRkip9Q$bxIc3FPm7LNqVJieHdRQh.PnA0r3xBtDVTSX32/aKJg	Compras Demo	t	2026-10-21 20:12:30.304799	\N	\N
10	planilla	planilla@optimatech.com	$pbkdf2-sha256$29000$pvTeW0spBSCE0FprjZFSqg$kMopLPpisvspp6FRpDRg8fMz6qPaQEVnlUR7NSDNCtg	Planilla Demo	t	2026-10-21 20:12:30.304799	\N	\N
11	auditor	auditor@optimatech.com	$pbkdf2-sha256$29000$r9V6z7lXCmGsFQIgZEypFQ$5GKbgaUGkCz3EPcVROk.fd9K1weY32xWprbvQNQbCxo	Auditor Demo	t	2026-10-21 20:12:30.304799	\N	\N
2	admin	admin@optimatech.com	$pbkdf2-sha256$29000$JOQcY0zJ2fsfQ4hxLmUs5Q$k5d1onYcsx9TEC5vMsLEeN0bDc.IRnQzqwWbc972b88	Administrador	t	2026-10-20 03:22:18.55509	2026-10-21 21:06:19.378357	\N
7	auxiliar	auxiliar@optimatech.com	$pbkdf2-sha256$29000$.H.PUQqB8F7rfY.RsnZOiQ$4SHRclpLxH3AZnValWdOwn4Qc2gePmN1pBrl8bktCcU	Auxiliar Demo	t	2026-10-21 20:12:30.304799	2026-10-21 21:06:19.397401	\N
6	contador	contador@optimatech.com	$pbkdf2-sha256$29000$u7e2FuIcwxhj7F0rBQDAuA$pxW058pcxOmK1z8WpPqj8pZS0AObP/tdHX/V8RXmeW4	Contador Demo	t	2026-10-21 20:12:30.304799	2026-10-21 21:06:19.40681	\N
8	ventas	ventas@optimatech.com	$pbkdf2-sha256$29000$U0ppjTFGCAEAwHgvJQTgPA$9QZziPOkxaEWqxBGF0TKgA5c7xJJCtODklDbtGo7A7c	Ventas Demo	t	2026-10-21 20:12:30.304799	2026-10-21 20:52:08.642921	\N
\.


--
-- Data for Name: usuario_rol; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuario_rol (usuario_id, rol_id) FROM stdin;
2	8
6	9
7	10
8	11
9	12
10	13
11	14
\.


--
-- Name: asiento_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.asiento_id_seq', 8, true);


--
-- Name: auditoria_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auditoria_id_seq', 5, true);


--
-- Name: cliente_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cliente_id_seq', 2, true);


--
-- Name: compra_detalle_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.compra_detalle_id_seq', 1, false);


--
-- Name: compra_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.compra_id_seq', 1, false);


--
-- Name: detalle_asiento_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.detalle_asiento_id_seq', 27, true);


--
-- Name: empleado_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.empleado_id_seq', 2, true);


--
-- Name: empresa_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.empresa_id_seq', 1, false);


--
-- Name: factura_detalle_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.factura_detalle_id_seq', 2, true);


--
-- Name: factura_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.factura_id_seq', 1, true);


--
-- Name: periodo_contable_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.periodo_contable_id_seq', 1, true);


--
-- Name: permiso_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.permiso_id_seq', 136, true);


--
-- Name: planilla_detalle_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.planilla_detalle_id_seq', 2, true);


--
-- Name: planilla_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.planilla_id_seq', 1, true);


--
-- Name: proveedor_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.proveedor_id_seq', 1, false);


--
-- Name: rol_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.rol_id_seq', 14, true);


--
-- Name: sucursal_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sucursal_id_seq', 3, true);


--
-- Name: usuario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuario_id_seq', 11, true);


--
-- Name: asiento asiento_codigo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asiento
    ADD CONSTRAINT asiento_codigo_key UNIQUE (codigo);


--
-- Name: asiento asiento_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asiento
    ADD CONSTRAINT asiento_pkey PRIMARY KEY (id);


--
-- Name: auditoria auditoria_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditoria
    ADD CONSTRAINT auditoria_pkey PRIMARY KEY (id);


--
-- Name: catalogo_cuenta catalogo_cuenta_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.catalogo_cuenta
    ADD CONSTRAINT catalogo_cuenta_pkey PRIMARY KEY (codigo);


--
-- Name: cliente cliente_codigo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_codigo_key UNIQUE (codigo);


--
-- Name: cliente cliente_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_pkey PRIMARY KEY (id);


--
-- Name: compra_detalle compra_detalle_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra_detalle
    ADD CONSTRAINT compra_detalle_pkey PRIMARY KEY (id);


--
-- Name: compra compra_numero_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra
    ADD CONSTRAINT compra_numero_key UNIQUE (numero);


--
-- Name: compra compra_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra
    ADD CONSTRAINT compra_pkey PRIMARY KEY (id);


--
-- Name: detalle_asiento detalle_asiento_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_asiento
    ADD CONSTRAINT detalle_asiento_pkey PRIMARY KEY (id);


--
-- Name: empleado empleado_codigo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.empleado
    ADD CONSTRAINT empleado_codigo_key UNIQUE (codigo);


--
-- Name: empleado empleado_dui_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.empleado
    ADD CONSTRAINT empleado_dui_key UNIQUE (dui);


--
-- Name: empleado empleado_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.empleado
    ADD CONSTRAINT empleado_pkey PRIMARY KEY (id);


--
-- Name: empresa empresa_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.empresa
    ADD CONSTRAINT empresa_pkey PRIMARY KEY (id);


--
-- Name: factura_detalle factura_detalle_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.factura_detalle
    ADD CONSTRAINT factura_detalle_pkey PRIMARY KEY (id);


--
-- Name: factura factura_numero_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.factura
    ADD CONSTRAINT factura_numero_key UNIQUE (numero);


--
-- Name: factura factura_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.factura
    ADD CONSTRAINT factura_pkey PRIMARY KEY (id);


--
-- Name: periodo_contable periodo_contable_anio_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.periodo_contable
    ADD CONSTRAINT periodo_contable_anio_key UNIQUE (anio);


--
-- Name: periodo_contable periodo_contable_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.periodo_contable
    ADD CONSTRAINT periodo_contable_pkey PRIMARY KEY (id);


--
-- Name: permiso permiso_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permiso
    ADD CONSTRAINT permiso_pkey PRIMARY KEY (id);


--
-- Name: planilla planilla_codigo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planilla
    ADD CONSTRAINT planilla_codigo_key UNIQUE (codigo);


--
-- Name: planilla_detalle planilla_detalle_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planilla_detalle
    ADD CONSTRAINT planilla_detalle_pkey PRIMARY KEY (id);


--
-- Name: planilla_detalle planilla_detalle_planilla_id_empleado_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planilla_detalle
    ADD CONSTRAINT planilla_detalle_planilla_id_empleado_id_key UNIQUE (planilla_id, empleado_id);


--
-- Name: planilla planilla_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planilla
    ADD CONSTRAINT planilla_pkey PRIMARY KEY (id);


--
-- Name: proveedor proveedor_codigo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proveedor
    ADD CONSTRAINT proveedor_codigo_key UNIQUE (codigo);


--
-- Name: proveedor proveedor_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proveedor
    ADD CONSTRAINT proveedor_pkey PRIMARY KEY (id);


--
-- Name: rol_permiso rol_permiso_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rol_permiso
    ADD CONSTRAINT rol_permiso_pkey PRIMARY KEY (rol_id, permiso_id);


--
-- Name: rol rol_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rol
    ADD CONSTRAINT rol_pkey PRIMARY KEY (id);


--
-- Name: sucursal sucursal_codigo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sucursal
    ADD CONSTRAINT sucursal_codigo_key UNIQUE (codigo);


--
-- Name: sucursal sucursal_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sucursal
    ADD CONSTRAINT sucursal_pkey PRIMARY KEY (id);


--
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id);


--
-- Name: usuario_rol usuario_rol_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_rol
    ADD CONSTRAINT usuario_rol_pkey PRIMARY KEY (usuario_id, rol_id);


--
-- Name: idx_asiento_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_asiento_fecha ON public.asiento USING btree (fecha);


--
-- Name: idx_asiento_periodo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_asiento_periodo ON public.asiento USING btree (periodo_id);


--
-- Name: idx_asiento_reverso_unico; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_asiento_reverso_unico ON public.asiento USING btree (reverso_de_id) WHERE (reverso_de_id IS NOT NULL);


--
-- Name: idx_auditoria_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_auditoria_fecha ON public.auditoria USING btree (fecha);


--
-- Name: idx_auditoria_modulo_accion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_auditoria_modulo_accion ON public.auditoria USING btree (modulo, accion);


--
-- Name: idx_auditoria_registro; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_auditoria_registro ON public.auditoria USING btree (entidad, registro_id);


--
-- Name: idx_auditoria_usuario; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_auditoria_usuario ON public.auditoria USING btree (usuario_id);


--
-- Name: idx_compra_detalle_compra; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_compra_detalle_compra ON public.compra_detalle USING btree (compra_id);


--
-- Name: idx_compra_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_compra_fecha ON public.compra USING btree (fecha);


--
-- Name: idx_compra_proveedor; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_compra_proveedor ON public.compra USING btree (proveedor_id);


--
-- Name: idx_cuenta_nivel; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_cuenta_nivel ON public.catalogo_cuenta USING btree (nivel);


--
-- Name: idx_cuenta_padre; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_cuenta_padre ON public.catalogo_cuenta USING btree (codigo_padre);


--
-- Name: idx_detalle_asiento; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_detalle_asiento ON public.detalle_asiento USING btree (asiento_id);


--
-- Name: idx_detalle_cuenta; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_detalle_cuenta ON public.detalle_asiento USING btree (cuenta_codigo);


--
-- Name: idx_factura_cliente; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_factura_cliente ON public.factura USING btree (cliente_id);


--
-- Name: idx_factura_detalle_factura; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_factura_detalle_factura ON public.factura_detalle USING btree (factura_id);


--
-- Name: idx_planilla_detalle_planilla; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_planilla_detalle_planilla ON public.planilla_detalle USING btree (planilla_id);


--
-- Name: idx_planilla_periodo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_planilla_periodo ON public.planilla USING btree (periodo);


--
-- Name: ix_permiso_codigo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_permiso_codigo ON public.permiso USING btree (codigo);


--
-- Name: ix_permiso_modulo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_permiso_modulo ON public.permiso USING btree (modulo);


--
-- Name: ix_rol_codigo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_rol_codigo ON public.rol USING btree (codigo);


--
-- Name: ix_usuario_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_usuario_email ON public.usuario USING btree (email);


--
-- Name: ix_usuario_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_usuario_username ON public.usuario USING btree (username);


--
-- Name: asiento asiento_anulado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asiento
    ADD CONSTRAINT asiento_anulado_por_fkey FOREIGN KEY (anulado_por) REFERENCES public.usuario(id) ON DELETE SET NULL;


--
-- Name: asiento asiento_aprobado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asiento
    ADD CONSTRAINT asiento_aprobado_por_fkey FOREIGN KEY (aprobado_por) REFERENCES public.usuario(id) ON DELETE SET NULL;


--
-- Name: asiento asiento_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asiento
    ADD CONSTRAINT asiento_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuario(id) ON DELETE SET NULL;


--
-- Name: asiento asiento_periodo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asiento
    ADD CONSTRAINT asiento_periodo_id_fkey FOREIGN KEY (periodo_id) REFERENCES public.periodo_contable(id);


--
-- Name: asiento asiento_reverso_de_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asiento
    ADD CONSTRAINT asiento_reverso_de_id_fkey FOREIGN KEY (reverso_de_id) REFERENCES public.asiento(id) ON DELETE RESTRICT;


--
-- Name: asiento asiento_sucursal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asiento
    ADD CONSTRAINT asiento_sucursal_id_fkey FOREIGN KEY (sucursal_id) REFERENCES public.sucursal(id);


--
-- Name: auditoria auditoria_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditoria
    ADD CONSTRAINT auditoria_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id) ON DELETE SET NULL;


--
-- Name: catalogo_cuenta catalogo_cuenta_codigo_padre_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.catalogo_cuenta
    ADD CONSTRAINT catalogo_cuenta_codigo_padre_fkey FOREIGN KEY (codigo_padre) REFERENCES public.catalogo_cuenta(codigo);


--
-- Name: cliente cliente_cuenta_codigo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_cuenta_codigo_fkey FOREIGN KEY (cuenta_codigo) REFERENCES public.catalogo_cuenta(codigo);


--
-- Name: cliente cliente_sucursal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_sucursal_id_fkey FOREIGN KEY (sucursal_id) REFERENCES public.sucursal(id);


--
-- Name: compra compra_aprobado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra
    ADD CONSTRAINT compra_aprobado_por_fkey FOREIGN KEY (aprobado_por) REFERENCES public.usuario(id) ON DELETE SET NULL;


--
-- Name: compra compra_asiento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra
    ADD CONSTRAINT compra_asiento_id_fkey FOREIGN KEY (asiento_id) REFERENCES public.asiento(id);


--
-- Name: compra compra_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra
    ADD CONSTRAINT compra_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuario(id) ON DELETE SET NULL;


--
-- Name: compra_detalle compra_detalle_compra_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra_detalle
    ADD CONSTRAINT compra_detalle_compra_id_fkey FOREIGN KEY (compra_id) REFERENCES public.compra(id) ON DELETE CASCADE;


--
-- Name: compra_detalle compra_detalle_cuenta_activo_codigo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra_detalle
    ADD CONSTRAINT compra_detalle_cuenta_activo_codigo_fkey FOREIGN KEY (cuenta_activo_codigo) REFERENCES public.catalogo_cuenta(codigo);


--
-- Name: compra compra_periodo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra
    ADD CONSTRAINT compra_periodo_id_fkey FOREIGN KEY (periodo_id) REFERENCES public.periodo_contable(id);


--
-- Name: compra compra_proveedor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra
    ADD CONSTRAINT compra_proveedor_id_fkey FOREIGN KEY (proveedor_id) REFERENCES public.proveedor(id);


--
-- Name: compra compra_sucursal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra
    ADD CONSTRAINT compra_sucursal_id_fkey FOREIGN KEY (sucursal_id) REFERENCES public.sucursal(id);


--
-- Name: detalle_asiento detalle_asiento_asiento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_asiento
    ADD CONSTRAINT detalle_asiento_asiento_id_fkey FOREIGN KEY (asiento_id) REFERENCES public.asiento(id) ON DELETE CASCADE;


--
-- Name: detalle_asiento detalle_asiento_cuenta_codigo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_asiento
    ADD CONSTRAINT detalle_asiento_cuenta_codigo_fkey FOREIGN KEY (cuenta_codigo) REFERENCES public.catalogo_cuenta(codigo);


--
-- Name: empleado empleado_cuenta_anticipo_codigo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.empleado
    ADD CONSTRAINT empleado_cuenta_anticipo_codigo_fkey FOREIGN KEY (cuenta_anticipo_codigo) REFERENCES public.catalogo_cuenta(codigo);


--
-- Name: empleado empleado_sucursal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.empleado
    ADD CONSTRAINT empleado_sucursal_id_fkey FOREIGN KEY (sucursal_id) REFERENCES public.sucursal(id);


--
-- Name: factura factura_aprobado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.factura
    ADD CONSTRAINT factura_aprobado_por_fkey FOREIGN KEY (aprobado_por) REFERENCES public.usuario(id) ON DELETE SET NULL;


--
-- Name: factura factura_asiento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.factura
    ADD CONSTRAINT factura_asiento_id_fkey FOREIGN KEY (asiento_id) REFERENCES public.asiento(id);


--
-- Name: factura factura_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.factura
    ADD CONSTRAINT factura_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.cliente(id);


--
-- Name: factura factura_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.factura
    ADD CONSTRAINT factura_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuario(id) ON DELETE SET NULL;


--
-- Name: factura_detalle factura_detalle_cuenta_ingreso_codigo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.factura_detalle
    ADD CONSTRAINT factura_detalle_cuenta_ingreso_codigo_fkey FOREIGN KEY (cuenta_ingreso_codigo) REFERENCES public.catalogo_cuenta(codigo);


--
-- Name: factura_detalle factura_detalle_factura_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.factura_detalle
    ADD CONSTRAINT factura_detalle_factura_id_fkey FOREIGN KEY (factura_id) REFERENCES public.factura(id) ON DELETE CASCADE;


--
-- Name: factura factura_periodo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.factura
    ADD CONSTRAINT factura_periodo_id_fkey FOREIGN KEY (periodo_id) REFERENCES public.periodo_contable(id);


--
-- Name: factura factura_sucursal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.factura
    ADD CONSTRAINT factura_sucursal_id_fkey FOREIGN KEY (sucursal_id) REFERENCES public.sucursal(id);


--
-- Name: planilla planilla_aprobado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planilla
    ADD CONSTRAINT planilla_aprobado_por_fkey FOREIGN KEY (aprobado_por) REFERENCES public.usuario(id) ON DELETE SET NULL;


--
-- Name: planilla planilla_asiento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planilla
    ADD CONSTRAINT planilla_asiento_id_fkey FOREIGN KEY (asiento_id) REFERENCES public.asiento(id);


--
-- Name: planilla planilla_creado_por_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planilla
    ADD CONSTRAINT planilla_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES public.usuario(id) ON DELETE SET NULL;


--
-- Name: planilla_detalle planilla_detalle_empleado_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planilla_detalle
    ADD CONSTRAINT planilla_detalle_empleado_id_fkey FOREIGN KEY (empleado_id) REFERENCES public.empleado(id);


--
-- Name: planilla_detalle planilla_detalle_planilla_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planilla_detalle
    ADD CONSTRAINT planilla_detalle_planilla_id_fkey FOREIGN KEY (planilla_id) REFERENCES public.planilla(id) ON DELETE CASCADE;

-- Name: planilla_detalle planilla_detalle_cuenta_gasto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
ALTER TABLE ONLY public.planilla_detalle
    ADD CONSTRAINT planilla_detalle_cuenta_gasto_fkey FOREIGN KEY (cuenta_gasto_codigo) REFERENCES public.catalogo_cuenta(codigo) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: planilla planilla_periodo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planilla
    ADD CONSTRAINT planilla_periodo_id_fkey FOREIGN KEY (periodo_id) REFERENCES public.periodo_contable(id);


--
-- Name: planilla planilla_sucursal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.planilla
    ADD CONSTRAINT planilla_sucursal_id_fkey FOREIGN KEY (sucursal_id) REFERENCES public.sucursal(id);


--
-- Name: proveedor proveedor_cuenta_codigo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proveedor
    ADD CONSTRAINT proveedor_cuenta_codigo_fkey FOREIGN KEY (cuenta_codigo) REFERENCES public.catalogo_cuenta(codigo);


--
-- Name: proveedor proveedor_sucursal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proveedor
    ADD CONSTRAINT proveedor_sucursal_id_fkey FOREIGN KEY (sucursal_id) REFERENCES public.sucursal(id);


--
-- Name: rol_permiso rol_permiso_permiso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rol_permiso
    ADD CONSTRAINT rol_permiso_permiso_id_fkey FOREIGN KEY (permiso_id) REFERENCES public.permiso(id);


--
-- Name: rol_permiso rol_permiso_rol_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rol_permiso
    ADD CONSTRAINT rol_permiso_rol_id_fkey FOREIGN KEY (rol_id) REFERENCES public.rol(id);


--
-- Name: usuario_rol usuario_rol_rol_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_rol
    ADD CONSTRAINT usuario_rol_rol_id_fkey FOREIGN KEY (rol_id) REFERENCES public.rol(id);


--
-- Name: usuario_rol usuario_rol_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_rol
    ADD CONSTRAINT usuario_rol_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id);


--
-- Name: usuario usuario_sucursal_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_sucursal_id_fkey FOREIGN KEY (sucursal_id) REFERENCES public.sucursal(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


--
-- PostgreSQL database dump complete
--

\unrestrict MJRlvMcCLV4AVCra0WQYSHj5bM4ac4QdrcFRAAMAqTkNKIeRLcXs3vcvqKumXr7

