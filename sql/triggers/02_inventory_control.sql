-- Archivo: sql/triggers/02_inventory_control.sql
-- Autor: Equipo Comercial Estuardo
-- Descripción: aplica reglas automáticas y trazabilidad.
-- Dependencias: Esquema y objetos previos según INSTALL.md; no ejecutar sobre producción sin respaldo.
USE comercial_estuardo_db;
DROP TRIGGER IF EXISTS trg_validar_stock_venta;
DROP TRIGGER IF EXISTS trg_venta_unidad;
DROP TRIGGER IF EXISTS trg_inventario_revision;
DROP TRIGGER IF EXISTS trg_kardex_insert;
DROP TRIGGER IF EXISTS trg_kardex_update;
DROP TRIGGER IF EXISTS trg_unidad_alta;
DROP TRIGGER IF EXISTS trg_unidad_historial;
DROP TRIGGER IF EXISTS trg_venta_conservar;
DROP TRIGGER IF EXISTS trg_compra_conservar;
DROP TRIGGER IF EXISTS trg_producto_identificacion_insert;
DROP TRIGGER IF EXISTS trg_producto_identificacion_update;
DELIMITER $$
CREATE TRIGGER trg_producto_identificacion_insert BEFORE INSERT ON PRODUCTO FOR EACH ROW
BEGIN
 IF EXISTS(SELECT 1 FROM CATEGORIA WHERE id_categoria=NEW.id_categoria AND LOWER(nombre) REGEXP '(^|[^[:alpha:]])(motos?|motocicletas?)([^[:alpha:]]|$)') THEN SET NEW.requiere_serie=1; END IF;
END$$
CREATE TRIGGER trg_producto_identificacion_update BEFORE UPDATE ON PRODUCTO FOR EACH ROW
BEGIN
 IF EXISTS(SELECT 1 FROM CATEGORIA WHERE id_categoria=NEW.id_categoria AND LOWER(nombre) REGEXP '(^|[^[:alpha:]])(motos?|motocicletas?)([^[:alpha:]]|$)') THEN SET NEW.requiere_serie=1; END IF;
 IF NEW.requiere_serie=0 AND OLD.requiere_serie=1 AND EXISTS(SELECT 1 FROM UNIDAD_PRODUCTO WHERE id_producto=OLD.id_producto) THEN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='El producto ya tiene unidades identificadas; conserva su seguimiento';
 END IF;
END$$
CREATE TRIGGER trg_validar_stock_venta BEFORE INSERT ON DETALLE_VENTA FOR EACH ROW
BEGIN
 DECLARE v_stock INT DEFAULT NULL;
 DECLARE v_serie TINYINT DEFAULT 0;
 DECLARE v_sucursal INT;
 DECLARE v_unidad INT DEFAULT NULL;
 DECLARE v_actor INT;
 DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_unidad=NULL;
 SELECT id_sucursal,id_empleado INTO v_sucursal,v_actor FROM VENTA WHERE id_venta=NEW.id_venta;
 SELECT stock_actual-stock_reservado INTO v_stock FROM INVENTARIO_SUCURSAL
 WHERE id_sucursal=v_sucursal AND id_producto=NEW.id_producto FOR UPDATE;
 IF v_stock IS NULL OR v_stock<NEW.cantidad THEN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Stock insuficiente disponible: hay unidades reservadas o agotadas';
 END IF;
 SELECT requiere_serie INTO v_serie FROM PRODUCTO WHERE id_producto=NEW.id_producto;
 IF v_serie=1 THEN
  SELECT id_unidad INTO v_unidad FROM UNIDAD_PRODUCTO
  WHERE id_producto=NEW.id_producto AND id_sucursal=v_sucursal AND estado='Disponible'
    AND vin_chasis=NEW.vin_chasis AND numero_motor=NEW.numero_motor FOR UPDATE;
  IF v_unidad IS NULL OR NEW.cantidad<>1 THEN
   SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Selecciona una motocicleta disponible de esta sucursal';
  END IF;
  SET NEW.id_unidad=v_unidad;
 ELSEIF NEW.vin_chasis IS NOT NULL OR NEW.numero_motor IS NOT NULL THEN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='El producto no utiliza identificación por VIN y motor';
 END IF;
 SET @mov_tipo='Venta',@mov_referencia=CONCAT('Venta #',NEW.id_venta),@mov_actor=v_actor,@mov_motivo=NULL;
END$$
CREATE TRIGGER trg_venta_unidad AFTER INSERT ON DETALLE_VENTA FOR EACH ROW
BEGIN
 IF NEW.id_unidad IS NOT NULL THEN
  UPDATE UNIDAD_PRODUCTO SET estado='Vendida',id_detalle_venta=NEW.id_detalle_venta WHERE id_unidad=NEW.id_unidad;
 END IF;
END$$
CREATE TRIGGER trg_inventario_revision BEFORE UPDATE ON INVENTARIO_SUCURSAL FOR EACH ROW
BEGIN
 IF NEW.stock_actual<>OLD.stock_actual OR NEW.stock_reservado<>OLD.stock_reservado THEN SET NEW.revision=OLD.revision+1; END IF;
END$$
CREATE TRIGGER trg_kardex_insert AFTER INSERT ON INVENTARIO_SUCURSAL FOR EACH ROW
BEGIN
 IF NEW.stock_actual<>0 OR NEW.stock_reservado<>0 THEN
 INSERT INTO MOVIMIENTO_INVENTARIO(id_sucursal,id_producto,tipo,referencia,id_empleado,cantidad,saldo_anterior,saldo_posterior,reservado_anterior,reservado_posterior,motivo)
 VALUES(NEW.id_sucursal,NEW.id_producto,COALESCE(@mov_tipo,'Alta de inventario'),@mov_referencia,@mov_actor,NEW.stock_actual,0,NEW.stock_actual,0,NEW.stock_reservado,@mov_motivo);
 END IF;
END$$
CREATE TRIGGER trg_kardex_update AFTER UPDATE ON INVENTARIO_SUCURSAL FOR EACH ROW
BEGIN
 IF NEW.stock_actual<>OLD.stock_actual OR NEW.stock_reservado<>OLD.stock_reservado THEN
 INSERT INTO MOVIMIENTO_INVENTARIO(id_sucursal,id_producto,tipo,referencia,id_empleado,cantidad,saldo_anterior,saldo_posterior,reservado_anterior,reservado_posterior,motivo)
 VALUES(NEW.id_sucursal,NEW.id_producto,COALESCE(@mov_tipo,'Cambio de inventario'),@mov_referencia,@mov_actor,NEW.stock_actual-OLD.stock_actual,OLD.stock_actual,NEW.stock_actual,OLD.stock_reservado,NEW.stock_reservado,@mov_motivo);
 END IF;
END$$
CREATE TRIGGER trg_unidad_alta AFTER INSERT ON UNIDAD_PRODUCTO FOR EACH ROW
BEGIN
 INSERT INTO HISTORIAL_UNIDAD(id_unidad,id_sucursal_destino,estado_nuevo,id_empleado,referencia,motivo)
 VALUES(NEW.id_unidad,NEW.id_sucursal,NEW.estado,@mov_actor,@mov_referencia,@mov_motivo);
END$$
CREATE TRIGGER trg_unidad_historial AFTER UPDATE ON UNIDAD_PRODUCTO FOR EACH ROW
BEGIN
 IF NEW.estado<>OLD.estado OR NEW.id_sucursal<>OLD.id_sucursal THEN
 INSERT INTO HISTORIAL_UNIDAD(id_unidad,id_sucursal_origen,id_sucursal_destino,estado_anterior,estado_nuevo,id_empleado,referencia,motivo)
 VALUES(NEW.id_unidad,OLD.id_sucursal,NEW.id_sucursal,OLD.estado,NEW.estado,@mov_actor,@mov_referencia,@mov_motivo);
 END IF;
END$$
CREATE TRIGGER trg_venta_conservar BEFORE DELETE ON VENTA FOR EACH ROW
BEGIN
 SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Conserva el documento: registra una anulación con motivo';
END$$
CREATE TRIGGER trg_compra_conservar BEFORE DELETE ON COMPRA FOR EACH ROW
BEGIN
 SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Conserva el documento: registra una anulación con motivo';
END$$
DELIMITER ;
