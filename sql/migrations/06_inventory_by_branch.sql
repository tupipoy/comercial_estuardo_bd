-- Archivo: sql/migrations/06_inventory_by_branch.sql
-- Autor: Equipo Comercial Estuardo
-- Descripción: convierte existencias globales a inventario por sucursal y crea traslados.
-- Dependencias: esquema Entrega 4 anterior y tablas EMPLEADO, PRODUCTO, SUCURSAL, COMPRA.
-- IMPORTANTE: respalda la base antes de ejecutar; aplicar una sola vez.
-- El stock existente se asigna a Sucursal Central y luego puede redistribuirse con traslados.
USE comercial_estuardo_db;

-- Validar antes de hacer cambios. Si no existe Sucursal Central, la migración se detiene aquí.
DROP PROCEDURE IF EXISTS validar_sucursal_migracion_inventario;
DELIMITER $$
CREATE PROCEDURE validar_sucursal_migracion_inventario(IN p_id_sucursal INT)
BEGIN
    IF p_id_sucursal IS NULL OR NOT EXISTS (
        SELECT 1 FROM SUCURSAL WHERE id_sucursal = p_id_sucursal AND nombre = 'Sucursal Central' AND estado = 1
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Debe existir una Sucursal Central activa para migrar el stock';
    END IF;
END$$
DELIMITER ;
SET @id_sucursal_inventario_inicial = (
    SELECT id_sucursal FROM SUCURSAL WHERE nombre = 'Sucursal Central' AND estado = 1 LIMIT 1
);
CALL validar_sucursal_migracion_inventario(@id_sucursal_inventario_inicial);
DROP PROCEDURE validar_sucursal_migracion_inventario;

CREATE TABLE INVENTARIO_SUCURSAL (
    id_sucursal INT NOT NULL,
    id_producto INT NOT NULL,
    stock_actual INT NOT NULL DEFAULT 0,
    actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id_sucursal, id_producto),
    CONSTRAINT fk_inventario_sucursal FOREIGN KEY (id_sucursal)
        REFERENCES SUCURSAL(id_sucursal) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_inventario_producto FOREIGN KEY (id_producto)
        REFERENCES PRODUCTO(id_producto) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_inventario_stock CHECK (stock_actual >= 0)
) ENGINE=InnoDB;

CREATE TABLE TRASLADO (
    id_traslado INT AUTO_INCREMENT PRIMARY KEY,
    numero_traslado VARCHAR(30) NOT NULL UNIQUE,
    fecha_traslado DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) NOT NULL DEFAULT 'Completado',
    id_sucursal_origen INT NOT NULL,
    id_sucursal_destino INT NOT NULL,
    id_empleado INT NOT NULL,
    CONSTRAINT fk_traslado_origen FOREIGN KEY (id_sucursal_origen)
        REFERENCES SUCURSAL(id_sucursal) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_traslado_destino FOREIGN KEY (id_sucursal_destino)
        REFERENCES SUCURSAL(id_sucursal) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_traslado_empleado FOREIGN KEY (id_empleado)
        REFERENCES EMPLEADO(id_empleado) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_traslado_sucursales CHECK (id_sucursal_origen <> id_sucursal_destino),
    CONSTRAINT chk_traslado_estado CHECK (estado IN ('Completado', 'Anulado'))
) ENGINE=InnoDB;

CREATE TABLE DETALLE_TRASLADO (
    id_detalle_traslado INT AUTO_INCREMENT PRIMARY KEY,
    id_traslado INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    CONSTRAINT fk_dettraslado_traslado FOREIGN KEY (id_traslado)
        REFERENCES TRASLADO(id_traslado) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_dettraslado_producto FOREIGN KEY (id_producto)
        REFERENCES PRODUCTO(id_producto) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT uq_dettraslado_producto UNIQUE (id_traslado, id_producto),
    CONSTRAINT chk_dettraslado_cantidad CHECK (cantidad > 0)
) ENGINE=InnoDB;

ALTER TABLE COMPRA
    ADD COLUMN id_sucursal INT NULL AFTER id_empleado;
UPDATE COMPRA AS c
INNER JOIN EMPLEADO AS e ON e.id_empleado = c.id_empleado
SET c.id_sucursal = e.id_sucursal;
ALTER TABLE COMPRA
    MODIFY id_sucursal INT NOT NULL,
    ADD CONSTRAINT fk_compra_sucursal FOREIGN KEY (id_sucursal)
        REFERENCES SUCURSAL(id_sucursal) ON UPDATE CASCADE ON DELETE RESTRICT;

INSERT INTO INVENTARIO_SUCURSAL (id_sucursal, id_producto, stock_actual)
SELECT @id_sucursal_inventario_inicial, id_producto, stock_actual FROM PRODUCTO;
ALTER TABLE PRODUCTO DROP CHECK chk_producto_stock_actual;
ALTER TABLE PRODUCTO DROP COLUMN stock_actual;
