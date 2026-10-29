-- Archivo: sql/migrations/10_document_corrections.sql
-- Autor: Equipo Comercial Estuardo
-- Descripción: permite correcciones auditadas de cabecera sin alterar importes ni stock.
-- Dependencias: esquema vigente después de la migración 09; aplicar una sola vez.
USE comercial_estuardo_db;
CREATE TABLE CORRECCION_DOCUMENTO (
 id_correccion BIGINT AUTO_INCREMENT PRIMARY KEY,
 id_venta INT NULL,
 id_compra INT NULL,
 id_empleado INT NOT NULL,
 fecha DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
 motivo VARCHAR(500) NOT NULL,
 datos_anteriores JSON NOT NULL,
 datos_nuevos JSON NOT NULL,
 FOREIGN KEY(id_venta) REFERENCES VENTA(id_venta) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY(id_compra) REFERENCES COMPRA(id_compra) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY(id_empleado) REFERENCES EMPLEADO(id_empleado) ON UPDATE RESTRICT ON DELETE RESTRICT,
 CHECK ((id_venta IS NOT NULL AND id_compra IS NULL) OR (id_venta IS NULL AND id_compra IS NOT NULL))
) ENGINE=InnoDB;
