-- Archivo: sql/views/01_views.sql
-- Autor: Equipo Comercial Estuardo
-- Descripción: crea vistas de inventario, stock crítico y ventas.
-- Dependencias: esquema y datos base instalados.
USE comercial_estuardo_db;

-- =========================================================
-- VISTA 1: INVENTARIO VALORIZADO
-- Muestra el valor del inventario disponible al costo actual.
-- =========================================================
CREATE OR REPLACE VIEW vw_inventario_valorizado AS
SELECT
    s.id_sucursal,
    s.nombre AS sucursal,
    p.id_producto,
    p.codigo_barra,
    p.nombre,
    c.nombre AS categoria,
    p.precio_costo,
    p.precio_venta,
    i.stock_actual,
    p.stock_minimo,
    (i.stock_actual * p.precio_costo) AS valor_inventario
FROM INVENTARIO_SUCURSAL AS i
INNER JOIN PRODUCTO AS p ON p.id_producto = i.id_producto
INNER JOIN SUCURSAL AS s ON s.id_sucursal = i.id_sucursal
INNER JOIN CATEGORIA AS c ON c.id_categoria = p.id_categoria
WHERE p.estado = 1 AND s.estado = 1;

-- =========================================================
-- VISTA 2: PRODUCTOS BAJO PUNTO DE REORDEN POR SUCURSAL
-- =========================================================
CREATE OR REPLACE VIEW vw_productos_stock_critico AS
SELECT
    s.id_sucursal,
    s.nombre AS sucursal,
    p.id_producto,
    p.codigo_barra,
    p.nombre,
    c.nombre AS categoria,
    i.stock_actual,
    p.stock_minimo
FROM INVENTARIO_SUCURSAL AS i
INNER JOIN PRODUCTO AS p ON p.id_producto = i.id_producto
INNER JOIN SUCURSAL AS s ON s.id_sucursal = i.id_sucursal
INNER JOIN CATEGORIA AS c ON c.id_categoria = p.id_categoria
WHERE p.estado = 1 AND s.estado = 1
  AND i.stock_actual <= p.stock_minimo;

-- =========================================================
-- VISTA 3: VENTAS DETALLADAS
-- Venta con los datos relacionados de cliente, empleado y sucursal.
-- =========================================================
CREATE OR REPLACE VIEW vw_ventas_detalladas AS
SELECT
    v.id_venta,
    v.serie_factura,
    v.numero_factura,
    v.fecha_venta,
    v.total_venta,
    v.tipo_pago,
    v.estado,
    c.id_cliente,
    CONCAT(c.nombres, ' ', IFNULL(c.apellidos, '')) AS cliente,
    e.id_empleado,
    CONCAT(e.nombres, ' ', e.apellidos) AS empleado,
    s.id_sucursal,
    s.nombre AS sucursal
FROM VENTA AS v
INNER JOIN CLIENTE AS c
    ON v.id_cliente = c.id_cliente
INNER JOIN EMPLEADO AS e
    ON v.id_empleado = e.id_empleado
INNER JOIN SUCURSAL AS s
    ON v.id_sucursal = s.id_sucursal;
