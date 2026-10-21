-- Restaura las credenciales de demostración del usuario administrador.
-- Ejecutar una sola vez en una base ya inicializada; no elimina ni recrea datos.
BEGIN;

UPDATE public.usuario
   SET password_hash = '$pbkdf2-sha256$29000$iG72RDyiFF.VfO9MdMDG9Ia2$3Z3Ers1/RerXorcrcFdaW1r3yWwjEZdgFJUXZbCyn18'
 WHERE username = 'admin'
   AND email = 'admin@optimatech.com';

COMMIT;
