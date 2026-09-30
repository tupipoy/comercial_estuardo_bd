USE comercial_estuardo_db;

-- =====================================================
-- DATOS INICIALES DE COMERCIAL ESTUARDO
-- Este seed se puede ejecutar varias veces sin duplicar
-- los registros definidos aquí.
-- =====================================================

-- -----------------------------------------------------
-- SUCURSALES
-- -----------------------------------------------------
INSERT INTO SUCURSAL (nombre, direccion, telefono, municipio, estado)
SELECT 'Sucursal Central', '4 Calle Zona 1', '77630001', 'San Juan Ostuncalco', 1
WHERE NOT EXISTS (
    SELECT 1 FROM SUCURSAL WHERE nombre = 'Sucursal Central'
);

INSERT INTO SUCURSAL (nombre, direccion, telefono, municipio, estado)
SELECT 'Sucursal Quetzaltenango', 'Zona 3', '77630002', 'Quetzaltenango', 1
WHERE NOT EXISTS (
    SELECT 1 FROM SUCURSAL WHERE nombre = 'Sucursal Quetzaltenango'
);

-- -----------------------------------------------------
-- CATEGORÍAS
-- -----------------------------------------------------
INSERT INTO CATEGORIA (nombre, descripcion, estado)
SELECT 'Repuestos de Motor', 'Repuestos para motor de motocicleta', 1
WHERE NOT EXISTS (
    SELECT 1 FROM CATEGORIA WHERE nombre = 'Repuestos de Motor'
);

INSERT INTO CATEGORIA (nombre, descripcion, estado)
SELECT 'Llantas', 'Llantas y neumáticos para motocicleta', 1
WHERE NOT EXISTS (
    SELECT 1 FROM CATEGORIA WHERE nombre = 'Llantas'
);

INSERT INTO CATEGORIA (nombre, descripcion, estado)
SELECT 'Lubricantes', 'Aceites y lubricantes', 1
WHERE NOT EXISTS (
    SELECT 1 FROM CATEGORIA WHERE nombre = 'Lubricantes'
);

INSERT INTO CATEGORIA (nombre, descripcion, estado)
SELECT 'Accesorios', 'Accesorios para motociclista y motocicleta', 1
WHERE NOT EXISTS (
    SELECT 1 FROM CATEGORIA WHERE nombre = 'Accesorios'
);

INSERT INTO CATEGORIA (nombre, descripcion, estado)
SELECT 'Eléctrico', 'Componentes del sistema eléctrico', 1
WHERE NOT EXISTS (
    SELECT 1 FROM CATEGORIA WHERE nombre = 'Eléctrico'
);

-- -----------------------------------------------------
-- PROVEEDORES
-- -----------------------------------------------------
INSERT INTO PROVEEDOR
    (nit, razon_social, contacto, telefono, correo, direccion, estado)
SELECT
    '1000001-1', 'Repuestos de Guatemala, S.A.', 'Carlos López',
    '55550001', 'ventas@repuestosgt.com', 'Guatemala', 1
WHERE NOT EXISTS (
    SELECT 1 FROM PROVEEDOR WHERE nit = '1000001-1'
);

INSERT INTO PROVEEDOR
    (nit, razon_social, contacto, telefono, correo, direccion, estado)
SELECT
    '1000002-2', 'Moto Partes Occidente', 'Andrea Gómez',
    '55550002', 'ventas@motopartes.com', 'Quetzaltenango', 1
WHERE NOT EXISTS (
    SELECT 1 FROM PROVEEDOR WHERE nit = '1000002-2'
);

INSERT INTO PROVEEDOR
    (nit, razon_social, contacto, telefono, correo, direccion, estado)
SELECT
    '1000003-3', 'Lubricantes Centroamericanos', 'José Pérez',
    '55550003', 'ventas@lubricantesca.com', 'Guatemala', 1
WHERE NOT EXISTS (
    SELECT 1 FROM PROVEEDOR WHERE nit = '1000003-3'
);

-- -----------------------------------------------------
-- CLIENTES
-- -----------------------------------------------------
INSERT INTO CLIENTE
    (nit, cui, nombres, apellidos, telefono, correo, direccion, estado)
SELECT
    'CF', NULL, 'Consumidor', 'Final', '00000000', NULL,
    'San Juan Ostuncalco', 1
WHERE NOT EXISTS (
    SELECT 1 FROM CLIENTE WHERE nit = 'CF'
);

INSERT INTO CLIENTE
    (nit, cui, nombres, apellidos, telefono, correo, direccion, estado)
SELECT
    '1234567-8', '1234567890101', 'Carlos', 'Gómez', '55551001',
    'carlos@example.com', 'San Juan Ostuncalco', 1
WHERE NOT EXISTS (
    SELECT 1 FROM CLIENTE WHERE nit = '1234567-8'
);

INSERT INTO CLIENTE
    (nit, cui, nombres, apellidos, telefono, correo, direccion, estado)
SELECT
    '2234567-8', '2234567890101', 'María', 'López', '55551002',
    'maria@example.com', 'Quetzaltenango', 1
WHERE NOT EXISTS (
    SELECT 1 FROM CLIENTE WHERE nit = '2234567-8'
);
