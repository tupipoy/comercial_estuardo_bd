USE comercial_estuardo_db;

-- Permite volver a aplicar el archivo para actualizar estos triggers.
DROP TRIGGER IF EXISTS trg_descontar_stock_venta;
DROP TRIGGER IF EXISTS trg_validar_stock_venta;

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

DELIMITER ;
