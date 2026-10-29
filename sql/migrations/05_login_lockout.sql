-- Archivo: sql/migrations/05_login_lockout.sql
-- Autor: Equipo Comercial Estuardo
-- Descripción: actualiza de forma incremental el esquema existente.
-- Dependencias: Esquema y objetos previos según INSTALL.md; no ejecutar sobre producción sin respaldo.
-- Ejecutar una sola vez en bases existentes para limitar intentos de acceso.
-- Bloqueo progresivo: la aplicación calcula la duración según los fallos.
USE comercial_estuardo_db;

ALTER TABLE EMPLEADO
    ADD COLUMN intentos_login_fallidos TINYINT UNSIGNED NOT NULL DEFAULT 0
        AFTER password_hash,
    ADD COLUMN bloqueado_hasta DATETIME NULL
        AFTER intentos_login_fallidos;
