# Casos de prueba — Entrega 4

**Proyecto:** Sistema de Gestión de Ventas, Compras e Inventario — Comercial Estuardo  
**Estado:** Casos preparados; pendientes de ejecución en MySQL 8 y en el despliegue de aceptación Railway.

Los resultados se deben completar con fecha, entorno y evidencia real. No considerar aprobados los casos hasta ejecutar el procedimiento completo y verificar la persistencia en MySQL.

| ID | Escenario | Resultado esperado | Estado |
|---|---|---|---|
| CP4-01 | Instalación limpia con los scripts de `INSTALL.md` | Diez tablas con 50 registros por conjunto; vistas, triggers, cuatro procedimientos y roles instalados. | Pendiente MySQL |
| CP4-02 | Inicializar empleado Administrador con hash y autenticarse | Login exitoso y acceso al inventario; contraseña en BD almacenada como hash. | Pendiente MySQL |
| CP4-03 | Intentar POST sin token CSRF en login y formulario protegido | Respuesta HTTP 400 sin cambio en datos. | Verificado con Flask test client; falta evidencia integrada |
| CP4-04 | Acceder como Vendedor a administración de Categorías/Sucursales/Empleados | Respuesta HTTP 403. | Pendiente MySQL/app integrada |
| CP4-05 | Crear, editar y desactivar una Categoría | Persistencia correcta, unicidad de nombre y desactivación lógica. | Pendiente MySQL |
| CP4-06 | Crear, editar y desactivar una Sucursal | Persistencia correcta, validación telefónica y conservación del historial. | Pendiente MySQL |
| CP4-07 | Crear y editar Empleado | Contraseña nueva guardada como hash; campos únicos y rol restringido a cargos permitidos. | Pendiente MySQL |
| CP4-08 | Desactivar último Administrador o cambiar el propio cargo | Operación rechazada; queda al menos un Administrador activo. | Pendiente MySQL |
| CP4-09 | Registrar compra con dos productos distintos | Una cabecera, dos detalles, total correcto y aumento de stock/costo en ambos productos. | Pendiente MySQL |
| CP4-10 | Compra con lista vacía, línea inválida o producto repetido | Rechazo transaccional sin cabecera, detalle ni cambio de stock. | Pendiente MySQL |
| CP4-11 | Registrar venta con dos productos y stock suficiente | Una cabecera, dos detalles, total correcto y descuento de stock en ambos productos. | Pendiente MySQL |
| CP4-12 | Venta del producto de prueba 6 (categoría Motocicletas) con VIN/motor nuevos | Guarda ambos seriales únicos y cantidad igual a una unidad. | Pendiente MySQL |
| CP4-13 | Venta sin stock suficiente o con VIN/motor repetido | Operación completa revertida; stock sin cambios. | Pendiente MySQL |
| CP4-14 | Venta con descuento mayor al importe, valores fuera de rango SQL o más de 50 líneas | La app rechaza antes de persistir; se validan límites INT y DECIMAL del esquema. | Pendiente MySQL/app |
| CP4-15 | Cierre de sesión mediante POST válido e inválido | Token válido cierra sesión; sin token responde HTTP 400. | Verificado con Flask test client; falta evidencia integrada |
| CP4-16 | Publicar con Gunicorn y MySQL en Railway | Dominio público responde; login, permisos y flujos principales funcionan. | Parcialmente verificado en Railway: dominio, login, módulos y alta/edición de cliente; compras/ventas aún pendientes |
| CP4-17 | Crear y editar un cliente temporal desde el dominio Railway | El alta y el cambio persisten y aparecen en la lista. | Aprobado manualmente por el usuario; pendiente adjuntar captura |
| CP4-18 | Vender producto de categoría `Repuestos de Motor` sin seriales | No se exige VIN/motor; estos seriales se exigen solo en categorías de motocicletas. | Pendiente de desplegar la corrección y probar en Railway |

## Evidencia a adjuntar

Para cada caso, anotar versión/tag, fecha, entorno, usuario/rol, pasos, resultado observado, consultas SQL de verificación y capturas o logs sin credenciales. Ejecutar CP4-01 en un esquema desechable: `sql/ddl/01_schema.sql` elimina y recrea `comercial_estuardo_db`.
