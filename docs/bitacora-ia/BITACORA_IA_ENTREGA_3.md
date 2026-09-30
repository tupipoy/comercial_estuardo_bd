# Bitácora de uso de IA — Entrega 3

## Proyecto

**Sistema de Gestión de Inventarios y Ventas — Comercial Estuardo**

**Fecha de registro:** 29 de septiembre de 2026

## Uso de la herramienta

Se utilizó un asistente de inteligencia artificial como apoyo para revisar el repositorio, implementar y documentar módulos Flask, preparar la instalación de MySQL y organizar evidencia de pruebas. El equipo conserva la responsabilidad de revisar el código, validar los resultados y decidir qué se entrega.

| Actividad | Apoyo de IA | Revisión o validación realizada |
|---|---|---|
| Ventas Web | Integración de rutas y plantillas con `sp_registrar_venta`, control por cargo y validación del estado de los triggers | Instalación completa en esquema temporal; pruebas de venta válida y venta sin stock |
| Compras Web | Integración de rutas y plantillas con `sp_registrar_compra`, y validación de proveedor, producto, cantidad y costo | Registro temporal de compra y comprobación de persistencia, incremento de stock y actualización de costo |
| CRUD de Proveedores | Rutas para listar, crear, editar y desactivar; plantillas y enlaces de navegación | Operaciones comprobadas con persistencia en MySQL temporal |
| Instalación SQL limpia | Revisión de orden y compatibilidad de los scripts; aislamiento mediante nombres temporales de esquema y roles | Se ejecutaron DDL, seed, bulk, vistas, triggers, procedimientos y roles; conteos y objetos fueron verificados |
| Pruebas funcionales | Revisión y actualización de los ocho casos documentados | CP01–CP08 se ejecutaron en Flask y MySQL temporales; todos pasaron |
| Documentación | Actualización de README, instalación, avance web, matriz y casos de prueba | `git diff --check` no reportó errores de formato |

## Resultado de las pruebas de instalación

La instalación se ejecutó en una base MySQL temporal independiente. Se verificaron 50 filas en cada entidad principal y tabla de detalle, tres vistas, dos triggers y dos procedimientos. Después se probaron autenticación, permisos por rol, CRUD de Productos y Clientes, Compras Web, CRUD de Proveedores y Ventas Web.

La prueba no modificó `comercial_estuardo_db`. El esquema y los roles temporales se eliminaron al finalizar. El procedimiento reproducible se describe en [INSTALL.md](../../INSTALL.md), y el detalle de resultados está en los [casos de prueba](../casos-prueba/CASOS_PRUEBA_ENTREGA_3.md).

## Límites y revisión humana

- La ejecución cubrió la instalación y flujos principales en una copia temporal; no constituye una prueba de despliegue en producción.
- El avance web de aproximadamente 70% es una estimación frente al alcance académico, no una medición automática de cobertura.
- Antes de entregar, el equipo debe revisar el contenido, confirmar que coincide con la rúbrica y completar personalmente las firmas de la certificación.
- No se incluyeron credenciales reales en este documento.
