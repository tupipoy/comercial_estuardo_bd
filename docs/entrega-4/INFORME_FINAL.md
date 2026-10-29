# Informe final del proyecto — Entrega 4

## Identificación

- **Proyecto:** Sistema de Gestión de Ventas, Compras e Inventario — Comercial Estuardo
- **SGBD:** MySQL 8+
- **Aplicación:** Flask, PyMySQL y Gunicorn
- **Despliegue:** Railway (activo; aceptación funcional completa pendiente)
- **Integrantes:** Elvin Guillermo Miranda Gómez (2690-24-16072); Juan Carlos Ochoa Samayoa (2690-23-7592)

## Problema y solución

El proyecto centraliza datos de productos, existencias, clientes, proveedores, compras y ventas. La solución implementa un modelo relacional InnoDB, lógica transaccional en procedimientos y triggers, controles de acceso por cargo y una interfaz web conectada a MySQL.

## Resultados técnicos

El modelo agrega inventario por sucursal, cabeceras y detalles de traslado, asigna compras y ventas a sucursales y conserva ocho entidades principales del negocio. Incluye vistas, triggers de stock/margen, cinco procedimientos y tres roles de base de datos. Administración ve el stock consolidado; Vendedores y Bodega consultan el de su sucursal. La migración 06 se aplicó en Railway después de generar y validar un respaldo completo; las 1,571 unidades de 53 productos se asignaron a Sucursal Central. La aplicación web incluye inventario, CRUD de Productos, Clientes, Proveedores, Categorías, Sucursales y Empleados, operaciones de compra y venta multiproducto y vistas de solo lectura de sus detalles. Los flujos por sucursal y las transacciones aún requieren prueba funcional integrada.

## Despliegue y validación

La aplicación está desplegada y accesible en Railway con Gunicorn. URL pública: https://comercialestuardobd-production.up.railway.app. El commit desplegado al publicar fue `3c611bb`. Tras aplicar la migración 06 y actualizar los objetos SQL, se comprobó que `/health` responde HTTP 200 y que el inventario conserva las 1,571 unidades bajo Sucursal Central. Falta probar compras, ventas, traslados y permisos con usuarios de la aplicación y completar los demás casos de aceptación.

## Limitaciones conocidas

- Las tablas asociativas se gestionan dentro de sus transacciones y tienen vistas de solo lectura; no se ofrece edición/borrado independiente del historial.
- La migración 06 ya se ejecutó en Railway; el respaldo local previo está en `backups/railway_pre_migracion06_20261029.sql.gz` y está excluido de Git. El stock histórico se asignó a Sucursal Central; debe redistribuirse mediante traslados según el conteo físico. Las transacciones por sucursal aún no tienen prueba funcional integrada. El DDL de instalación es destructivo; validar en un esquema temporal.
- La trazabilidad VIN/motor está modelada y el formulario exige seriales al vender productos en categoría cuyo nombre contenga “moto”; debe validarse en MySQL.

## Declaración de integridad académica

**Pendiente de revisión, aprobación y firma de cada integrante.** Antes de firmar, el equipo debe confirmar que revisó la versión final, que la bitácora consolidada identifica el apoyo de herramientas de IA y que cada integrante puede explicar las decisiones de modelado, seguridad, transacciones y despliegue. Esta sección no constituye una declaración ya aprobada por los integrantes.

## Referencias de entrega

- **Tag Git:** pendiente (`entrega-4`).
- **Respaldo previo local:** directorio `version1/`, snapshot del commit `9467202`, ignorado por Git y no desplegado.
- **URL pública:** https://comercialestuardobd-production.up.railway.app
- **Fecha de cierre:** pendiente.
