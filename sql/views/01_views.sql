USE comercial_estuardo_db;

-- =========================================================
-- VISTA 1: INVENTARIO VALORIZADO
-- Muestra el valor del inventario disponible al costo actual.
-- =========================================================
CREATE OR REPLACE VIEW vw_inventario_valorizado AS
SELECT
    p.id_producto,
    p.codigo_barra,
    p.nombre,
    c.nombre AS categoria,
    p.precio_costo,
    p.precio_venta,
    p.stock_actual,
    p.stock_minimo,
    (p.stock_actual * p.precio_costo) AS valor_inventario
FROM PRODUCTO AS p
INNER JOIN CATEGORIA AS c
    ON p.id_categoria = c.id_categoria
WHERE p.estado = 1;

-- =========================================================
-- VISTA 2: PRODUCTOS BAJO PUNTO DE REORDEN
-- =========================================================
CREATE OR REPLACE VIEW vw_productos_stock_critico AS
SELECT
    p.id_producto,
    p.codigo_barra,
    p.nombre,
    c.nombre AS categoria,
    p.stock_actual,
    p.stock_minimo
FROM PRODUCTO AS p
INNER JOIN CATEGORIA AS c
    ON p.id_categoria = c.id_categoria
WHERE p.estado = 1
  AND p.stock_actual <= p.stock_minimo;

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
