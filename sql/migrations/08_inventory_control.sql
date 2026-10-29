-- Archivo: sql/migrations/08_inventory_control.sql
-- Autor: Equipo Comercial Estuardo
-- Descripción: actualiza de forma incremental el esquema existente.
-- Dependencias: Esquema y objetos previos según INSTALL.md; no ejecutar sobre producción sin respaldo.
-- Aplicar una vez después de la migración 07. No elimina documentos.
USE comercial_estuardo_db;

ALTER TABLE PRODUCTO ADD COLUMN requiere_serie TINYINT NOT NULL DEFAULT 0,
 ADD CONSTRAINT chk_producto_serie CHECK (requiere_serie IN (0,1));
UPDATE PRODUCTO p JOIN CATEGORIA c ON c.id_categoria=p.id_categoria
SET p.requiere_serie=1 WHERE LOWER(c.nombre) REGEXP '(^|[^[:alpha:]])(motos?|motocicletas?)([^[:alpha:]]|$)';
UPDATE PRODUCTO p JOIN DETALLE_VENTA d ON d.id_producto=p.id_producto
SET p.requiere_serie=1 WHERE d.vin_chasis IS NOT NULL AND d.numero_motor IS NOT NULL;

ALTER TABLE INVENTARIO_SUCURSAL
 ADD COLUMN stock_reservado INT NOT NULL DEFAULT 0,
 ADD COLUMN stock_minimo INT NULL,
 ADD COLUMN revision BIGINT NOT NULL DEFAULT 0,
 ADD CONSTRAINT chk_reservas CHECK (stock_reservado>=0 AND stock_reservado<=stock_actual),
 ADD CONSTRAINT chk_minimo_sucursal CHECK (stock_minimo IS NULL OR stock_minimo>=0);

CREATE TABLE UNIDAD_PRODUCTO (
 id_unidad INT AUTO_INCREMENT PRIMARY KEY,
 id_producto INT NOT NULL,
 vin_chasis VARCHAR(50) NOT NULL UNIQUE,
 numero_motor VARCHAR(50) NOT NULL UNIQUE,
 id_sucursal INT NOT NULL,
 estado VARCHAR(30) NOT NULL DEFAULT 'Disponible',
 id_detalle_compra INT NULL,
 id_detalle_venta INT NULL,
 id_traslado INT NULL,
 fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (id_producto) REFERENCES PRODUCTO(id_producto) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY (id_sucursal) REFERENCES SUCURSAL(id_sucursal) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY (id_detalle_compra) REFERENCES DETALLE_COMPRA(id_detalle_compra) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY (id_detalle_venta) REFERENCES DETALLE_VENTA(id_detalle_venta) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY (id_traslado) REFERENCES TRASLADO(id_traslado) ON UPDATE RESTRICT ON DELETE RESTRICT,
 CONSTRAINT chk_unidad_estado CHECK (estado IN ('Disponible','Reservada','En tránsito','Vendida','Baja','Devuelta a proveedor')),
 INDEX idx_unidad_sucursal (id_sucursal,id_producto,estado)
) ENGINE=InnoDB;

INSERT INTO UNIDAD_PRODUCTO(id_producto,vin_chasis,numero_motor,id_sucursal,estado,id_detalle_venta)
SELECT d.id_producto,d.vin_chasis,d.numero_motor,v.id_sucursal,'Vendida',d.id_detalle_venta
FROM DETALLE_VENTA d JOIN VENTA v ON v.id_venta=d.id_venta
WHERE d.vin_chasis IS NOT NULL AND d.numero_motor IS NOT NULL AND v.estado='Emitida';

ALTER TABLE DETALLE_VENTA
 DROP INDEX vin_chasis, DROP INDEX numero_motor,
 ADD COLUMN id_unidad INT NULL,
 ADD FOREIGN KEY (id_unidad) REFERENCES UNIDAD_PRODUCTO(id_unidad) ON UPDATE RESTRICT ON DELETE RESTRICT,
 ADD INDEX idx_venta_vin (vin_chasis), ADD INDEX idx_venta_motor (numero_motor);
UPDATE DETALLE_VENTA d JOIN UNIDAD_PRODUCTO u ON u.id_detalle_venta=d.id_detalle_venta SET d.id_unidad=u.id_unidad;

CREATE TABLE TRASLADO_UNIDAD (
 id_traslado INT NOT NULL,
 id_unidad INT NOT NULL,
 recibida TINYINT NOT NULL DEFAULT 0,
 PRIMARY KEY(id_traslado,id_unidad),
 FOREIGN KEY (id_traslado) REFERENCES TRASLADO(id_traslado) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY (id_unidad) REFERENCES UNIDAD_PRODUCTO(id_unidad) ON UPDATE RESTRICT ON DELETE RESTRICT,
 CHECK (recibida IN (0,1))
) ENGINE=InnoDB;
ALTER TABLE TRASLADO DROP CHECK chk_traslado_estado,
 ADD CONSTRAINT chk_traslado_estado CHECK (estado IN ('Pendiente de aprobación','Rechazado','Aprobado','En tránsito','Con diferencias','Completado','Anulado'));

CREATE TABLE EVENTO_TRASLADO (
 id_evento BIGINT AUTO_INCREMENT PRIMARY KEY,
 id_traslado INT NOT NULL,
 accion VARCHAR(50) NOT NULL,
 id_empleado INT NOT NULL,
 observacion VARCHAR(500) NULL,
 fecha DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
 FOREIGN KEY (id_traslado) REFERENCES TRASLADO(id_traslado) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY (id_empleado) REFERENCES EMPLEADO(id_empleado) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE MOVIMIENTO_INVENTARIO (
 id_movimiento BIGINT AUTO_INCREMENT PRIMARY KEY,
 fecha DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
 id_sucursal INT NOT NULL,
 id_producto INT NOT NULL,
 tipo VARCHAR(50) NOT NULL,
 referencia VARCHAR(100) NULL,
 id_empleado INT NULL,
 cantidad INT NOT NULL,
 saldo_anterior INT NOT NULL,
 saldo_posterior INT NOT NULL,
 reservado_anterior INT NOT NULL,
 reservado_posterior INT NOT NULL,
 motivo VARCHAR(500) NULL,
 FOREIGN KEY(id_sucursal) REFERENCES SUCURSAL(id_sucursal) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY(id_producto) REFERENCES PRODUCTO(id_producto) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY(id_empleado) REFERENCES EMPLEADO(id_empleado) ON UPDATE RESTRICT ON DELETE RESTRICT,
 INDEX idx_movimiento_consulta(id_sucursal,id_producto,fecha)
) ENGINE=InnoDB;
INSERT INTO MOVIMIENTO_INVENTARIO(id_sucursal,id_producto,tipo,cantidad,saldo_anterior,saldo_posterior,reservado_anterior,reservado_posterior,motivo)
SELECT id_sucursal,id_producto,'Saldo inicial',stock_actual,0,stock_actual,0,0,'Existencias al activar el Kardex; no reconstruye movimientos previos' FROM INVENTARIO_SUCURSAL;

CREATE TABLE HISTORIAL_UNIDAD (
 id_historial BIGINT AUTO_INCREMENT PRIMARY KEY,
 id_unidad INT NOT NULL,
 fecha DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
 id_sucursal_origen INT NULL,
 id_sucursal_destino INT NOT NULL,
 estado_anterior VARCHAR(30) NULL,
 estado_nuevo VARCHAR(30) NOT NULL,
 id_empleado INT NULL,
 referencia VARCHAR(100) NULL,
 motivo VARCHAR(500) NULL,
 FOREIGN KEY(id_unidad) REFERENCES UNIDAD_PRODUCTO(id_unidad) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY(id_empleado) REFERENCES EMPLEADO(id_empleado) ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB;
INSERT INTO HISTORIAL_UNIDAD(id_unidad,id_sucursal_destino,estado_nuevo,referencia)
SELECT id_unidad,id_sucursal,estado,'Identificación histórica de venta' FROM UNIDAD_PRODUCTO;

CREATE TABLE CONTEO_INVENTARIO (
 id_conteo INT AUTO_INCREMENT PRIMARY KEY,
 id_sucursal INT NOT NULL,
 id_producto INT NOT NULL,
 stock_sistema INT NOT NULL,
 reservado_sistema INT NOT NULL,
 revision_sistema BIGINT NOT NULL,
 cantidad_contada INT NOT NULL,
 unidades_snapshot JSON NULL,
 unidades_presentes JSON NULL,
 unidades_nuevas JSON NULL,
 motivo VARCHAR(500) NOT NULL,
 estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
 id_solicitante INT NOT NULL,
 id_responsable INT NULL,
 fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 fecha_resolucion DATETIME NULL,
 observacion VARCHAR(500) NULL,
 FOREIGN KEY(id_sucursal) REFERENCES SUCURSAL(id_sucursal) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY(id_producto) REFERENCES PRODUCTO(id_producto) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY(id_solicitante) REFERENCES EMPLEADO(id_empleado) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY(id_responsable) REFERENCES EMPLEADO(id_empleado) ON UPDATE RESTRICT ON DELETE RESTRICT,
 CHECK(cantidad_contada>=0),
 CHECK(estado IN ('Pendiente','Aprobado','Rechazado'))
) ENGINE=InnoDB;

CREATE TABLE REVERSO_DOCUMENTO (
 id_reverso INT AUTO_INCREMENT PRIMARY KEY,
 tipo VARCHAR(30) NOT NULL,
 id_venta INT NULL,
 id_compra INT NULL,
 id_empleado INT NOT NULL,
 fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 motivo VARCHAR(500) NOT NULL,
 importe DECIMAL(12,2) NOT NULL DEFAULT 0,
 FOREIGN KEY(id_venta) REFERENCES VENTA(id_venta) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY(id_compra) REFERENCES COMPRA(id_compra) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY(id_empleado) REFERENCES EMPLEADO(id_empleado) ON UPDATE RESTRICT ON DELETE RESTRICT,
 CHECK(tipo IN ('Devolución venta','Anulación venta','Devolución compra','Anulación compra')),
 CHECK((id_venta IS NOT NULL AND id_compra IS NULL) OR (id_compra IS NOT NULL AND id_venta IS NULL))
) ENGINE=InnoDB;
CREATE TABLE DETALLE_REVERSO (
 id_detalle_reverso INT AUTO_INCREMENT PRIMARY KEY,
 id_reverso INT NOT NULL,
 id_producto INT NOT NULL,
 id_detalle_venta INT NULL,
 id_detalle_compra INT NULL,
 cantidad INT NOT NULL,
 importe DECIMAL(12,2) NOT NULL,
 FOREIGN KEY(id_reverso) REFERENCES REVERSO_DOCUMENTO(id_reverso) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY(id_producto) REFERENCES PRODUCTO(id_producto) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY(id_detalle_venta) REFERENCES DETALLE_VENTA(id_detalle_venta) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY(id_detalle_compra) REFERENCES DETALLE_COMPRA(id_detalle_compra) ON UPDATE RESTRICT ON DELETE RESTRICT,
 CHECK(cantidad>0)
) ENGINE=InnoDB;

CREATE TABLE RESPALDO_EJECUCION (
 id_respaldo BIGINT AUTO_INCREMENT PRIMARY KEY,
 inicio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 fin DATETIME NULL,
 estado VARCHAR(20) NOT NULL DEFAULT 'En proceso',
 restauracion_verificada TINYINT NOT NULL DEFAULT 0,
 archivo VARCHAR(200) NULL,
 sha256 VARCHAR(64) NULL,
 enlace VARCHAR(300) NULL,
 detalle VARCHAR(500) NULL
) ENGINE=InnoDB;

-- Las reservas aprobadas previas se materializan solo al instalar el nuevo flujo.
-- Revisar que no haya más cantidad aprobada que stock disponible antes de ejecutar.
UPDATE INVENTARIO_SUCURSAL i JOIN (
 SELECT t.id_sucursal_origen,d.id_producto,SUM(d.cantidad) cantidad
 FROM TRASLADO t JOIN DETALLE_TRASLADO d ON d.id_traslado=t.id_traslado
 WHERE t.estado='Aprobado' GROUP BY t.id_sucursal_origen,d.id_producto
) r ON r.id_sucursal_origen=i.id_sucursal AND r.id_producto=i.id_producto
SET i.stock_reservado=r.cantidad;

UPDATE MOVIMIENTO_INVENTARIO m JOIN INVENTARIO_SUCURSAL i USING(id_sucursal,id_producto)
SET m.reservado_posterior=i.stock_reservado WHERE m.tipo='Saldo inicial';
