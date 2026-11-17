BEGIN;

-- Cuenta control única para facturas emitidas al crédito.
INSERT INTO public.catalogo_cuenta (codigo, nombre, naturaleza, nivel, codigo_padre)
VALUES ('1.1.3.01.04', 'Clientes por Cobrar - General', 'Deudora', 5, '1.1.3.01')
ON CONFLICT (codigo) DO NOTHING;

-- Las fichas dejan de elegir una cuenta distinta por cliente.
UPDATE public.cliente
   SET cuenta_codigo = '1.1.3.01.04'
 WHERE cuenta_codigo IS DISTINCT FROM '1.1.3.01.04';

COMMIT;
