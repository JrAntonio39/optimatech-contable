-- Restaura la contraseña solicitada para la cuenta de demostración admin.
-- Ejecutar una sola vez en la base ya inicializada; no modifica otros datos.
BEGIN;

UPDATE public.usuario
   SET password_hash = '$pbkdf2-sha256$29000$JOQcY0zJ2fsfQ4hxLmUs5Q$k5d1onYcsx9TEC5vMsLEeN0bDc.IRnQzqwWbc972b88'
 WHERE username = 'admin'
   AND email = 'admin@optimatech.com';

COMMIT;
