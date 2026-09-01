/*
 Archivo: datos_prueba.sql
 Proyecto: Comercial Estuardo (Motos)
 Descripción: Datos ficticios de prueba para validar el funcionamiento de la base de datos.
 SGBD: MySQL
 Dependencias: sql/ddl/esquema.sql
*/

USE comercial_estuardo;



-- DATOS DE PRUEBA: SUCURSAL
-- La primera sucursal corresponde a la ubicación principal
-- de Comercial Estuardo. Las demás son datos ficticios.


INSERT INTO sucursal (
    nombre,
    direccion,
    municipio,
    telefono
)
VALUES (
    'Sucursal Principal',
    '1ra Avenida 1-27, Zona 3',
    'San Juan Ostuncalco',
    '42671877'
);

INSERT INTO sucursal (
    nombre,
    direccion,
    municipio,
    telefono
)
SELECT
    CONCAT('Sucursal de Prueba ', LPAD(n, 2, '0')),
    CONCAT('Dirección ficticia ', n),
    'San Juan Ostuncalco',
    CONCAT('5000', LPAD(n, 4, '0'))
FROM (
    SELECT (u.n + d.n * 10) AS n
    FROM
        (
            SELECT 0 n UNION ALL SELECT 1 UNION ALL SELECT 2
            UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
            UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8
            UNION ALL SELECT 9
        ) u
    CROSS JOIN
        (
            SELECT 0 n UNION ALL SELECT 1 UNION ALL SELECT 2
            UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
        ) d
) numeros
WHERE n BETWEEN 2 AND 50;





-- DATOS DE PRUEBA: EMPLEADO
-- Se genera un empleado ficticio por sucursal.


INSERT INTO empleado (
    id_sucursal,
    nit_dpi,
    nombre,
    apellido,
    cargo,
    telefono
)
SELECT
    id_sucursal,
    CONCAT('DPI-', LPAD(id_sucursal, 8, '0')),
    CONCAT('Empleado ', LPAD(id_sucursal, 2, '0')),
    'Prueba',
    CASE
        WHEN MOD(id_sucursal, 3) = 0 THEN 'Administrador'
        WHEN MOD(id_sucursal, 3) = 1 THEN 'Vendedor'
        ELSE 'Bodega'
    END,
    CONCAT('5555', LPAD(id_sucursal, 4, '0'))
FROM sucursal
ORDER BY id_sucursal
LIMIT 50;




-- DATOS DE PRUEBA: USUARIO
-- Se genera una cuenta por empleado para pruebas de login.


INSERT INTO usuario (
    id_empleado,
    nombre_usuario,
    contrasena,
    rol
)
SELECT
    id_empleado,
    CONCAT('usuario', LPAD(id_empleado, 2, '0')),
    SHA2(CONCAT('ClaveTemporal', id_empleado), 256),
    CASE
        WHEN cargo = 'Administrador' THEN 'ADMINISTRADOR'
        WHEN cargo = 'Vendedor' THEN 'VENDEDOR'
        ELSE 'BODEGA'
    END
FROM empleado
ORDER BY id_empleado
LIMIT 50;




-- DATOS DE PRUEBA: CLIENTE
-- Se generan 50 clientes ficticios.


INSERT INTO cliente (
    nit_dpi,
    nombre,
    apellido,
    telefono,
    correo,
    direccion
)
SELECT
    CONCAT('NIT-DPI-', LPAD(id_empleado, 8, '0')),
    CONCAT('Cliente ', LPAD(id_empleado, 2, '0')),
    CONCAT('Apellido ', LPAD(id_empleado, 2, '0')),
    CONCAT('5200', LPAD(id_empleado, 4, '0')),
    CONCAT('cliente', id_empleado, '@correo.test'),
    CONCAT(
        'Dirección ficticia cliente ',
        id_empleado,
        ', Quetzaltenango, Guatemala'
    )
FROM empleado
ORDER BY id_empleado
LIMIT 50;







-- DATOS DE PRUEBA: CATEGORIA
-- Catálogo principal de tipos de productos.


INSERT INTO categoria (
    nombre_cat,
    descripcion
)
VALUES
(
    'Motocicletas',
    'Motocicletas disponibles para la venta'
),
(
    'Repuestos',
    'Repuestos y piezas para motocicletas'
),
(
    'Cascos',
    'Cascos y equipo de protección para motociclistas'
);






-- DATOS DE PRUEBA: PRODUCTO
-- Se generan 50 productos distribuidos entre
-- motocicletas, repuestos y cascos.


INSERT INTO producto (
    id_categoria,
    codigo_barra,
    nombre_prod,
    stock_min,
    stock_actual,
    precio_venta,
    descripcion
)
SELECT
    CASE
        WHEN MOD(n, 3) = 1 THEN
            (SELECT id_categoria
             FROM categoria
             WHERE nombre_cat = 'Motocicletas')

        WHEN MOD(n, 3) = 2 THEN
            (SELECT id_categoria
             FROM categoria
             WHERE nombre_cat = 'Repuestos')

        ELSE
            (SELECT id_categoria
             FROM categoria
             WHERE nombre_cat = 'Cascos')
    END,

    CASE
        WHEN MOD(n, 3) = 1
            THEN CONCAT('MOTO-', LPAD(n, 3, '0'))
        WHEN MOD(n, 3) = 2
            THEN CONCAT('REP-', LPAD(n, 3, '0'))
        ELSE
            CONCAT('CAS-', LPAD(n, 3, '0'))
    END,

    CASE
        WHEN MOD(n, 3) = 1
            THEN CONCAT('Motocicleta modelo ', n)
        WHEN MOD(n, 3) = 2
            THEN CONCAT('Repuesto ', n)
        ELSE
            CONCAT('Casco modelo ', n)
    END,

    3,
    10 + MOD(n, 20),

    CASE
        WHEN MOD(n, 3) = 1 THEN 10500 + (n * 150)
        WHEN MOD(n, 3) = 2 THEN 80 + (n * 8)
        ELSE 400 + (n * 15)
    END,

    CONCAT('Producto ficticio de prueba número ', n)

FROM (
    SELECT (u.n + d.n * 10 + 1) AS n
    FROM
        (
            SELECT 0 n UNION ALL SELECT 1 UNION ALL SELECT 2
            UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
            UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8
            UNION ALL SELECT 9
        ) u
    CROSS JOIN
        (
            SELECT 0 n UNION ALL SELECT 1 UNION ALL SELECT 2
            UNION ALL SELECT 3 UNION ALL SELECT 4
        ) d
) numeros
WHERE n <= 50;




-- DATOS DE PRUEBA: PROVEEDOR
-- Se generan 50 proveedores ficticios.


INSERT INTO proveedor (
    nit,
    razon_social,
    contacto,
    telefono,
    direccion
)
SELECT
    CONCAT('NIT-PROV-', LPAD(n, 6, '0')),
    CONCAT('Proveedor ', LPAD(n, 2, '0')),
    CONCAT('Contacto ', n),
    CONCAT('5555', LPAD(n, 4, '0')),
    CONCAT(
        'Dirección ficticia proveedor ',
        n,
        ', Guatemala'
    )
FROM (
    SELECT (u.n + d.n * 10 + 1) AS n
    FROM
        (
            SELECT 0 n UNION ALL SELECT 1 UNION ALL SELECT 2
            UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
            UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8
            UNION ALL SELECT 9
        ) u
    CROSS JOIN
        (
            SELECT 0 n UNION ALL SELECT 1 UNION ALL SELECT 2
            UNION ALL SELECT 3 UNION ALL SELECT 4
        ) d
) numeros
WHERE n <= 50;




-- VERIFICACIÓN DE DATOS CARGADOS


SELECT 'sucursal' AS tabla, COUNT(*) AS registros FROM sucursal
UNION ALL
SELECT 'empleado', COUNT(*) FROM empleado
UNION ALL
SELECT 'usuario', COUNT(*) FROM usuario
UNION ALL
SELECT 'cliente', COUNT(*) FROM cliente
UNION ALL
SELECT 'categoria', COUNT(*) FROM categoria
UNION ALL
SELECT 'producto', COUNT(*) FROM producto
UNION ALL
SELECT 'proveedor', COUNT(*) FROM proveedor;