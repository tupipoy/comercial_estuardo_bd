# Manual de usuario — Entrega 4

**Sistema:** Gestión de Ventas, Compras e Inventario — Comercial Estuardo
**Versión:** Borrador de trabajo para Entrega 4

## Acceso

1. Abrir [Comercial Estuardo en Railway](https://comercialestuardobd-production.up.railway.app) o `http://localhost:5050` en desarrollo.
2. Ingresar correo o CUI y contraseña habilitados por el administrador.
3. El menú disponible depende del cargo asignado: Administrador, Vendedor o Bodega.
4. Para salir, seleccionar **Cerrar sesión**.

## Resumen del inventario

Al iniciar sesión se abre el resumen con el total de productos activos, referencias bajo mínimo, productos agotados y operaciones de compra/venta del período seleccionado. El valor del inventario solo se muestra cuando los productos con existencias tienen un costo registrado mayor que cero. La distribución por categoría y la lista de alertas se calculan con el catálogo actual. En teléfonos, usa la barra inferior y **Más** para navegar los demás módulos habilitados por tu cargo.

## Inventario

Abrir **Inventario** para consultar productos activos, categoría, precio y existencias. Vendedores ven las cantidades de su sucursal asignada. Bodega puede cambiar entre **Inventario local**, que muestra el stock de su sucursal, e **Inventario general**, que permite consultar el stock por producto y sucursal sin modificarlo. El Administrador puede cambiar entre **Consolidado**, que suma las existencias, y **Por sucursal**, que detalla las cantidades en cada ubicación y permite abrir la edición del producto. En el inventario general se puede filtrar por sucursal. Usar el campo de búsqueda para filtrar por nombre, código o categoría. El filtro de stock bajo se puede combinar con la búsqueda para localizar existencias críticas de un producto o categoría.

## Productos

Los usuarios autorizados pueden consultar, buscar por nombre, código o categoría, crear, editar y desactivar productos. El catálogo es compartido: el Administrador puede editar cualquiera y sus datos descriptivos y precios aplican a todas las sucursales. Bodega ve en este catálogo el stock local; para consultar las demás debe usar **Inventario general**. Antes de guardar, completar los campos obligatorios y seleccionar una categoría activa. El precio de venta debe ser igual o mayor que el costo; además, el sistema no permite aplicar un descuento que deje una línea de venta por debajo de su costo. La desactivación conserva el historial y oculta el producto de los listados operativos.

## Clientes

Los usuarios autorizados pueden consultar y buscar clientes por nombre, NIT, CUI o correo, además de crear, editar y desactivar sus registros. El NIT es obligatorio; el CUI es opcional. NIT y CUI deben ser únicos cuando se proporcionen.

## Proveedores

Administrador y Bodega pueden consultar proveedores aprobados, buscar por razón social, NIT o contacto y seleccionarlos en compras cuando estén activos. Ambos perfiles pueden usar **Proponer proveedor**; se requiere NIT, razón social y teléfono. La propuesta queda pendiente y todavía no aparece en Compras.

En **Propuestas**, Administración revisa todas las solicitudes, puede corregir sus datos y aprobarlas, o rechazarlas indicando el motivo. Bodega consulta sus propias propuestas y el resultado. Solo Administración puede editar proveedores aprobados o desactivarlos. La desactivación conserva las compras históricas. Se puede consultar el catálogo de activos e inactivos; las propuestas pendientes también aparecen como alerta administrativa.

| Acción | Bodega | Administrador |
|---|---|---|
| Consultar proveedores | Sí | Sí |
| Seleccionarlos en compras | Sí | Sí |
| Proponer un proveedor nuevo | Sí | Sí |
| Aprobarlo y modificar sus datos | No | Sí |
| Desactivarlo | No | Sí |

## Administración (Administrador)

El Administrador (perfil de gerencia en este sistema) dispone además de **Categorías**, **Sucursales** y **Empleados**. En cada catálogo puede consultar, crear, editar y desactivar registros. Desde cada documento puede registrar una devolución parcial o anular todo lo pendiente, indicando un motivo. El original y sus líneas se conservan; el Vendedor puede consultar e imprimir. Antes de desactivar una categoría, desactiva los productos que aún estén activos en ella; antes de desactivar una sucursal, reasigna o desactiva sus empleados activos. Esto conserva las relaciones históricas. Al crear un empleado, se asigna una contraseña inicial de al menos 10 caracteres; al editarlo, la contraseña se puede dejar vacía para conservar la existente. El sistema guarda contraseñas como hash.

## Ventas

Los usuarios autorizados pueden consultar ventas, filtrarlas por factura, cliente, empleado o rango de fechas, abrir **Ver factura** para revisar sus líneas y registrar una venta seleccionando cliente y forma de pago, y agregando una o más líneas de producto. Para cada línea se indica cantidad y descuento; para motocicletas se selecciona una unidad ya identificada por VIN/chasis y motor. El inventario disponible se valida en MySQL. Si no hay existencias suficientes, la operación completa se rechaza sin descontar stock.

## Compras

Los usuarios autorizados pueden consultar compras de su sucursal (el Administrador puede consultar todas), filtrarlas por número de orden, proveedor, empleado o rango de fechas, abrir **Ver orden** para revisar sus líneas y registrar una recepción en su sucursal, agregando una o más líneas con producto, cantidad y costo unitario. Al confirmar, el servicio transaccional almacena la compra y actualiza las existencias de esa sucursal y el costo vigente dentro de una transacción.

## Traslados entre sucursales

Administrador y Bodega pueden solicitar traslados. Bodega solo puede elegir su sucursal asignada como origen; el Administrador puede elegir cualquier origen. Selecciona una sucursal destino distinta, agrega productos y cantidades disponibles y envía la solicitud. Al aprobar, el stock se reserva y deja de estar disponible para vender; las existencias físicas cambian cuando Bodega de origen confirma el despacho. En ese momento las unidades salen del origen y quedan en tránsito. Bodega de destino registra las cantidades acumuladas que recibió y las unidades exactas; solo las nuevas cantidades recibidas se agregan a su inventario. Los faltantes permanecen como diferencias pendientes y pueden completarse después. El detalle conserva quién solicitó, aprobó, despachó y recibió, las fechas y cualquier diferencia. El historial muestra traslados de las sucursales involucradas y el Administrador puede consultar todos.

## Unidades y Kardex

En **Unidades**, consulta VIN, motor, sucursal, estado y recorrido de cada motocicleta. En Compras, registra un `VIN | MOTOR` por cada unidad recibida. En Ventas y Traslados, selecciona unidades disponibles de la sucursal; no se pueden vender las reservadas o en tránsito. Administración puede completar identidades de existencias anteriores sin alterar su cantidad.

El **Kardex** muestra entradas, salidas, reservas, responsables y saldos por sucursal, con filtros de producto y fechas. Su saldo inicial corresponde al día de activación; no reconstruye movimientos anteriores.

## Conteos, mínimos y ajustes

En **Conteos y ajustes**, selecciona sucursal y producto. Bodega registra lo encontrado y Administración autoriza o rechaza el ajuste. Para motocicletas marca las unidades encontradas y añade los VIN/motores de unidades nuevas. Si el inventario cambió desde el conteo, se requiere otro conteo. No se pueden dar de baja unidades reservadas sin resolver primero sus reservas. Administración puede definir un mínimo diferente por sucursal.

## Devoluciones y anulaciones

Administración abre **Devolución / Anulación** desde una venta o compra. Para una devolución parcial, indica cantidades y motivo; para anular, se revierte todo lo pendiente. Nunca se devuelve más de lo original menos devoluciones anteriores. Las compras solo pueden revertirse si hay stock disponible en su sucursal y, para motocicletas, unidades exactas procedentes de esa compra. Los documentos muestran el importe original y el neto después de reversos.

## Alertas y respaldos

**Alertas** reúne mínimos de stock, traslados por autorizar, reservas por despachar, recepciones pendientes y unidades sin identificar. Administración también ve el estado del respaldo. **Respaldos** registra copias diarias cifradas, restauraciones verificadas y un enlace a su descarga. La recuperación está documentada en `docs/operaciones/RESPALDOS.md`.

## Mensajes y problemas comunes

- **Credenciales incorrectas:** confirmar correo/CUI y solicitar al administrador que habilite la cuenta.
- **No autorizado:** solicitar el cargo correcto; no intentar acceder con una URL directa.
- **Error al guardar:** confirmar que la conexión a MySQL esté disponible y que los datos requeridos sean válidos.
- **Stock insuficiente:** reducir la cantidad o registrar la recepción de compra correspondiente.


## Corrección de cabeceras

Administración puede abrir **Corregir cabecera** desde una compra o venta vigente. En ventas corrige cliente o forma de pago; en compras, proveedor o número de orden. Debe indicar un motivo. El sistema conserva las versiones anterior y nueva, responsable y fecha. Las cantidades, importes, sucursal y líneas permanecen sin cambios; para cantidades utiliza Devolución / Anulación. Los documentos anulados no se corrigen.

## Alcance de la verificación

La instalación y los flujos se comprobaron con formularios y sesiones reales del cliente Flask sobre MySQL temporal. La evidencia está en los casos de Entrega 4. Los integrantes deben revisar la presentación visual en su navegador y practicar la defensa con los datos de demostración.
