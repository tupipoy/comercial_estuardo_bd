-- Ejecutar una vez en la base comercial_estuardo_db ya desplegada.
-- Protege las escrituras SQL directas, además de las validaciones de Flask.
USE comercial_estuardo_db;

-- Revisa primero los registros existentes; corrige cualquier precio bajo costo.
SELECT id_producto, nombre, precio_costo, precio_venta
FROM PRODUCTO
WHERE precio_venta < precio_costo;

DROP TRIGGER IF EXISTS trg_validar_margen_venta;
DROP TRIGGER IF EXISTS trg_producto_margen_insert;
DROP TRIGGER IF EXISTS trg_producto_margen_update;

DELIMITER $$

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
