# Informe final — Entrega 4

**Fecha de cierre técnico:** 29 de octubre de 2026, conforme a la fecha indicada por el equipo.
**Proyecto:** Sistema de Gestión de Ventas, Compras e Inventario — Comercial Estuardo.
**Integrantes:** Elvin Guillermo Miranda Gómez, 2690-24-16072; Juan Carlos Ochoa Samayoa, 2690-23-7592.
**Entrega:** repositorio público y tag `entrega-4`.
**URL:** https://comercialestuardobd-production.up.railway.app

## Solución y alcance

El sistema centraliza los ocho dominios principales: SUCURSAL, EMPLEADO, CLIENTE, CATEGORIA, PRODUCTO, PROVEEDOR, COMPRA y VENTA. Las relaciones Compra–Producto y Venta–Producto se resuelven con sus detalles. El esquema físico completo tiene 25 tablas: incorpora existencias por sucursal, unidades identificadas, reservas, traslados, movimientos, conteos, reversos, propuestas y auditoría.

La aplicación incluye los módulos de los requerimientos RF-01 a RF-12. Los catálogos tienen creación, consulta, actualización y baja lógica. Los proveedores requieren aprobación. Compras y ventas admiten alta, consulta, corrección auditada de cabeceras y anulación; las líneas se mantienen como historial y los cambios de cantidades se procesan mediante devoluciones/reversos. La restricción de edición de líneas emitidas conserva stock, totales y trazabilidad y no elimina el CRUD de las tablas principales.

## Arquitectura y transacciones

`web/db.py` separa la conexión; `web/app.py` controla autenticación, formularios y catálogos; `inventory_control.py`, `supplier_control.py` y `control_routes.py` procesan operaciones de negocio. Las consultas reciben valores mediante parámetros. Los identificadores SQL dinámicos se construyen únicamente desde listas y nombres controlados por el código.

La instalación crea 3 vistas, 15 triggers y 8 procedimientos. `sp_registrar_venta_detallada` procesa las ventas web. Los procedimientos de compra siguen disponibles y se prueban directamente; la recepción de unidades identificadas usa el servicio transaccional Python. Los procedimientos antiguos de traslado de la versión 07 no se usan desde la aplicación nueva y Bodega no tiene permiso para ejecutarlos. El flujo vigente utiliza bloqueo de filas y auditoría desde los servicios.

## Normalización y decisiones defendibles

El modelo lógico separa personas, catálogos, sucursales y transacciones para evitar repetir sus datos descriptivos. Ejemplo: una lista inicial `(factura, cliente, producto1, producto2, categoría, cantidad)` se separa en CLIENTE, VENTA, PRODUCTO, CATEGORIA y DETALLE_VENTA: se eliminan grupos repetitivos (1FN), la línea describe un producto vendido (2FN) y los datos del cliente/categoría dependen de sus propias claves (3FN).

El stock dejó de ser una columna global de PRODUCTO: depende del par `(id_sucursal,id_producto)`. VIN y motor pertenecen a UNIDAD_PRODUCTO y tienen unicidad global; una unidad devuelta puede aparecer en más de una venta histórica sin duplicar su identidad. Los totales, subtotales y snapshots de auditoría se conservan deliberadamente como datos históricos calculados transaccionalmente. Esta desnormalización controlada, sus invariantes y la interpretación del estándar S7 deben explicarse en la defensa; no se presenta como ausencia absoluta de datos derivados.

## Validación ejecutada

Se instaló la versión completa en MySQL 8.4 temporal con datos semilla y masivos, las tres configuraciones de roles y un entorno Python 3.11 nuevo con `requirements.txt`. Se verificaron 50 filas por cada entidad principal, 57 FK, objetos SQL y permisos efectivos con usuarios temporales. El entorno y los roles se eliminaron después.

La aceptación usa login real, token CSRF renovado, CRUD de catálogos, empleados, compra/venta de varias líneas, actualización auditada de cabeceras y procedimientos. Se complementa con 12 casos de inventario, 7 de proveedores y una prueba de cifrado/alteración. La evidencia y el estado exacto están en [Casos de prueba](../casos-prueba/CASOS_PRUEBA_ENTREGA_4.md) y [VERIFICACION_ENTREGA4.json](evidencias/VERIFICACION_ENTREGA4.json).

Railway utiliza Gunicorn y MySQL. Se comprobó `/health` y los nuevos endpoints protegidos. Las migraciones productivas se respaldaron y probaron primero sobre una copia. El respaldo cifrado tiene una restauración real verificada: [ejecución 40946013024](https://github.com/tupipoy/comercial_estuardo_bd/actions/runs/40946013024). Las pruebas funcionales automatizadas no reemplazan una inspección visual final en el navegador por los integrantes.

## Integridad académica y revisión del equipo

El apoyo de OpenAI Codex y las comprobaciones automáticas se documentan en las bitácoras. Los integrantes deben revisar el código entregado y explicar individualmente modelado, restricciones, SQL, roles y transacciones. Se conservan las aprobaciones que ya figuraban en la certificación; esta revisión automática no crea firmas ni acredita una defensa oral realizada.

El usuario confirmó que el equipo está formado por dos personas. El PDF permite variar el tamaño con autorización docente; no se adjuntó una constancia. La aprobación formal del ER no quedó confirmada en esta revisión y debe ser conservada por el equipo. El archivo Chen editable, que estaba vacío, fue recuperado desde el modelo incrustado en su PNG. El Chen conserva el modelo conceptual base; el relacional vigente documenta sus extensiones físicas.

## Observaciones que permanecen visibles

- S1: las tablas siguen `UPPER_SNAKE_CASE`; las columnas, `snake_case`. No se hizo un cambio masivo de nombres productivos para aparentar cumplimiento. Si se exige minúscula literal, este criterio necesita ajuste o aceptación expresa del catedrático.
- S7: importes históricos y auditoría son redundancia controlada, no datos capturados libremente; deben justificarse.
- La ratificación personal de la certificación, constancia del ER y defensa oral corresponden al equipo. No se certifica automáticamente una comprensión individual.

## Referencias

[Verificación del PDF](ENTREGA4_VERIFICACION_REQUISITOS.md) · [Trazabilidad](MATRIZ_TRAZABILIDAD_ENTREGA_4.md) · [Manual técnico](ENTREGA4_MANUAL_TECNICO.md) · [Manual de usuario](ENTREGA4_MANUAL_USUARIO.md) · [Certificación](../certificaciones/CERTIFICACION_ENTREGA_4.md).
