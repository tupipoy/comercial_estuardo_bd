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

El modelo agrega inventario por sucursal, cabeceras y detalles de traslado, asigna compras y ventas a sucursales y conserva ocho entidades principales del negocio. Incluye vistas, triggers de stock/margen, cinco procedimientos y tres roles de base de datos. Administración ve el stock consolidado; Vendedores y Bodega consultan el de su sucursal. El código y los scripts están implementados localmente; falta migrar y probar la base de Railway antes de desplegar esta versión. La aplicación web incluye inventario, CRUD de Productos, Clientes, Proveedores, Categorías, Sucursales y Empleados, operaciones de compra y venta mult producto y vistas de solo lectura de sus detalles. El usuario confirmó en Railway la existencia de los tres triggers que protegen las ventas y que no quedaron productos con precio por debajo del costo; los flujos de compra/venta mult producto aún requieren prueba funcional integrada.

## Despliegue y validación

La aplicación está desplegada y accesible en Railway con Gunicorn. URL pública: https://comercialestuardobd-production.up.railway.app. El usuario confirmó que el dominio abre, que el login y los módulos funcionan, que pudo crear y editar clientes, y que aplicó la migración de margen y verificó los triggers en la base productiva. Falta registrar el commit exacto activo, validar compras/ventas en el despliegue y documentar la instalación limpia y los demás casos de aceptación.

## Limitaciones conocidas

- Las tablas asociativas se gestionan dentro de sus transacciones y tienen vistas de solo lectura; no se ofrece edición/borrado independiente del historial.
- La migración 06 requiere respaldo previo y asigna el stock histórico global a Sucursal Central; luego debe redistribuirse mediante traslados según el conteo físico. No se ha ejecutado en Railway ni se han probado transacciones por sucursal. El DDL de instalación es destructivo; validar en un esquema temporal.
- La trazabilidad VIN/motor está modelada y el formulario exige seriales al vender productos en categoría cuyo nombre contenga “moto”; debe validarse en MySQL.

## Declaración de integridad académica

**Pendiente de revisión, aprobación y firma de cada integrante.** Antes de firmar, el equipo debe confirmar que revisó la versión final, que la bitácora consolidada identifica el apoyo de herramientas de IA y que cada integrante puede explicar las decisiones de modelado, seguridad, transacciones y despliegue. Esta sección no constituye una declaración ya aprobada por los integrantes.

## Referencias de entrega

- **Tag Git:** pendiente (`entrega-4`).
- **Respaldo previo local:** directorio `version1/`, snapshot del commit `9467202`, ignorado por Git y no desplegado.
- **URL pública:** https://comercialestuardobd-production.up.railway.app
- **Fecha de cierre:** pendiente.
