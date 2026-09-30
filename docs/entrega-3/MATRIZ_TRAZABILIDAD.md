# MATRIZ DE TRAZABILIDAD — ENTREGA 3

## Proyecto

**Sistema de Gestión de Inventarios y Ventas — Comercial Estuardo**

## Objetivo y criterio de estado

Esta matriz relaciona requisitos con código, documentación y evidencia ejecutada. La instalación limpia y las pruebas funcionales se hicieron en un esquema MySQL temporal aislado. Ese esquema y los roles temporales se eliminaron al terminar; la base local de trabajo no se modificó.

- ✅ Implementado y verificado con evidencia disponible.
- 🟡 Implementado, pero con alguna verificación o evidencia pendiente.
- 🔴 Pendiente.

| ID | Requisito | Implementación y evidencia | Estado |
|---|---|---|---|
| RQ-01 | Modelo relacional normalizado hasta 3FN | `sql/ddl/01_schema.sql`; `docs/entrega-2/normalizacion.md` | ✅ Documentado |
| RQ-02 | Mínimo 8 entidades principales | SUCURSAL, EMPLEADO, CLIENTE, CATEGORIA, PRODUCTO, PROVEEDOR, COMPRA y VENTA; 50 filas verificadas por entidad | ✅ |
| RQ-03 | Relaciones N:M | DETALLE_COMPRA y DETALLE_VENTA relacionan compras/ventas con productos | ✅ |
| RQ-04 | Restricciones de integridad | PK, FK, UNIQUE, NOT NULL y CHECK en `sql/ddl/01_schema.sql` | ✅ |
| RQ-05 | Mínimo 50 registros por entidad principal | `01_seed_data.sql` + `02_bulk_data.sql`; se verificaron 50 filas en las ocho entidades y las dos tablas de detalle | ✅ |
| RQ-06 | Vistas SQL de negocio | Las tres vistas de `sql/views/01_views.sql` se crearon en la instalación limpia | ✅ |
| RQ-07 | Trigger que valida stock de venta | `trg_validar_stock_venta`; la prueba CP08 rechazó el exceso y revirtió la operación | ✅ |
| RQ-08 | Trigger que descuenta stock | `trg_descontar_stock_venta`; CP07 verificó el descuento de dos unidades | ✅ |
| RQ-09 | Procedimiento para registrar ventas | `sp_registrar_venta`; invocado desde Flask y validado con CP07 y CP08 | ✅ |
| RQ-10 | Procedimiento para registrar compras | `sp_registrar_compra`; validado desde Compras Web, incluyendo aumento de stock y actualización de costo | ✅ |
| RQ-11 | Tres roles MySQL | `rol_administrador`, `rol_ventas`, `rol_bodega` en `sql/security/01_roles.sql` | ✅ |
| RQ-12 | Privilegios diferenciados por rol MySQL | GRANT por tablas y EXECUTE por procedimiento en `sql/security/01_roles.sql`; roles y privilegios revisados en MySQL | ✅ |
| RQ-13 | Inicio de sesión con contraseña hash | Verificación PBKDF2, login válido e inválido en CP01 y CP02 | ✅ |
| RQ-14 | Protección de rutas | Decorador `requiere_rol` en `web/app.py`; rutas protegidas por sesión y cargo | ✅ |
| RQ-15 | Control por cargo en Flask | CP03/CP04 y rutas de Compras/Ventas/Proveedores verificaron HTTP 200 y 403 según rol | ✅ |
| RQ-16 | CRUD de Productos | Alta, edición y baja lógica persistidas en MySQL temporal; CP05 | ✅ |
| RQ-17 | CRUD de Clientes | Alta, edición y baja lógica persistidas en MySQL temporal; CP06 | ✅ |
| RQ-18 | Baja lógica | `estado = 0` verificado para Productos, Clientes y Proveedores | ✅ |
| RQ-19 | Consultas parametrizadas | Consultas de Flask usan placeholders `%s`; `web/app.py` y `web/db.py` | ✅ |
| RQ-20 | Protección y ejemplo de configuración sensible | `.env` excluido por `.gitignore`; `.env.example` contiene solo valores de ejemplo | ✅ |
| RQ-21 | Guía de instalación | `INSTALL.md` incluye orden de scripts, credenciales iniciales y nota de migraciones; se comprobó en esquema limpio | ✅ |
| RQ-22 | Ocho casos de prueba documentados | CP01–CP08 aprobados en `docs/casos-prueba/CASOS_PRUEBA_ENTREGA_3.md` | ✅ |
| RQ-23 | Módulo web de Ventas | Lista y registro con `sp_registrar_venta`; CP07 y CP08 | ✅ |
| RQ-24 | Módulo web de Compras | Lista y registro con `sp_registrar_compra`; persistencia, stock y costo verificados | ✅ |
| RQ-25 | CRUD web de Proveedores | Alta, edición, listado y baja lógica probados en MySQL temporal | ✅ |
| RQ-26 | Aplicación con avance aproximado de 70% | Estimación y alcance descritos en `docs/entrega-3/AVANCE_WEB_ENTREGA_3.md` | ✅ Estimación documentada |
| RQ-27 | Documento AVANCE_WEB de Entrega 3 | `docs/entrega-3/AVANCE_WEB_ENTREGA_3.md` | ✅ |
| RQ-28 | Bitácora IA de Entrega 3 | `docs/bitacora-ia/BITACORA_IA_ENTREGA_3.md` | ✅ |
| RQ-29 | Certificación de calidad de Entrega 3 | `docs/certificaciones/CERTIFICACION_ENTREGA_3.md` | ✅ |

## Evidencia de instalación limpia

Se ejecutaron en orden los archivos indicados en `INSTALL.md`, usando una copia temporal de los nombres de esquema y de los roles para aislar la prueba. Se comprobó:

- 50 filas en SUCURSAL, EMPLEADO, CLIENTE, CATEGORIA, PRODUCTO, PROVEEDOR, COMPRA y VENTA.
- 50 filas en DETALLE_COMPRA y DETALLE_VENTA.
- 3 vistas, 2 triggers y 2 procedimientos creados.
- Creación de roles y GRANT del script de seguridad.
- Ejecución de CP01–CP08 y comprobaciones adicionales de CRUD de Proveedores y Compras Web.

El esquema temporal y los roles temporales se eliminaron después de la verificación. No se ejecutó `01_schema.sql` sobre `comercial_estuardo_db`.

## Resumen

La instalación desde cero y los ocho casos funcionales pasaron en un entorno temporal. Quedan como trabajo posterior las mejoras que exceden el alcance actual, como compras o ventas con varios productos por operación, reportes adicionales y despliegue fuera del entorno local.
