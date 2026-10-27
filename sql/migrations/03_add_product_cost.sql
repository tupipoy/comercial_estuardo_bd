-- Ejecutar una sola vez en la base existente para guardar el costo actual del producto.
-- Los productos existentes reciben 0.00 hasta que se actualice su costo real.
-- Archivo: sql/migrations/03_add_product_cost.sql
-- Autor: Equipo Comercial Estuardo
-- Descripción: agrega el costo vigente del producto a esquemas existentes.
-- Dependencias: esquema previo de comercial_estuardo_db; verificar que la columna no exista.
USE comercial_estuardo_db;

ALTER TABLE PRODUCTO
    ADD COLUMN precio_costo DECIMAL(10,2) NOT NULL DEFAULT 0.00 AFTER descripcion;

ALTER TABLE PRODUCTO
    ADD CONSTRAINT chk_producto_precio_costo CHECK (precio_costo >= 0);
