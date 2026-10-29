-- Archivo: sql/security/02_inventory_control.sql
-- Autor: Equipo Comercial Estuardo
-- Descripción: configura roles y privilegios.
-- Dependencias: Esquema y objetos previos según INSTALL.md; no ejecutar sobre producción sin respaldo.
USE comercial_estuardo_db;
GRANT SELECT (requiere_serie) ON comercial_estuardo_db.PRODUCTO TO 'rol_ventas';
GRANT SELECT ON comercial_estuardo_db.UNIDAD_PRODUCTO TO 'rol_ventas','rol_bodega';
GRANT SELECT ON comercial_estuardo_db.HISTORIAL_UNIDAD TO 'rol_ventas','rol_bodega';
GRANT SELECT ON comercial_estuardo_db.MOVIMIENTO_INVENTARIO TO 'rol_ventas','rol_bodega';
GRANT SELECT ON comercial_estuardo_db.TRASLADO TO 'rol_ventas';
GRANT SELECT ON comercial_estuardo_db.DETALLE_TRASLADO TO 'rol_ventas';
GRANT SELECT ON comercial_estuardo_db.REVERSO_DOCUMENTO TO 'rol_ventas','rol_bodega';
GRANT SELECT ON comercial_estuardo_db.DETALLE_REVERSO TO 'rol_ventas','rol_bodega';
GRANT SELECT,INSERT,UPDATE ON comercial_estuardo_db.COMPRA TO 'rol_bodega';
GRANT SELECT,INSERT ON comercial_estuardo_db.DETALLE_COMPRA TO 'rol_bodega';
GRANT SELECT,INSERT,UPDATE ON comercial_estuardo_db.TRASLADO TO 'rol_bodega';
GRANT SELECT,INSERT,UPDATE ON comercial_estuardo_db.DETALLE_TRASLADO TO 'rol_bodega';
GRANT SELECT,INSERT,UPDATE ON comercial_estuardo_db.UNIDAD_PRODUCTO TO 'rol_bodega';
GRANT SELECT,INSERT,UPDATE ON comercial_estuardo_db.TRASLADO_UNIDAD TO 'rol_bodega';
GRANT SELECT,INSERT ON comercial_estuardo_db.EVENTO_TRASLADO TO 'rol_bodega';
GRANT SELECT,INSERT ON comercial_estuardo_db.CONTEO_INVENTARIO TO 'rol_bodega';
-- Las autorizaciones por usuario, sucursal y estado se aplican en el servicio web.
-- El actor se consulta desde EMPLEADO en cada operación; no se confía en campos del formulario.
-- Los procedimientos de traslados de la versión 07 no manejan reservas ni unidades.
-- Los nuevos movimientos se ejecutan mediante web/inventory_control.py.
REVOKE EXECUTE ON PROCEDURE comercial_estuardo_db.sp_registrar_traslado FROM 'rol_bodega';
REVOKE EXECUTE ON PROCEDURE comercial_estuardo_db.sp_resolver_traslado FROM 'rol_bodega';
REVOKE EXECUTE ON PROCEDURE comercial_estuardo_db.sp_despachar_traslado FROM 'rol_bodega';
REVOKE EXECUTE ON PROCEDURE comercial_estuardo_db.sp_recibir_traslado FROM 'rol_bodega';
