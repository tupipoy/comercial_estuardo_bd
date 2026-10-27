-- Ejecutar una sola vez en la base existente para habilitar contraseñas hash.
-- Los empleados existentes conservarán NULL hasta que se les asigne un hash.
-- Archivo: sql/migrations/02_add_employee_password_hash.sql
-- Autor: Equipo Comercial Estuardo
-- Descripción: agrega el campo para guardar hashes de contraseña de empleado.
-- Dependencias: esquema previo de comercial_estuardo_db; verificar que la columna no exista.
USE comercial_estuardo_db;

ALTER TABLE EMPLEADO
    ADD COLUMN password_hash VARCHAR(255) NULL AFTER correo;
