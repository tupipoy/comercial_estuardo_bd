-- Archivo: sql/migrations/09_supplier_proposals.sql
-- Autor: Equipo Comercial Estuardo
-- Descripción: actualiza de forma incremental el esquema existente.
-- Dependencias: Esquema y objetos previos según INSTALL.md; no ejecutar sobre producción sin respaldo.
-- Proveedores existentes conservan su aprobación y su historial.
-- Las altas nuevas se proponen y se aprueban antes de entrar al catálogo.
USE comercial_estuardo_db;

CREATE TABLE PROPUESTA_PROVEEDOR (
 id_propuesta INT AUTO_INCREMENT PRIMARY KEY,
 nit VARCHAR(15) NOT NULL,
 razon_social VARCHAR(150) NOT NULL,
 contacto VARCHAR(100) NULL,
 telefono VARCHAR(15) NOT NULL,
 correo VARCHAR(100) NULL,
 direccion VARCHAR(200) NULL,
 estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
 id_solicitante INT NOT NULL,
 fecha_solicitud DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
 id_responsable INT NULL,
 fecha_resolucion DATETIME(6) NULL,
 observacion VARCHAR(500) NULL,
 id_proveedor INT NULL UNIQUE,
 nit_pendiente VARCHAR(15) GENERATED ALWAYS AS (CASE WHEN estado='Pendiente' THEN nit ELSE NULL END) STORED,
 UNIQUE KEY uq_propuesta_nit_pendiente (nit_pendiente),
 FOREIGN KEY (id_solicitante) REFERENCES EMPLEADO(id_empleado) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY (id_responsable) REFERENCES EMPLEADO(id_empleado) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY (id_proveedor) REFERENCES PROVEEDOR(id_proveedor) ON UPDATE RESTRICT ON DELETE RESTRICT,
 CHECK (estado IN ('Pendiente','Aprobada','Rechazada')),
 CHECK ((estado='Pendiente' AND id_responsable IS NULL AND fecha_resolucion IS NULL AND id_proveedor IS NULL)
     OR (estado='Aprobada' AND id_responsable IS NOT NULL AND fecha_resolucion IS NOT NULL AND id_proveedor IS NOT NULL)
     OR (estado='Rechazada' AND id_responsable IS NOT NULL AND fecha_resolucion IS NOT NULL AND id_proveedor IS NULL)),
 INDEX idx_propuestas_solicitante (id_solicitante,estado)
) ENGINE=InnoDB;

CREATE TABLE EVENTO_PROVEEDOR (
 id_evento BIGINT AUTO_INCREMENT PRIMARY KEY,
 id_propuesta INT NULL,
 id_proveedor INT NULL,
 id_empleado INT NOT NULL,
 accion VARCHAR(30) NOT NULL,
 fecha DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
 observacion VARCHAR(500) NULL,
 datos_anteriores JSON NULL,
 datos_nuevos JSON NULL,
 FOREIGN KEY (id_propuesta) REFERENCES PROPUESTA_PROVEEDOR(id_propuesta) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY (id_proveedor) REFERENCES PROVEEDOR(id_proveedor) ON UPDATE RESTRICT ON DELETE RESTRICT,
 FOREIGN KEY (id_empleado) REFERENCES EMPLEADO(id_empleado) ON UPDATE RESTRICT ON DELETE RESTRICT,
 CHECK (id_propuesta IS NOT NULL OR id_proveedor IS NOT NULL)
) ENGINE=InnoDB;
