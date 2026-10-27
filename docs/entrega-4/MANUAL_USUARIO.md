# Manual de usuario — Entrega 4

**Sistema:** Gestión de Ventas, Compras e Inventario — Comercial Estuardo  
**Versión:** Borrador de trabajo para Entrega 4

## Acceso

1. Abrir [Comercial Estuardo en Railway](https://comercialestuardobd-production.up.railway.app) o `http://localhost:5050` en desarrollo.
2. Ingresar correo o CUI y contraseña habilitados por el administrador.
3. El menú disponible depende del cargo asignado: Administrador, Vendedor o Bodega.
4. Para salir, seleccionar **Cerrar sesión**.

## Inventario

Abrir **Inventario** para consultar productos activos, categoría, precio y existencias. Usar el campo de búsqueda para filtrar por nombre, código o categoría. El filtro de stock bajo se puede combinar con la búsqueda para localizar existencias críticas de un producto o categoría.

## Productos

Los usuarios autorizados pueden consultar, buscar por nombre, código o categoría, crear, editar y desactivar productos. Antes de guardar, completar los campos obligatorios y seleccionar una categoría activa. La desactivación conserva el historial y oculta el producto de los listados operativos.

## Clientes

Los usuarios autorizados pueden consultar y buscar clientes por nombre, NIT, CUI o correo, además de crear, editar y desactivar sus registros. El NIT es obligatorio; el CUI es opcional. NIT y CUI deben ser únicos cuando se proporcionen.

## Proveedores

Los usuarios autorizados pueden consultar y buscar proveedores por razón social, NIT o contacto, además de crear, editar y desactivar sus registros. Se requiere NIT, razón social y teléfono.

## Administración (Administrador)

El Administrador dispone además de **Categorías**, **Sucursales** y **Empleados**. En cada catálogo puede consultar, crear, editar y desactivar registros. Antes de desactivar una categoría, desactiva los productos que aún estén activos en ella; antes de desactivar una sucursal, reasigna o desactiva sus empleados activos. Esto conserva las relaciones históricas. Al crear un empleado, se asigna una contraseña inicial de al menos 10 caracteres; al editarlo, la contraseña se puede dejar vacía para conservar la existente. El sistema guarda contraseñas como hash.

## Ventas

Los usuarios autorizados pueden consultar ventas, filtrarlas por factura, cliente, empleado o rango de fechas, abrir **Ver factura** para revisar sus líneas y registrar una venta seleccionando cliente y forma de pago, y agregando una o más líneas de producto. Para cada línea se indica cantidad y descuento; para motocicletas se ingresan VIN/chasis y número de motor. El inventario disponible se valida en MySQL. Si no hay existencias suficientes, la operación completa se rechaza sin descontar stock.

## Compras

Los usuarios autorizados pueden consultar compras, filtrarlas por número de orden, proveedor, empleado o rango de fechas, abrir **Ver orden** para revisar sus líneas y registrar una recepción seleccionando proveedor y número de orden, y agregando una o más líneas con producto, cantidad y costo unitario. Al confirmar, el procedimiento almacena la compra y actualiza stock y costo vigente dentro de una transacción.

## Mensajes y problemas comunes

- **Credenciales incorrectas:** confirmar correo/CUI y solicitar al administrador que habilite la cuenta.
- **No autorizado:** solicitar el cargo correcto; no intentar acceder con una URL directa.
- **Error al guardar:** confirmar que la conexión a MySQL esté disponible y que los datos requeridos sean válidos.
- **Stock insuficiente:** reducir la cantidad o registrar la recepción de compra correspondiente.

## Funciones por validar para la versión final

Este manual describe los módulos presentes en el repositorio. Completar la revisión de cada flujo contra la versión desplegada y retirar esta nota antes de la entrega final.
