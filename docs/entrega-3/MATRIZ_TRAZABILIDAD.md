# MATRIZ DE TRAZABILIDAD — ENTREGA 3

## Proyecto

**Sistema de Gestión de Inventarios y Ventas — Comercial Estuardo**

## Objetivo

Relacionar los requisitos del proyecto con su implementación técnica y la evidencia disponible. La matriz distingue los archivos preparados de los objetos instalados y las pruebas ejecutadas en la base local.

## Estados

- ✅ Implementado y verificado.
- 🟡 Implementado, con verificación o despliegue pendiente.
- 🔴 Pendiente de implementación.

| ID | Requisito | Implementación | Archivo / evidencia | Estado |
|---|---|---|---|---|
| RQ-01 | Modelo relacional normalizado hasta 3FN | Diseño relacional y documentación de normalización | `sql/ddl/01_schema.sql`; `docs/entrega-2/normalizacion.md` | ✅ Documentado |
| RQ-02 | Mínimo 8 entidades principales | SUCURSAL, EMPLEADO, CLIENTE, CATEGORIA, PRODUCTO, PROVEEDOR, COMPRA y VENTA | `sql/ddl/01_schema.sql` | ✅ Definidas |
| RQ-03 | Relaciones N:M | COMPRA–PRODUCTO se representa con DETALLE_COMPRA y VENTA–PRODUCTO con DETALLE_VENTA | `sql/ddl/01_schema.sql` | ✅ Definidas |
| RQ-04 | Restricciones de integridad | PK, FK, UNIQUE, NOT NULL y CHECK | `sql/ddl/01_schema.sql` | ✅ Definidas |
| RQ-05 | Mínimo 50 registros por entidad principal | Seed y carga masiva preparados; la carga masiva aún no está en la base local | `sql/dml/01_seed_data.sql`; `sql/dml/02_bulk_data.sql` | 🟡 Scripts listos; falta ejecutar y verificar en instalación limpia |
| RQ-06 | Vistas SQL de negocio | Inventario valorizado, stock crítico y ventas detalladas | `sql/views/01_views.sql` | 🟡 Script listo; no aparecen instaladas en la base local |
| RQ-07 | Trigger para validar stock | Rechaza el detalle de venta si no hay existencias suficientes | `sql/triggers/01_triggers.sql` | 🟡 Script listo; no aparece instalado ni probado en la base local |
| RQ-08 | Trigger para descontar stock | Descuenta existencias al insertar detalle de venta | `sql/triggers/01_triggers.sql` | 🟡 Script listo; no aparece instalado ni probado en la base local |
| RQ-09 | Procedimiento para registrar venta | Registra cabecera y detalle en transacción y depende de los triggers de venta | `sql/procedimiento/01_procedures.sql`; metadata `information_schema.ROUTINES` | 🟡 Instalado; falta probar una venta y su reversión |
| RQ-10 | Procedimiento para registrar compra | Registra compra y detalle, aumenta stock y actualiza costo | `sql/procedimiento/01_procedures.sql`; metadata `information_schema.ROUTINES` | 🟡 Instalado; falta probar persistencia y actualización |
| RQ-11 | Tres roles MySQL | `rol_administrador`, `rol_ventas`, `rol_bodega` | `sql/security/01_roles.sql`; `SHOW GRANTS` en MySQL | ✅ Roles presentes |
| RQ-12 | Privilegios diferenciados | Administrador con acceso amplio; ventas y bodega con permisos distintos y ejecución de sus procedimientos | `sql/security/01_roles.sql`; salida `SHOW GRANTS` | ✅ Verificados en MySQL |
| RQ-13 | Inicio de sesión con contraseña hash | Werkzeug verifica `password_hash` y Flask crea sesión | `web/app.py`; empleados de prueba con hashes PBKDF2 | 🟡 Login correcto verificado; falta probar contraseña incorrecta |
| RQ-14 | Protección de rutas | Las rutas de módulos exigen sesión y cargo permitido | `web/app.py`, decorador `requiere_rol` | ✅ Implementado; control por cargo probado |
| RQ-15 | Control por cargo en Flask | Administrador accede a los tres módulos; Vendedor y Bodega tienen accesos distintos | `web/app.py`; plantillas; prueba Flask contra MySQL local | ✅ Verificado: rutas permitidas HTTP 200 y prohibidas HTTP 403 |
| RQ-16 | CRUD de Productos | Crear, consultar, editar y desactivar lógicamente | `web/app.py`; `web/templates/productos.html`; `web/templates/producto_form.html` | 🟡 Implementado; creación/edición/baja con persistencia real pendientes |
| RQ-17 | CRUD de Clientes | Crear, consultar, editar y desactivar lógicamente | `web/app.py`; `web/templates/clientes.html`; `web/templates/cliente_form.html` | 🟡 Implementado; creación/edición/baja con persistencia real pendientes |
| RQ-18 | Baja lógica | Productos y clientes se actualizan a `estado = 0` | Rutas `desactivar_producto` y `desactivar_cliente` en `web/app.py` | 🟡 Implementada; falta validar cambios en MySQL |
| RQ-19 | Consultas parametrizadas | Consultas Flask usan placeholders `%s` | `web/app.py`; `web/db.py` | ✅ Implementado |
| RQ-20 | Protección de variables sensibles | `.env` está excluido por `.gitignore`; no hay `.env.example` en el repositorio | `.gitignore`; `web/db.py` | 🟡 Exclusión implementada; falta agregar plantilla de configuración |
| RQ-21 | Guía de instalación | Instrucciones de instalación y configuración | `INSTALL.md` | ✅ Disponible |
| RQ-22 | Casos de prueba documentados | Ocho casos documentados; CP01, CP03 y CP04 aprobados; los demás pendientes | `docs/casos-prueba/CASOS_PRUEBA_ENTREGA_3.md` | 🟡 Parcial; 3 aprobados y 5 pendientes |
| RQ-23 | Módulo web de Ventas | Interfaz para registrar y consultar ventas | Pendiente | 🔴 Pendiente |
| RQ-24 | Módulo web de Compras | Interfaz para registrar y consultar compras | Pendiente | 🔴 Pendiente |
| RQ-25 | Módulo web de Proveedores | CRUD de proveedores | Pendiente | 🔴 Pendiente |
| RQ-26 | Avance web aproximado del 70% | Medición del avance funcional frente a la rúbrica | Sin evidencia de medición | 🔴 Pendiente de evaluar |
| RQ-27 | AVANCE_WEB de Entrega 3 | Documento actualizado para esta fase | Pendiente | 🔴 Pendiente |
| RQ-28 | Bitácora IA de Entrega 3 | Registro de uso y validación de herramientas IA | Pendiente | 🔴 Pendiente |
| RQ-29 | Certificación de calidad de Entrega 3 | Certificación revisada y firmada | Pendiente | 🔴 Pendiente |

## Evidencia de estado de MySQL

En la base local se comprobó que existen `sp_registrar_venta`, `sp_registrar_compra` y los tres roles. `SHOW GRANTS` confirmó los privilegios diferenciados y el permiso `EXECUTE` para ventas y bodega. La consulta a `information_schema` no encontró vistas ni triggers instalados.

La migración `sql/migrations/03_add_product_cost.sql` se aplicó a la base local para que la ruta de Productos encuentre `precio_costo`. Los scripts `01_seed_data.sql` y `02_bulk_data.sql` se mantienen separados; el bulk está preparado para una instalación limpia y no se ha cargado en la base local.

## Resumen

### Implementado y verificado

- Esquema con ocho entidades principales y tablas asociativas.
- Roles MySQL y privilegios diferenciados.
- Inicio de sesión correcto de los usuarios de prueba.
- Control de acceso por cargo y menú condicionado.
- Consultas parametrizadas.

### Implementado, pendiente de verificación o instalación

- Datos de prueba para llegar a 50 registros por entidad.
- Vistas y triggers SQL.
- Comportamiento transaccional de los procedimientos.
- Persistencia real de las operaciones CRUD.
- Login con contraseña incorrecta y la mayoría de los casos de prueba.
- Plantilla `.env.example`.

### Pendientes de implementación o documentación

- Módulos web de Ventas, Compras y Proveedores.
- Evaluación del porcentaje de avance web.
- `AVANCE_WEB` de Entrega 3.
- Bitácora IA de Entrega 3.
- Certificación de calidad de Entrega 3.

## Conclusión

La matriz muestra qué requisitos tienen código o scripts disponibles y cuáles se comprobaron en la base local. Antes de declarar completa la Entrega 3, se deben instalar y probar las vistas y triggers, validar las transacciones y operaciones CRUD con MySQL, y cerrar la documentación pendiente.
