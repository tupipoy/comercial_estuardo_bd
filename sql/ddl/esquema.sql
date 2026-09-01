/*
 Archivo: esquema.sql
 Proyecto: Comercial Estuardo
 Descripción: Creación inicial de la base de datos y tabla sucursal.
 SGBD: MySQL
 Dependencias: Ninguna
*/

CREATE DATABASE IF NOT EXISTS comercial_estuardo
CHARACTER SET utf8mb4
COLLATE utf8mb4_0900_ai_ci;

USE comercial_estuardo;

CREATE TABLE IF NOT EXISTS sucursal (
    id_sucursal INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    municipio VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    estado ENUM('ACTIVA', 'INACTIVA') NOT NULL DEFAULT 'ACTIVA'
);


CREATE TABLE IF NOT EXISTS empleado (
    id_empleado INT AUTO_INCREMENT PRIMARY KEY,
    id_sucursal INT NOT NULL,
    nit_dpi VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    cargo VARCHAR(60) NOT NULL,
    telefono VARCHAR(20),

    CONSTRAINT fk_empleado_sucursal
        FOREIGN KEY (id_sucursal)
        REFERENCES sucursal(id_sucursal)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);


CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    id_empleado INT NOT NULL UNIQUE,
    nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL,
    rol ENUM(
        'ADMINISTRADOR',
        'VENDEDOR',
        'BODEGA'
    ) NOT NULL,
    estado ENUM('ACTIVO', 'INACTIVO') NOT NULL DEFAULT 'ACTIVO',

    CONSTRAINT fk_usuario_empleado
        FOREIGN KEY (id_empleado)
        REFERENCES empleado(id_empleado)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);



CREATE TABLE IF NOT EXISTS cliente (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nit_dpi VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(120) UNIQUE,
    direccion VARCHAR(200)
);


CREATE TABLE IF NOT EXISTS categoria (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre_cat VARCHAR(80) NOT NULL UNIQUE,
    descripcion VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS producto (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    id_categoria INT NOT NULL,
    codigo_barra VARCHAR(50) NOT NULL UNIQUE,
    nombre_prod VARCHAR(120) NOT NULL,
    stock_min INT NOT NULL DEFAULT 0,
    stock_actual INT NOT NULL DEFAULT 0,
    precio_venta DECIMAL(10,2) NOT NULL,
    descripcion VARCHAR(255),

    CONSTRAINT fk_producto_categoria
        FOREIGN KEY (id_categoria)
        REFERENCES categoria(id_categoria)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_producto_stock_min
        CHECK (stock_min >= 0),

    CONSTRAINT chk_producto_stock_actual
        CHECK (stock_actual >= 0),

    CONSTRAINT chk_producto_precio_venta
        CHECK (precio_venta >= 0)
);


CREATE TABLE IF NOT EXISTS proveedor (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nit VARCHAR(20) NOT NULL UNIQUE,
    razon_social VARCHAR(150) NOT NULL,
    contacto VARCHAR(100),
    telefono VARCHAR(20),
    direccion VARCHAR(200)
);


CREATE TABLE IF NOT EXISTS venta (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    id_sucursal INT NOT NULL,
    id_cliente INT NOT NULL,
    id_empleado INT NOT NULL,

    serie_factura VARCHAR(20) NOT NULL,
    num_factura VARCHAR(50) NOT NULL,
    fecha_emision DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_venta DECIMAL(12,2) NOT NULL DEFAULT 0,
    estado VARCHAR(30) NOT NULL,

    CONSTRAINT uq_venta_factura
        UNIQUE (serie_factura, num_factura),

    CONSTRAINT chk_venta_total
        CHECK (total_venta >= 0),

    CONSTRAINT fk_venta_sucursal
        FOREIGN KEY (id_sucursal)
        REFERENCES sucursal(id_sucursal)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_venta_cliente
        FOREIGN KEY (id_cliente)
        REFERENCES cliente(id_cliente)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_venta_empleado
        FOREIGN KEY (id_empleado)
        REFERENCES empleado(id_empleado)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);


CREATE TABLE IF NOT EXISTS detalle_venta (
    id_detalle_venta INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT NOT NULL,
    id_producto INT NOT NULL,

    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    descuento DECIMAL(10,2) NOT NULL DEFAULT 0,

    sub_total DECIMAL(12,2)
        GENERATED ALWAYS AS (
            (cantidad * precio_unitario) - descuento
        ) STORED,

    CONSTRAINT fk_detalle_venta_venta
        FOREIGN KEY (id_venta)
        REFERENCES venta(id_venta)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_detalle_venta_producto
        FOREIGN KEY (id_producto)
        REFERENCES producto(id_producto)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_detalle_venta_cantidad
        CHECK (cantidad > 0),

    CONSTRAINT chk_detalle_venta_precio
        CHECK (precio_unitario >= 0),

    CONSTRAINT chk_detalle_venta_descuento
        CHECK (descuento >= 0),

    CONSTRAINT chk_detalle_venta_descuento_valido
        CHECK (descuento <= cantidad * precio_unitario),

    CONSTRAINT uq_venta_producto
        UNIQUE (id_venta, id_producto)
);


CREATE TABLE IF NOT EXISTS compra (
    id_compra INT AUTO_INCREMENT PRIMARY KEY,
    id_proveedor INT NOT NULL,
    id_empleado INT NOT NULL,

    num_orden VARCHAR(50) NOT NULL UNIQUE,
    fecha_compra DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_compra DECIMAL(12,2) NOT NULL DEFAULT 0,

    CONSTRAINT chk_compra_total
        CHECK (total_compra >= 0),

    CONSTRAINT fk_compra_proveedor
        FOREIGN KEY (id_proveedor)
        REFERENCES proveedor(id_proveedor)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_compra_empleado
        FOREIGN KEY (id_empleado)
        REFERENCES empleado(id_empleado)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);


CREATE TABLE IF NOT EXISTS detalle_compra (
    id_detalle_compra INT AUTO_INCREMENT PRIMARY KEY,
    id_compra INT NOT NULL,
    id_producto INT NOT NULL,

    cant_recibida INT NOT NULL,
    costo_unit DECIMAL(10,2) NOT NULL,

    sub_total DECIMAL(12,2)
        GENERATED ALWAYS AS (cant_recibida * costo_unit) STORED,

    CONSTRAINT fk_detalle_compra_compra
        FOREIGN KEY (id_compra)
        REFERENCES compra(id_compra)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_detalle_compra_producto
        FOREIGN KEY (id_producto)
        REFERENCES producto(id_producto)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_detalle_compra_cantidad
        CHECK (cant_recibida > 0),

    CONSTRAINT chk_detalle_compra_costo
        CHECK (costo_unit >= 0),

    CONSTRAINT uq_compra_producto
        UNIQUE (id_compra, id_producto)
);


