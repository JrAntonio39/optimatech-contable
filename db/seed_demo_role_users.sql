-- Agrega cuentas de demostración para probar los roles existentes.
-- Clave compartida solo para pruebas locales: Demo1234
-- El script se puede ejecutar varias veces sin duplicar usuarios ni relaciones.
BEGIN;

INSERT INTO public.usuario
    (username, email, password_hash, nombre_completo, activo, fecha_creacion)
VALUES
    ('contador', 'contador@optimatech.com', '$pbkdf2-sha256$29000$IHbuaBIv3rBESNC5OS6CI7Gf$qjq/yBQhEhDp1RB7LpbWiDILmHSQ9zu7F0fU4gUYgx4', 'Usuario Demo - Contador', TRUE, CURRENT_TIMESTAMP),
    ('auxiliar', 'auxiliar@optimatech.com', '$pbkdf2-sha256$29000$lY7DCU4i.xgLzakyyLbBcBZI$baYQ4g9.rb0lsQ9qhhOxUkwt5.FAyx17Fb.xiXDMpLc', 'Usuario Demo - Auxiliar', TRUE, CURRENT_TIMESTAMP),
    ('ventas', 'ventas@optimatech.com', '$pbkdf2-sha256$29000$.qtsPbFRBA06pj.AQ/JzaAWX$Ru5228HSN3Vs4VSnM9UHsVxiRIFYSPowaAdYMPdUfDw', 'Usuario Demo - Ventas', TRUE, CURRENT_TIMESTAMP),
    ('compras', 'compras@optimatech.com', '$pbkdf2-sha256$29000$avedPQ5nKQueffL5VWcCJUfq$WWRXdN9XM1T0Uho4Rk3DAlRUmpwbzqPLmMutJfKW1W0', 'Usuario Demo - Compras', TRUE, CURRENT_TIMESTAMP),
    ('planilla', 'planilla@optimatech.com', '$pbkdf2-sha256$29000$gsk5zU9jlHAti8DO.USCvKwX$NNr99Kxe9DeajHFp4M0pJSB/Ly3GQcFg.lpIs1ioLs0', 'Usuario Demo - Planilla', TRUE, CURRENT_TIMESTAMP),
    ('auditor', 'auditor@optimatech.com', '$pbkdf2-sha256$29000$CTzQMK6nh4cRPI4wRJjterlP$lN2ZBLBW1tFP.J2ZTEV2p5ZnxCIZvsKPtYS/p0Fyo0Q', 'Usuario Demo - Auditor', TRUE, CURRENT_TIMESTAMP)
ON CONFLICT (username) DO NOTHING;

INSERT INTO public.usuario_rol (usuario_id, rol_id)
SELECT u.id, r.id
  FROM public.usuario AS u
  JOIN public.rol AS r ON r.codigo = u.username
 WHERE u.username IN ('contador', 'auxiliar', 'ventas', 'compras', 'planilla', 'auditor')
ON CONFLICT DO NOTHING;

COMMIT;
