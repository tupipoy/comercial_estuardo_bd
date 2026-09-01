
-- SISTEMA DE GESTIÓN DE VENTAS, COMPRAS E INVENTARIO - COMERCIAL ESTUARDO

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
    precio_venta DECIMAL(10,2) NOT NULL,
    stock_actual INT NOT NULL DEFAULT 0,
    stock_minimo INT NOT NULL DEFAULT 1,
    id_categoria INT NOT NULL,
    estado TINYINT(1) NOT NULL DEFAULT 1,
    CONSTRAINT fk_producto_categoria FOREIGN KEY (id_categoria) 
        REFERENCES CATEGORIA(id_categoria) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT chk_producto_precio CHECK (precio_venta > 0),
    CONSTRAINT chk_producto_stock_actual CHECK (stock_actual >= 0),
    CONSTRAINT chk_producto_stock_minimo CHECK (stock_minimo >= 0),
    CONSTRAINT chk_producto_estado CHECK (estado IN (0, 1))
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
    CONSTRAINT fk_compra_proveedor FOREIGN KEY (id_proveedor) 
        REFERENCES PROVEEDOR(id_proveedor) 
        ON UPDATE CASCADE 
        ON DELETE RESTRICT,
    CONSTRAINT fk_compra_empleado FOREIGN KEY (id_empleado) 
        REFERENCES EMPLEADO(id_empleado) 
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