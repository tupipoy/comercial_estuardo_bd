-- Archivo: sql/procedures/02_transfer_workflow.sql
-- Autor: Equipo Comercial Estuardo
-- Descripción: implementa operaciones transaccionales.
-- Dependencias: Esquema y objetos previos según INSTALL.md; no ejecutar sobre producción sin respaldo.
-- Flujo de solicitud, aprobacion, despacho y recepcion de traslados.
USE comercial_estuardo_db;

DROP PROCEDURE IF EXISTS sp_registrar_traslado;
DROP PROCEDURE IF EXISTS sp_resolver_traslado;
DROP PROCEDURE IF EXISTS sp_despachar_traslado;
DROP PROCEDURE IF EXISTS sp_recibir_traslado;

DELIMITER $$

CREATE PROCEDURE sp_registrar_traslado(
    IN p_numero_traslado VARCHAR(30),
    IN p_id_sucursal_origen INT,
    IN p_id_sucursal_destino INT,
    IN p_id_empleado INT,
    IN p_detalles JSON
)
BEGIN
    DECLARE v_id_traslado INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
    START TRANSACTION;
    IF p_id_sucursal_origen = p_id_sucursal_destino THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El origen y destino deben ser distintos';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM SUCURSAL WHERE id_sucursal=p_id_sucursal_origen AND estado=1)
       OR NOT EXISTS (SELECT 1 FROM SUCURSAL WHERE id_sucursal=p_id_sucursal_destino AND estado=1) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Las sucursales deben estar activas';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM EMPLEADO WHERE id_empleado=p_id_empleado AND estado=1
        AND (cargo='Administrador' OR (cargo='Bodega' AND id_sucursal=p_id_sucursal_origen))) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No puedes solicitar traslados desde esa sucursal';
    END IF;
    IF p_detalles IS NULL OR JSON_TYPE(p_detalles)<>'ARRAY' OR JSON_LENGTH(p_detalles)=0
       OR JSON_LENGTH(p_detalles)>50 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El traslado debe incluir productos válidos';
    END IF;
    IF JSON_LENGTH(p_detalles)<>(SELECT COUNT(DISTINCT id_producto) FROM JSON_TABLE(p_detalles,'$[*]' COLUMNS(id_producto INT PATH '$.id_producto')) j)
       OR EXISTS (SELECT 1 FROM JSON_TABLE(p_detalles,'$[*]' COLUMNS(id_producto INT PATH '$.id_producto',cantidad INT PATH '$.cantidad')) j WHERE id_producto IS NULL OR cantidad IS NULL OR cantidad<=0)
       OR EXISTS (SELECT 1 FROM JSON_TABLE(p_detalles,'$[*]' COLUMNS(id_producto INT PATH '$.id_producto')) j LEFT JOIN PRODUCTO p ON p.id_producto=j.id_producto AND p.estado=1 WHERE p.id_producto IS NULL) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Las líneas del traslado no son válidas';
    END IF;
    IF (SELECT COUNT(*) FROM JSON_TABLE(p_detalles,'$[*]' COLUMNS(id_producto INT PATH '$.id_producto',cantidad INT PATH '$.cantidad')) j
        LEFT JOIN INVENTARIO_SUCURSAL i ON i.id_sucursal=p_id_sucursal_origen AND i.id_producto=j.id_producto
        WHERE COALESCE(i.stock_actual,0)<j.cantidad) > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Existencias insuficientes en la sucursal de origen';
    END IF;
    INSERT INTO TRASLADO(numero_traslado,estado,id_sucursal_origen,id_sucursal_destino,id_empleado)
    VALUES(p_numero_traslado,'Pendiente de aprobación',p_id_sucursal_origen,p_id_sucursal_destino,p_id_empleado);
    SET v_id_traslado=LAST_INSERT_ID();
    INSERT INTO DETALLE_TRASLADO(id_traslado,id_producto,cantidad)
    SELECT v_id_traslado,id_producto,cantidad FROM JSON_TABLE(p_detalles,'$[*]' COLUMNS(id_producto INT PATH '$.id_producto',cantidad INT PATH '$.cantidad')) j;
    COMMIT;
END$$

CREATE PROCEDURE sp_resolver_traslado(IN p_id_traslado INT, IN p_id_empleado INT, IN p_aprobar TINYINT, IN p_observacion VARCHAR(500))
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
    START TRANSACTION;
    IF NOT EXISTS (SELECT 1 FROM EMPLEADO WHERE id_empleado=p_id_empleado AND estado=1 AND cargo='Administrador') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Solo un administrador puede resolver la solicitud';
    END IF;
    UPDATE TRASLADO SET estado=IF(p_aprobar=1,'Aprobado','Rechazado'),
        id_empleado_aprobacion=p_id_empleado, fecha_aprobacion=CURRENT_TIMESTAMP,
        observacion_resolucion=NULLIF(TRIM(p_observacion),'')
    WHERE id_traslado=p_id_traslado AND estado='Pendiente de aprobación';
    IF ROW_COUNT()<>1 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='La solicitud ya fue resuelta o no existe'; END IF;
    IF p_aprobar=1 AND EXISTS (
        SELECT 1 FROM DETALLE_TRASLADO d LEFT JOIN INVENTARIO_SUCURSAL i
          ON i.id_sucursal=(SELECT id_sucursal_origen FROM TRASLADO WHERE id_traslado=p_id_traslado) AND i.id_producto=d.id_producto
        WHERE d.id_traslado=p_id_traslado AND COALESCE(i.stock_actual,0)<d.cantidad
    ) THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='No hay existencias suficientes para aprobar'; END IF;
    COMMIT;
END$$

CREATE PROCEDURE sp_despachar_traslado(IN p_id_traslado INT, IN p_id_empleado INT)
BEGIN
    DECLARE v_origen INT;
    DECLARE v_estado VARCHAR(30);
    DECLARE v_filas INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
    START TRANSACTION;
    SELECT id_sucursal_origen,estado INTO v_origen,v_estado FROM TRASLADO WHERE id_traslado=p_id_traslado FOR UPDATE;
    IF v_estado IS NULL OR v_estado<>'Aprobado' THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='El traslado no está aprobado'; END IF;
    IF NOT EXISTS (SELECT 1 FROM EMPLEADO WHERE id_empleado=p_id_empleado AND estado=1
       AND (cargo='Administrador' OR (cargo='Bodega' AND id_sucursal=v_origen))) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Solo bodega de origen puede despachar';
    END IF;
    UPDATE INVENTARIO_SUCURSAL i JOIN DETALLE_TRASLADO d ON d.id_producto=i.id_producto AND d.id_traslado=p_id_traslado
       SET i.stock_actual=i.stock_actual-d.cantidad WHERE i.id_sucursal=v_origen AND i.stock_actual>=d.cantidad;
    SET v_filas=ROW_COUNT();
    IF v_filas<>(SELECT COUNT(*) FROM DETALLE_TRASLADO WHERE id_traslado=p_id_traslado) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Existencias insuficientes; no se despachó el traslado';
    END IF;
    UPDATE TRASLADO SET estado='En tránsito',id_empleado_despacho=p_id_empleado,fecha_despacho=CURRENT_TIMESTAMP WHERE id_traslado=p_id_traslado;
    COMMIT;
END$$

CREATE PROCEDURE sp_recibir_traslado(IN p_id_traslado INT, IN p_id_empleado INT, IN p_detalles JSON, IN p_observacion VARCHAR(500))
BEGIN
    DECLARE v_destino INT;
    DECLARE v_estado VARCHAR(30);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
    START TRANSACTION;
    SELECT id_sucursal_destino,estado INTO v_destino,v_estado FROM TRASLADO WHERE id_traslado=p_id_traslado FOR UPDATE;
    IF v_estado IS NULL OR v_estado<>'En tránsito' THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='El traslado no está en tránsito'; END IF;
    IF NOT EXISTS (SELECT 1 FROM EMPLEADO WHERE id_empleado=p_id_empleado AND estado=1
       AND (cargo='Administrador' OR (cargo='Bodega' AND id_sucursal=v_destino))) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Solo bodega de destino puede confirmar la recepción';
    END IF;
    IF p_detalles IS NULL OR JSON_TYPE(p_detalles)<>'ARRAY'
       OR JSON_LENGTH(p_detalles)<>(SELECT COUNT(*) FROM DETALLE_TRASLADO WHERE id_traslado=p_id_traslado)
       OR JSON_LENGTH(p_detalles)<>(SELECT COUNT(DISTINCT id_producto) FROM JSON_TABLE(p_detalles,'$[*]' COLUMNS(id_producto INT PATH '$.id_producto')) j)
       OR EXISTS (SELECT 1 FROM JSON_TABLE(p_detalles,'$[*]' COLUMNS(id_producto INT PATH '$.id_producto',cantidad INT PATH '$.cantidad')) j
         LEFT JOIN DETALLE_TRASLADO d ON d.id_traslado=p_id_traslado AND d.id_producto=j.id_producto
         WHERE d.id_producto IS NULL OR j.cantidad IS NULL OR j.cantidad<0 OR j.cantidad>d.cantidad) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Indica una cantidad recibida válida para cada producto';
    END IF;
    IF EXISTS (SELECT 1 FROM JSON_TABLE(p_detalles,'$[*]' COLUMNS(id_producto INT PATH '$.id_producto',cantidad INT PATH '$.cantidad')) j
        JOIN DETALLE_TRASLADO d ON d.id_traslado=p_id_traslado AND d.id_producto=j.id_producto
        WHERE j.cantidad<d.cantidad) AND (p_observacion IS NULL OR CHAR_LENGTH(TRIM(p_observacion))=0) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Describe la diferencia de cantidades en la observación';
    END IF;
    UPDATE DETALLE_TRASLADO d JOIN JSON_TABLE(p_detalles,'$[*]' COLUMNS(id_producto INT PATH '$.id_producto',cantidad INT PATH '$.cantidad')) j
      ON j.id_producto=d.id_producto SET d.cantidad_recibida=j.cantidad WHERE d.id_traslado=p_id_traslado;
    INSERT INTO INVENTARIO_SUCURSAL(id_sucursal,id_producto,stock_actual)
    SELECT v_destino,id_producto,cantidad FROM JSON_TABLE(p_detalles,'$[*]' COLUMNS(id_producto INT PATH '$.id_producto',cantidad INT PATH '$.cantidad')) j WHERE cantidad>0
    ON DUPLICATE KEY UPDATE stock_actual=INVENTARIO_SUCURSAL.stock_actual+VALUES(stock_actual);
    UPDATE TRASLADO SET estado='Completado',id_empleado_recepcion=p_id_empleado,fecha_recepcion=CURRENT_TIMESTAMP,
      observacion_recepcion=NULLIF(TRIM(p_observacion),'') WHERE id_traslado=p_id_traslado;
    COMMIT;
END$$

DELIMITER ;
