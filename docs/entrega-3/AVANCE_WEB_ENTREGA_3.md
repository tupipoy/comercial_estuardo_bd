# AVANCE WEB — ENTREGA 3

## Proyecto

**Sistema de Gestión de Inventarios y Ventas — Comercial Estuardo**

## Resumen

La aplicación Flask integra autenticación de empleados, autorización por cargo y módulos web conectados a MySQL. El avance funcional de esta fase se estima en aproximadamente **70%**, según los módulos descritos para la entrega. Es una estimación de implementación; la evaluación final corresponde a la rúbrica del curso.

## Funciones implementadas

- Inicio y cierre de sesión con contraseñas verificadas mediante hash y sesión Flask.
- Control de acceso por cargos Administrador, Vendedor y Bodega tanto en las rutas como en la navegación.
- Consulta de inventario y alerta de existencias bajas.
- CRUD de Productos, Clientes y Proveedores, con validación y desactivación lógica.
- Consulta y registro web de Ventas mediante `sp_registrar_venta`; los triggers validan y descuentan el inventario.
- Consulta y registro web de Compras mediante `sp_registrar_compra`; el procedimiento registra la compra, incrementa existencias y actualiza el costo vigente.
- Consultas SQL parametrizadas para las operaciones de la aplicación.

## Base de datos

La instalación limpia reúne el DDL, los datos semilla y masivos, tres vistas, dos triggers, dos procedimientos almacenados y tres roles MySQL con permisos diferenciados. Los scripts se ejecutaron en un esquema temporal separado y luego se eliminaron ese esquema y los roles de prueba.

## Verificación funcional

En una instalación temporal completa se ejecutaron los ocho casos de `docs/casos-prueba/CASOS_PRUEBA_ENTREGA_3.md`. Pasaron el inicio de sesión válido e inválido, el control de acceso, la persistencia de Productos y Clientes, la venta válida con descuento de stock y el rechazo transaccional de una venta sin existencias. También se verificaron el CRUD de Proveedores y la compra web con actualización de stock y costo.

La comprobación no modificó la base de datos local de trabajo. Para reproducirla, sigue [INSTALL.md](../../INSTALL.md) y consulta los resultados caso por caso en la [matriz de trazabilidad](MATRIZ_TRAZABILIDAD.md) y los [casos de prueba](../casos-prueba/CASOS_PRUEBA_ENTREGA_3.md).

## Alcance pendiente

El porcentaje es aproximado. Mejoras como ampliar los flujos de compra y venta a múltiples productos por operación, reportes adicionales, administración de cuentas de usuario y despliegue fuera del entorno local pueden desarrollarse en fases posteriores, de acuerdo con la rúbrica y el tiempo disponible.
