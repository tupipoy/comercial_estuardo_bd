-- Archivo: sql/security/03_supplier_proposals.sql
-- Autor: Equipo Comercial Estuardo
-- Descripción: configura roles y privilegios.
-- Dependencias: Esquema y objetos previos según INSTALL.md; no ejecutar sobre producción sin respaldo.
-- MySQL 8.0.30+; ejecutar después de la migración 09 y los roles base.
USE comercial_estuardo_db;
REVOKE IF EXISTS INSERT, UPDATE, DELETE ON comercial_estuardo_db.PROVEEDOR FROM 'rol_bodega';
GRANT SELECT ON comercial_estuardo_db.PROVEEDOR TO 'rol_bodega';
GRANT SELECT ON comercial_estuardo_db.PROPUESTA_PROVEEDOR TO 'rol_bodega';
GRANT INSERT (nit,razon_social,contacto,telefono,correo,direccion,id_solicitante)
 ON comercial_estuardo_db.PROPUESTA_PROVEEDOR TO 'rol_bodega';
GRANT SELECT,INSERT ON comercial_estuardo_db.EVENTO_PROVEEDOR TO 'rol_bodega';
