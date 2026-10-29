# Casos de prueba y resultados — Entrega 4

**Fecha:** 29/10/2026. **Entorno:** Python 3.11 limpio y MySQL 8.4 aislado; no se introducen datos sintéticos en producción.
**Evidencias:** [registro de ejecución](../entrega-4/evidencias/PRUEBAS_ENTREGA4.txt), [instalación y metadatos](../entrega-4/evidencias/VERIFICACION_ENTREGA4.json), [auditoría de Git](../entrega-4/evidencias/AUDITORIA_REPOSITORIO.json).
**Suites:** 8 casos de aceptación, 12 de inventario, 7 de proveedores y 1 de cifrado: **28 pruebas automatizadas**. Los escenarios de la tabla agrupan comprobaciones de esas suites; no todos corresponden a un único método.

| ID | Escenario | Resultado / evidencia |
|---|---|---|
| CP4-01 | Instalación completa desde cero | 25 tablas, 3 vistas, 15 triggers, 8 procedimientos, 57 FK; 50 filas en las ocho entidades principales; JSON |
| CP4-02 | Login con hash real | Aceptación: login válido, sesión y datos de empleado autenticado |
| CP4-03 | CSRF en login y acciones protegidas | POST sin token devuelve 400; se consume el token renovado después de autenticarse |
| CP4-04 | Vendedor fuera de administración | Categorías, sucursales, empleados, proveedores, conteos y respaldos devuelven 403 |
| CP4-05 | CRUD de categoría | Alta, edición y baja lógica persistidas por formularios |
| CP4-06 | CRUD de sucursal | Alta, edición y baja lógica persistidas por formularios |
| CP4-07 | CRUD de empleado y hash | Alta, edición, baja y contraseña no almacenada en texto plano |
| CP4-08 | Autoprotección de cuenta administrativa | No se desactiva la cuenta en sesión; reglas de rol inspeccionadas |
| CP4-09 | Compra de dos productos | Una cabecera, dos líneas, total correcto y unidades identificadas |
| CP4-10 | Compra con VIN repetido | Rollback de cabecera, unidades y existencias; suite inventario |
| CP4-11 | Venta de dos productos | Dos líneas, total correcto, unidad vinculada y stock actualizado |
| CP4-12 | Identificación y venta de motocicleta | VIN/motor únicos en la unidad; la venta exige unidad disponible |
| CP4-13 | Stock insuficiente | El SP revierte la venta sin cabecera parcial; stock conservado |
| CP4-14 | Importe bajo costo y tipo inválido | Formulario rechaza datos y MySQL rechaza descuento bajo costo; no quedan ventas |
| CP4-15 | Logout | Sin CSRF devuelve 400; válido elimina la sesión y las rutas vuelven al login |
| CP4-16 | Railway + Gunicorn | Servicio público y endpoints protegidos; resultado de despliegue comprobado al cierre |
| CP4-17 | CRUD de cliente | Alta, edición y baja lógica persistidas en MySQL temporal |
| CP4-18 | Repuestos de Motor | Se recibe sin VIN/motor; la detección usa palabras completas de motocicletas |
| CP4-19 | Roles SQL efectivos | Tres usuarios temporales; solo Administración tiene DDL y Bodega/Ventas no modifican proveedores |
| CP4-20 | CRUD de producto | Alta, edición, baja lógica y reglas de precio verificadas |
| CP4-21 | Alcance por sucursal | Pantallas y consultas se ejecutan con los tres perfiles |
| CP4-22 | Reserva y despacho | Aprobar aparta unidades; despachar descuenta físico y libera reserva |
| CP4-23 | Concurrencia | Dos aprobaciones no sobrerreservan el inventario; una propuesta no crea dos proveedores |
| CP4-24 | Recepción parcial de traslado | Se acredita solo el incremento recibido, se conservan diferencias y no hay doble ingreso |
| CP4-25 | Conteo y ajuste | Conteo obsoleto rechazado; faltantes y nuevas unidades quedan auditados |
| CP4-26 | Proveedores por propuesta | Ambos proponen; solo Admin aprueba/edita/desactiva; pendientes no aparecen en Compras |
| CP4-27 | Recuperación y cifrado | Archivo descifrado coincide, manipulación rechazada y ejecución real de Actions restaura MySQL aislado |
| CP4-28 | Corrección, devolución y anulación | Cabeceras con auditoría, importes/stock intactos al corregir; reversos evitan devoluciones duplicadas y conservan originales |

## Comandos reproducibles

```bash
python tests/test_delivery4_acceptance.py --isolated
python tests/test_inventory_control.py --isolated
python tests/test_supplier_proposals.py --isolated
python tests/test_backup_crypto.py
```

Las suites SQL crean bases `ce_acceptance_*`; aceptación también crea roles y usuarios temporales. Se eliminan al terminar. Las credenciales se reciben por entorno y no se publican.

## Límites de la evidencia

El cliente Flask ejecuta formularios, cookies, CSRF y consultas reales, pero no renderiza un navegador. La revisión visual final en móvil/escritorio y la explicación individual deben realizarla los integrantes. No se afirma haber probado todas las combinaciones de datos posibles. Las condiciones extremas adicionales pueden ser revisadas por el catedrático.
