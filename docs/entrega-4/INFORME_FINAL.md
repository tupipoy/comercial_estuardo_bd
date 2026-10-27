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

La base cuenta con ocho entidades principales y dos entidades asociativas, datos de prueba, vistas, dos triggers, cuatro procedimientos (versiones de una línea y mult producto) y tres roles de base de datos. La aplicación web incluye inventario, CRUD de Productos, Clientes, Proveedores, Categorías, Sucursales y Empleados, operaciones de compra y venta mult producto y vistas de solo lectura de sus detalles. Los flujos SQL mult producto aún requieren prueba integrada con MySQL.

## Despliegue y validación

La aplicación está desplegada y accesible en Railway con Gunicorn. URL pública: https://comercialestuardobd-production.up.railway.app. El usuario confirmó que el dominio abre, que el login y los módulos funcionan, y que pudo crear y editar clientes. Falta registrar la versión exacta probada, validar compras/ventas en el despliegue y documentar la instalación limpia y los demás casos de aceptación.

## Limitaciones conocidas

- Las tablas asociativas se gestionan dentro de sus transacciones y tienen vistas de solo lectura; no se ofrece edición/borrado independiente del historial.
- La ejecución integrada de procedimientos y transacciones mult producto sigue pendiente de registrar. Railway tiene servicio MySQL, pero no se debe usar el DDL destructivo de instalación sobre la base productiva; validar en un esquema o servicio temporal.
- La trazabilidad VIN/motor está modelada y el formulario exige seriales al vender productos en categoría cuyo nombre contenga “moto”; debe validarse en MySQL.

## Declaración de integridad académica

**Pendiente de revisión, aprobación y firma de cada integrante.** Antes de firmar, el equipo debe confirmar que revisó la versión final, que la bitácora consolidada identifica el apoyo de herramientas de IA y que cada integrante puede explicar las decisiones de modelado, seguridad, transacciones y despliegue. Esta sección no constituye una declaración ya aprobada por los integrantes.

## Referencias de entrega

- **Tag Git:** pendiente (`entrega-4`).
- **URL pública:** https://comercialestuardobd-production.up.railway.app
- **Fecha de cierre:** pendiente.
