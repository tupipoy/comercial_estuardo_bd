# Informe final del proyecto — Entrega 4

## Identificación

- **Proyecto:** Sistema de Gestión de Ventas, Compras e Inventario — Comercial Estuardo
- **SGBD:** MySQL 8+
- **Aplicación:** Flask, PyMySQL y Gunicorn
- **Despliegue previsto:** Railway
- **Integrantes:** Elvin Guillermo Miranda Gómez (2690-24-16072); Juan Carlos Ochoa Samayoa (2690-23-7592)

## Problema y solución

El proyecto centraliza datos de productos, existencias, clientes, proveedores, compras y ventas. La solución implementa un modelo relacional InnoDB, lógica transaccional en procedimientos y triggers, controles de acceso por cargo y una interfaz web conectada a MySQL.

## Resultados técnicos

La base cuenta con ocho entidades principales y dos entidades asociativas, datos de prueba, vistas, dos triggers, cuatro procedimientos (versiones de una línea y mult producto) y tres roles de base de datos. La aplicación web incluye inventario, CRUD de Productos, Clientes, Proveedores, Categorías, Sucursales y Empleados, operaciones de compra y venta mult producto y vistas de solo lectura de sus detalles. Los flujos SQL mult producto aún requieren prueba integrada con MySQL.

## Despliegue y validación

La aplicación está preparada para ejecutarse con Gunicorn en Railway; falta registrar aquí la URL, fecha de despliegue, configuración de servicios y evidencia de funcionamiento cuando el equipo complete la publicación. Los resultados de instalación limpia y pruebas de aceptación se añadirán sin atribuir resultados no ejecutados.

## Limitaciones conocidas

- Las tablas asociativas se gestionan dentro de sus transacciones y tienen vistas de solo lectura; no se ofrece edición/borrado independiente del historial.
- La ejecución integrada de procedimientos y transacciones mult producto sigue pendiente por falta de una instancia MySQL disponible en la validación actual.
- La trazabilidad VIN/motor está modelada y el formulario exige seriales al vender productos en categoría cuyo nombre contenga “moto”; debe validarse en MySQL.

## Declaración de integridad académica

El equipo declara que revisó y validó el diseño, los scripts, el código y la documentación incluidos en la versión entregada; que identificó el apoyo recibido de herramientas de inteligencia artificial en la bitácora consolidada; y que puede explicar individualmente las decisiones de modelado, seguridad, transacciones y despliegue. Completar y firmar esta declaración únicamente después de la revisión final del equipo.

## Referencias de entrega

- **Tag Git:** pendiente (`entrega-4`).
- **URL pública:** pendiente.
- **Fecha de cierre:** pendiente.
