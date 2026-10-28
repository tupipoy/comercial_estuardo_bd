-- Ejecutar una sola vez en bases existentes para limitar intentos de acceso.
-- Bloqueo progresivo: la aplicación calcula la duración según los fallos.
USE comercial_estuardo_db;

ALTER TABLE EMPLEADO
    ADD COLUMN intentos_login_fallidos TINYINT UNSIGNED NOT NULL DEFAULT 0
        AFTER password_hash,
    ADD COLUMN bloqueado_hasta DATETIME NULL
        AFTER intentos_login_fallidos;
