USE comercial_estuardo_db;

-- Roles de base de datos para Comercial Estuardo.
-- Ejecutar después de crear las vistas y los procedimientos almacenados.
CREATE ROLE IF NOT EXISTS
    'rol_administrador',
    'rol_ventas',
    'rol_bodega';

-- Administración: control completo del esquema, sin delegar privilegios.
GRANT ALL PRIVILEGES ON comercial_estuardo_db.*
    TO 'rol_administrador';

-- Ventas: consulta de datos necesarios para atender una venta y
-- gestión de clientes. Las ventas se registran mediante el procedimiento,
-- que crea cabecera y detalle de forma transaccional.
GRANT SELECT ON comercial_estuardo_db.CATEGORIA
    TO 'rol_ventas';
GRANT SELECT (
    id_producto, codigo_barra, nombre, precio_venta,
    stock_actual, stock_minimo, id_categoria, estado
) ON comercial_estuardo_db.PRODUCTO
    TO 'rol_ventas';
GRANT SELECT (
    id_empleado, nombres, apellidos, cargo, id_sucursal, estado
) ON comercial_estuardo_db.EMPLEADO
    TO 'rol_ventas';
GRANT SELECT ON comercial_estuardo_db.SUCURSAL
    TO 'rol_ventas';
GRANT SELECT, INSERT, UPDATE ON comercial_estuardo_db.CLIENTE
    TO 'rol_ventas';
GRANT SELECT ON comercial_estuardo_db.VENTA
    TO 'rol_ventas';
GRANT SELECT ON comercial_estuardo_db.DETALLE_VENTA
    TO 'rol_ventas';
GRANT EXECUTE ON PROCEDURE comercial_estuardo_db.sp_registrar_venta
    TO 'rol_ventas';

-- Bodega: mantenimiento de catálogo, proveedores y compras. Las compras
-- se registran mediante el procedimiento para que detalle, existencias y
-- costo actual se actualicen dentro de una sola transacción.
GRANT SELECT ON comercial_estuardo_db.CATEGORIA
    TO 'rol_bodega';
GRANT SELECT, INSERT, UPDATE ON comercial_estuardo_db.PRODUCTO
    TO 'rol_bodega';
GRANT SELECT, INSERT, UPDATE ON comercial_estuardo_db.PROVEEDOR
    TO 'rol_bodega';
GRANT SELECT (
    id_empleado, nombres, apellidos, cargo, id_sucursal, estado
) ON comercial_estuardo_db.EMPLEADO
    TO 'rol_bodega';
GRANT SELECT ON comercial_estuardo_db.COMPRA
    TO 'rol_bodega';
GRANT SELECT ON comercial_estuardo_db.DETALLE_COMPRA
    TO 'rol_bodega';
GRANT EXECUTE ON PROCEDURE comercial_estuardo_db.sp_registrar_compra
    TO 'rol_bodega';

-- La asignación a usuarios se realiza cuando existan las cuentas MySQL.
-- Ejemplo (reemplazar por los usuarios reales):
-- GRANT 'rol_ventas' TO 'usuario_ventas'@'localhost';
-- SET DEFAULT ROLE 'rol_ventas' TO 'usuario_ventas'@'localhost';
