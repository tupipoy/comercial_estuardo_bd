-- Ejecutar una sola vez en la base existente para habilitar contraseñas hash.
-- Los empleados existentes conservarán NULL hasta que se les asigne un hash.
USE comercial_estuardo_db;

ALTER TABLE EMPLEADO
    ADD COLUMN password_hash VARCHAR(255) NULL AFTER correo;
