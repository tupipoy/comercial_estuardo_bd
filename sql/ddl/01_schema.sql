
-- Archivo: sql/ddl/01_schema.sql
-- Autor: Equipo Comercial Estuardo
-- Descripción: crea el esquema relacional, sus tablas y restricciones.
-- Dependencias: ninguna; elimina y recrea comercial_estuardo_db.
-- Revisión: no ejecutar sin autorización de ER y sin respaldar datos.

DROP DATABASE IF EXISTS comercial_estuardo_db;
CREATE DATABASE comercial_estuardo_db 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE comercial_estuardo_db;


CREATE TABLE SUCURSAL (
    id_sucursal INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    direccion VARCHAR(200) NOT NULL,
    telefono VARCHAR(15) NOT NULL,
    municipio VARCHAR(100) NOT NULL,
    estado TINYINT(1) NOT NULL DEFAULT 1,
    CONSTRAINT chk_sucursal_telefono CHECK (LENGTH(telefono) >= 8),
    CONSTRAINT chk_sucursal_estado CHECK (estado IN (0, 1))
) ENGINE=InnoDB;


CREATE TABLE EMPLEADO (
    id_empleado INT AUTO_INCREMENT PRIMARY KEY,
    cui VARCHAR(13) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    cargo VARCHAR(50) NOT NULL,
    telefono VARCHAR(15) NOT NULL,
    correo VARCHAR(100) NULL UNIQUE,
    password_hash VARCHAR(255) NULL,
    intentos_login_fallidos TINYINT UNSIGNED NOT NULL DEFAULT 0,
    bloqueado_hasta DATETIME NULL,
    fecha_ingreso DATE NOT NULL,
    id_sucursal INT NOT NULL,
    estado TINYINT(1) NOT NULL DEFAULT 1,
    CONSTRAINT fk_empleado_sucursal FOREIGN KEY (id_sucursal) 
        REFERENCES SUCURSAL(id_sucursal) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT chk_empleado_cui CHECK (LENGTH(cui) = 13),
    CONSTRAINT chk_empleado_estado CHECK (estado IN (0, 1))
) ENGINE=InnoDB;


CREATE TABLE CLIENTE (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nit VARCHAR(15) NOT NULL UNIQUE,
    cui VARCHAR(13) NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NULL,
    telefono VARCHAR(15) NOT NULL,
    correo VARCHAR(100) NULL,
    direccion VARCHAR(200) NOT NULL,
    estado TINYINT(1) NOT NULL DEFAULT 1,
    CONSTRAINT chk_cliente_cui CHECK (cui IS NULL OR LENGTH(cui) = 13),
    CONSTRAINT chk_cliente_estado CHECK (estado IN (0, 1))
) ENGINE=InnoDB;


CREATE TABLE CATEGORIA (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(255) NULL,
    estado TINYINT(1) NOT NULL DEFAULT 1,
    CONSTRAINT chk_categoria_estado CHECK (estado IN (0, 1))
) ENGINE=InnoDB;


CREATE TABLE PRODUCTO (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    codigo_barra VARCHAR(50) NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT NULL,
    precio_costo DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    precio_venta DECIMAL(10,2) NOT NULL,
    stock_minimo INT NOT NULL DEFAULT 1,
    id_categoria INT NOT NULL,
    estado TINYINT(1) NOT NULL DEFAULT 1,
    CONSTRAINT fk_producto_categoria FOREIGN KEY (id_categoria) 
        REFERENCES CATEGORIA(id_categoria) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT chk_producto_precio CHECK (precio_venta > 0),
    CONSTRAINT chk_producto_precio_costo CHECK (precio_costo >= 0),
    CONSTRAINT chk_producto_margen CHECK (precio_venta >= precio_costo),
    CONSTRAINT chk_producto_stock_minimo CHECK (stock_minimo >= 0),
    CONSTRAINT chk_producto_estado CHECK (estado IN (0, 1))
) ENGINE=InnoDB;

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
    estado VARCHAR(30) NOT NULL DEFAULT 'Pendiente de aprobación',
    id_sucursal_origen INT NOT NULL,
    id_sucursal_destino INT NOT NULL,
    id_empleado INT NOT NULL,
    id_empleado_aprobacion INT NULL,
    fecha_aprobacion DATETIME NULL,
    observacion_resolucion VARCHAR(500) NULL,
    id_empleado_despacho INT NULL,
    fecha_despacho DATETIME NULL,
    id_empleado_recepcion INT NULL,
    fecha_recepcion DATETIME NULL,
    observacion_recepcion VARCHAR(500) NULL,
    CONSTRAINT fk_traslado_origen FOREIGN KEY (id_sucursal_origen)
        REFERENCES SUCURSAL(id_sucursal) ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_traslado_destino FOREIGN KEY (id_sucursal_destino)
        REFERENCES SUCURSAL(id_sucursal) ON UPDATE RESTRICT ON DELETE RESTRICT,
    CONSTRAINT fk_traslado_empleado FOREIGN KEY (id_empleado)
        REFERENCES EMPLEADO(id_empleado) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_traslado_aprobador FOREIGN KEY (id_empleado_aprobacion)
        REFERENCES EMPLEADO(id_empleado) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_traslado_despachador FOREIGN KEY (id_empleado_despacho)
        REFERENCES EMPLEADO(id_empleado) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_traslado_receptor FOREIGN KEY (id_empleado_recepcion)
        REFERENCES EMPLEADO(id_empleado) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_traslado_sucursales CHECK (id_sucursal_origen <> id_sucursal_destino),
    CONSTRAINT chk_traslado_estado CHECK (estado IN ('Pendiente de aprobación', 'Rechazado', 'Aprobado', 'En tránsito', 'Completado', 'Anulado'))
) ENGINE=InnoDB;

CREATE TABLE DETALLE_TRASLADO (
    id_detalle_traslado INT AUTO_INCREMENT PRIMARY KEY,
    id_traslado INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    cantidad_recibida INT NULL,
    CONSTRAINT fk_dettraslado_traslado FOREIGN KEY (id_traslado)
        REFERENCES TRASLADO(id_traslado) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_dettraslado_producto FOREIGN KEY (id_producto)
        REFERENCES PRODUCTO(id_producto) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT uq_dettraslado_producto UNIQUE (id_traslado, id_producto),
    CONSTRAINT chk_dettraslado_cantidad CHECK (cantidad > 0),
    CONSTRAINT chk_dettraslado_recibida CHECK (cantidad_recibida IS NULL OR (cantidad_recibida >= 0 AND cantidad_recibida <= cantidad))
) ENGINE=InnoDB;


CREATE TABLE PROVEEDOR (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nit VARCHAR(15) NOT NULL UNIQUE,
    razon_social VARCHAR(150) NOT NULL,
    contacto VARCHAR(100) NULL,
    telefono VARCHAR(15) NOT NULL,
    correo VARCHAR(100) NULL,
    direccion VARCHAR(200) NULL,
    estado TINYINT(1) NOT NULL DEFAULT 1,
    CONSTRAINT chk_proveedor_estado CHECK (estado IN (0, 1))
) ENGINE=InnoDB;


CREATE TABLE COMPRA (
    id_compra INT AUTO_INCREMENT PRIMARY KEY,
    numero_orden VARCHAR(30) NOT NULL UNIQUE,
    fecha_compra DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_compra DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    estado_recepcion VARCHAR(20) NOT NULL,
    id_proveedor INT NOT NULL,
    id_empleado INT NOT NULL,
    id_sucursal INT NOT NULL,
    CONSTRAINT fk_compra_proveedor FOREIGN KEY (id_proveedor) 
        REFERENCES PROVEEDOR(id_proveedor) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT fk_compra_empleado FOREIGN KEY (id_empleado) 
        REFERENCES EMPLEADO(id_empleado) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT fk_compra_sucursal FOREIGN KEY (id_sucursal)
        REFERENCES SUCURSAL(id_sucursal)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT chk_compra_total CHECK (total_compra >= 0),
    CONSTRAINT chk_compra_estado CHECK (estado_recepcion IN ('Pendiente', 'Recibido', 'Cancelado'))
) ENGINE=InnoDB;


CREATE TABLE DETALLE_COMPRA (
    id_detalle_compra INT AUTO_INCREMENT PRIMARY KEY,
    id_compra INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    costo_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    CONSTRAINT fk_detcompra_compra FOREIGN KEY (id_compra) 
        REFERENCES COMPRA(id_compra) 
        ON UPDATE CASCADE 
        ON DELETE CASCADE,
    CONSTRAINT fk_detcompra_producto FOREIGN KEY (id_producto) 
        REFERENCES PRODUCTO(id_producto) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT chk_detcompra_cantidad CHECK (cantidad > 0),
    CONSTRAINT chk_detcompra_costo CHECK (costo_unitario > 0),
    CONSTRAINT chk_detcompra_subtotal CHECK (subtotal >= 0)
) ENGINE=InnoDB;


CREATE TABLE VENTA (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    serie_factura VARCHAR(10) NOT NULL,
    numero_factura INT NOT NULL,
    fecha_venta DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_venta DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    tipo_pago VARCHAR(30) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Emitida',
    id_cliente INT NOT NULL,
    id_empleado INT NOT NULL,
    id_sucursal INT NOT NULL,
    CONSTRAINT uq_venta_factura UNIQUE (serie_factura, numero_factura),
    CONSTRAINT fk_venta_cliente FOREIGN KEY (id_cliente) 
        REFERENCES CLIENTE(id_cliente) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT fk_venta_empleado FOREIGN KEY (id_empleado) 
        REFERENCES EMPLEADO(id_empleado) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT fk_venta_sucursal FOREIGN KEY (id_sucursal) 
        REFERENCES SUCURSAL(id_sucursal) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT chk_venta_total CHECK (total_venta >= 0),
    CONSTRAINT chk_venta_tipo_pago CHECK (tipo_pago IN ('Efectivo', 'Transferencia', 'Depósito Bancario')),
    CONSTRAINT chk_venta_estado CHECK (estado IN ('Emitida', 'Anulada'))
) ENGINE=InnoDB;


CREATE TABLE DETALLE_VENTA (
    id_detalle_venta INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT NOT NULL,
    id_producto INT NOT NULL,
    vin_chasis VARCHAR(50) NULL UNIQUE,
    numero_motor VARCHAR(50) NULL UNIQUE,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    descuento DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    subtotal DECIMAL(12,2) NOT NULL,
    CONSTRAINT fk_detventa_venta FOREIGN KEY (id_venta) 
        REFERENCES VENTA(id_venta) 
        ON UPDATE CASCADE 
        ON DELETE CASCADE,
    CONSTRAINT fk_detventa_producto FOREIGN KEY (id_producto) 
        REFERENCES PRODUCTO(id_producto) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT chk_detventa_cantidad CHECK (cantidad > 0),
    CONSTRAINT chk_detventa_precio CHECK (precio_unitario > 0),
    CONSTRAINT chk_detventa_descuento CHECK (descuento >= 0),
    CONSTRAINT chk_detventa_subtotal CHECK (subtotal >= 0)
) ENGINE=InnoDB;
