-- Archivo: sql/triggers/01_triggers.sql
-- Autor: Equipo Comercial Estuardo
-- Descripción: valida y descuenta existencias al insertar detalles de venta.
-- Dependencias: sql/ddl/01_schema.sql; InnoDB; ejecutar antes de los procedimientos.
USE comercial_estuardo_db;

-- IMPORTANTE: ejecutar el archivo completo en MySQL Workbench (Execute All).
-- No ejecutar solo las líneas CREATE TRIGGER: Workbench necesita procesar
-- DELIMITER $$ antes del cuerpo compuesto y DELIMITER ; al terminar.
-- Permite volver a aplicar el archivo para actualizar estos triggers.
DROP TRIGGER IF EXISTS trg_descontar_stock_venta;
DROP TRIGGER IF EXISTS trg_validar_stock_venta;
DROP TRIGGER IF EXISTS trg_validar_margen_venta;
DROP TRIGGER IF EXISTS trg_producto_margen_insert;
DROP TRIGGER IF EXISTS trg_producto_margen_update;

DELIMITER $$

-- =========================================================
-- TRIGGER 1: VALIDAR STOCK DISPONIBLE
-- Bloquea la fila del producto mientras valida la existencia,
-- para evitar que dos ventas concurrentes consuman el mismo stock.
-- =========================================================
CREATE TRIGGER trg_validar_stock_venta
BEFORE INSERT ON DETALLE_VENTA
FOR EACH ROW
BEGIN
    DECLARE v_stock_actual INT DEFAULT NULL;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_stock_actual = NULL;

    SELECT stock_actual
      INTO v_stock_actual
      FROM PRODUCTO
     WHERE id_producto = NEW.id_producto
     FOR UPDATE;

    IF v_stock_actual IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El producto indicado no existe';
    END IF;

    IF v_stock_actual < NEW.cantidad THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Stock insuficiente para realizar la venta';
    END IF;
END$$

-- =========================================================
-- TRIGGER 2: DESCONTAR STOCK
-- Actualiza las existencias después de guardar cada detalle.
-- =========================================================
CREATE TRIGGER trg_descontar_stock_venta
AFTER INSERT ON DETALLE_VENTA
FOR EACH ROW
BEGIN
    UPDATE PRODUCTO
       SET stock_actual = stock_actual - NEW.cantidad
     WHERE id_producto = NEW.id_producto;
END$$

-- =========================================================
-- TRIGGER 3: IMPEDIR VENTAS BAJO COSTO
-- Incluye descuentos aplicados a toda la línea.
-- =========================================================
CREATE TRIGGER trg_validar_margen_venta
BEFORE INSERT ON DETALLE_VENTA
FOR EACH ROW
BEGIN
    DECLARE v_costo DECIMAL(10,2) DEFAULT NULL;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_costo = NULL;

    SELECT precio_costo INTO v_costo
      FROM PRODUCTO
     WHERE id_producto = NEW.id_producto
     FOR UPDATE;

    IF v_costo IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No se pudo validar el costo del producto';
    END IF;

    IF NEW.cantidad * NEW.precio_unitario - NEW.descuento < NEW.cantidad * v_costo THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'La venta y el descuento no pueden quedar por debajo del costo';
    END IF;
END$$

-- Impiden registrar o cambiar productos dejando el precio por debajo del costo.
CREATE TRIGGER trg_producto_margen_insert
BEFORE INSERT ON PRODUCTO
FOR EACH ROW
BEGIN
    IF NEW.precio_venta < NEW.precio_costo THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El precio de venta no puede ser menor que el costo';
    END IF;
END$$

CREATE TRIGGER trg_producto_margen_update
BEFORE UPDATE ON PRODUCTO
FOR EACH ROW
BEGIN
    IF NEW.precio_venta < NEW.precio_costo THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El precio de venta no puede ser menor que el costo';
    END IF;
END$$

DELIMITER ;
