USE comercial_estuardo_db;

-- Los procedimientos asumen que existen las tablas y, para ventas,
-- los triggers definidos en sql/triggers/01_triggers.sql.
DROP PROCEDURE IF EXISTS sp_registrar_venta;
DROP PROCEDURE IF EXISTS sp_registrar_compra;

DELIMITER $$

-- =========================================================
-- PROCEDIMIENTO 1: REGISTRAR VENTA
-- Justificación: registra cabecera y detalle como una sola
-- operación. Si falla el detalle o la validación de stock,
-- también se revierte la cabecera.
-- El trigger de DETALLE_VENTA controla y descuenta existencias.
-- =========================================================
CREATE PROCEDURE sp_registrar_venta(
    IN p_serie_factura VARCHAR(10),
    IN p_numero_factura INT,
    IN p_tipo_pago VARCHAR(30),
    IN p_id_cliente INT,
    IN p_id_empleado INT,
    IN p_id_sucursal INT,
    IN p_id_producto INT,
    IN p_cantidad INT,
    IN p_precio_unitario DECIMAL(10,2),
    IN p_descuento DECIMAL(10,2)
)
BEGIN
    DECLARE v_id_venta INT;
    DECLARE v_total_bruto DECIMAL(12,2);
    DECLARE v_subtotal DECIMAL(12,2);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    IF p_serie_factura IS NULL OR CHAR_LENGTH(TRIM(p_serie_factura)) = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'La serie de factura es obligatoria';
    END IF;

    IF p_numero_factura IS NULL OR p_numero_factura <= 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El número de factura debe ser mayor que cero';
    END IF;

    IF p_tipo_pago IS NULL OR p_tipo_pago NOT IN (
        'Efectivo', 'Transferencia', 'Depósito Bancario'
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El tipo de pago no es válido';
    END IF;

    IF p_cantidad IS NULL OR p_cantidad <= 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'La cantidad debe ser mayor que cero';
    END IF;

    IF p_precio_unitario IS NULL OR p_precio_unitario <= 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El precio unitario debe ser mayor que cero';
    END IF;

    IF p_descuento IS NULL OR p_descuento < 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El descuento no puede ser negativo';
    END IF;

    SET v_total_bruto = p_cantidad * p_precio_unitario;
    IF p_descuento > v_total_bruto THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El descuento no puede superar el importe bruto';
    END IF;
    SET v_subtotal = v_total_bruto - p_descuento;

    INSERT INTO VENTA (
        serie_factura,
        numero_factura,
        fecha_venta,
        total_venta,
        tipo_pago,
        estado,
        id_cliente,
        id_empleado,
        id_sucursal
    ) VALUES (
        p_serie_factura,
        p_numero_factura,
        NOW(),
        v_subtotal,
        p_tipo_pago,
        'Emitida',
        p_id_cliente,
        p_id_empleado,
        p_id_sucursal
    );

    SET v_id_venta = LAST_INSERT_ID();

    INSERT INTO DETALLE_VENTA (
        id_venta,
        id_producto,
        vin_chasis,
        numero_motor,
        cantidad,
        precio_unitario,
        descuento,
        subtotal
    ) VALUES (
        v_id_venta,
        p_id_producto,
        NULL,
        NULL,
        p_cantidad,
        p_precio_unitario,
        p_descuento,
        v_subtotal
    );

    -- El trigger trg_descontar_stock_venta actualiza el inventario.
    COMMIT;
END$$

-- =========================================================
-- PROCEDIMIENTO 2: REGISTRAR COMPRA
-- Justificación: registra compra y detalle de forma atómica;
-- al recibirla, actualiza existencias y el costo vigente del
-- producto. El detalle conserva el costo histórico de compra.
-- =========================================================
CREATE PROCEDURE sp_registrar_compra(
    IN p_numero_orden VARCHAR(30),
    IN p_id_proveedor INT,
    IN p_id_empleado INT,
    IN p_id_producto INT,
    IN p_cantidad INT,
    IN p_costo_unitario DECIMAL(10,2)
)
BEGIN
    DECLARE v_id_compra INT;
    DECLARE v_subtotal DECIMAL(12,2);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    IF p_numero_orden IS NULL OR CHAR_LENGTH(TRIM(p_numero_orden)) = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El número de orden es obligatorio';
    END IF;

    IF p_cantidad IS NULL OR p_cantidad <= 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'La cantidad debe ser mayor que cero';
    END IF;

    IF p_costo_unitario IS NULL OR p_costo_unitario <= 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El costo unitario debe ser mayor que cero';
    END IF;

    SET v_subtotal = p_cantidad * p_costo_unitario;

    INSERT INTO COMPRA (
        numero_orden,
        fecha_compra,
        total_compra,
        estado_recepcion,
        id_proveedor,
        id_empleado
    ) VALUES (
        p_numero_orden,
        NOW(),
        v_subtotal,
        'Recibido',
        p_id_proveedor,
        p_id_empleado
    );

    SET v_id_compra = LAST_INSERT_ID();

    INSERT INTO DETALLE_COMPRA (
        id_compra,
        id_producto,
        cantidad,
        costo_unitario,
        subtotal
    ) VALUES (
        v_id_compra,
        p_id_producto,
        p_cantidad,
        p_costo_unitario,
        v_subtotal
    );

    UPDATE PRODUCTO
       SET stock_actual = stock_actual + p_cantidad,
           precio_costo = p_costo_unitario
     WHERE id_producto = p_id_producto;

    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El producto indicado no existe';
    END IF;

    COMMIT;
END$$

DELIMITER ;
