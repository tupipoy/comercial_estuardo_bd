# CASOS DE PRUEBA — ENTREGA 3

## Proyecto

**Sistema de Gestión de Inventarios y Ventas — Comercial Estuardo**

## Objetivo

Documentar las pruebas funcionales y de seguridad de la base de datos y la aplicación web correspondientes a la Entrega 3, indicando cuáles se ejecutaron y cuáles siguen pendientes.

## Entorno de prueba

- Aplicación Flask con MySQL local.
- Usuarios de prueba creados en `EMPLEADO` con hashes PBKDF2:
  - `ventas@comercialestuardo.com` — cargo `Vendedor`.
  - `bodega@comercialestuardo.com` — cargo `Bodega`.
- Se aplicó `sql/migrations/03_add_product_cost.sql` porque la ruta de productos requiere `PRODUCTO.precio_costo`.

---

## CP01 — Inicio de sesión correcto

**Objetivo:** Verificar que un empleado activo con credenciales válidas pueda iniciar sesión.

**Precondiciones:** El empleado existe, tiene `estado = 1` y `password_hash` válido.

**Datos de prueba:** Se inició sesión con las cuentas de prueba de Vendedor y Bodega usando sus contraseñas correspondientes.

**Procedimiento:** Abrir el login, ingresar correo y contraseña válidos y enviar el formulario.

**Resultado esperado:** Se crea la sesión y la aplicación redirige a Inventario.

**Resultado obtenido:** Ambos inicios de sesión devolvieron redirección HTTP `302` y guardaron el cargo esperado en la sesión.

**Estado:** ✅ Aprobado

---

## CP02 — Inicio de sesión incorrecto

**Objetivo:** Comprobar que el sistema rechace una contraseña incorrecta.

**Precondiciones:** El usuario existe en `EMPLEADO`.

**Datos de prueba:** Usuario válido y contraseña incorrecta.

**Procedimiento:** Enviar el formulario de login con la contraseña incorrecta.

**Resultado esperado:** El sistema rechaza el acceso, muestra un mensaje de credenciales incorrectas y no crea una sesión autenticada.

**Resultado obtenido:** Pendiente de prueba con MySQL local.

**Estado:** ⏳ Pendiente

---

## CP03 — Restricción de Productos para Vendedor

**Objetivo:** Verificar que un empleado con cargo `Vendedor` no pueda acceder a Productos.

**Precondiciones:** Existe un Vendedor activo y autenticado.

**Procedimiento:** Iniciar sesión como Vendedor, comprobar el menú e intentar abrir `/productos` directamente.

**Resultado esperado:** Inventario y Clientes son accesibles; Productos no aparece en el menú y la ruta responde HTTP `403`.

**Resultado obtenido:** Inventario y Clientes respondieron HTTP `200`; `/productos` respondió HTTP `403`; el enlace de Productos no apareció en el menú.

**Estado:** ✅ Aprobado

---

## CP04 — Restricción de Clientes para Bodega

**Objetivo:** Verificar que un empleado con cargo `Bodega` no pueda acceder a Clientes.

**Precondiciones:** Existe un usuario de Bodega activo y autenticado.

**Procedimiento:** Iniciar sesión como Bodega, comprobar el menú e intentar abrir `/clientes` directamente.

**Resultado esperado:** Inventario y Productos son accesibles; Clientes no aparece en el menú y la ruta responde HTTP `403`.

**Resultado obtenido:** Inventario y Productos respondieron HTTP `200`; `/clientes` respondió HTTP `403`; el enlace de Clientes no apareció en el menú.

**Estado:** ✅ Aprobado

---

## CP05 — Crear producto

**Objetivo:** Comprobar que un usuario autorizado pueda registrar un producto y que persista en MySQL.

**Precondiciones:** Usuario Administrador o Bodega y al menos una categoría activa.

**Procedimiento:** Iniciar sesión, abrir Productos, crear un producto y consultar el registro en MySQL.

**Consulta de verificación:**

```sql
SELECT *
FROM PRODUCTO
ORDER BY id_producto DESC
LIMIT 1;
```

**Resultado esperado:** El producto aparece en la interfaz y en MySQL con `estado = 1`.

**Resultado obtenido:** La ruta CRUD se verificó con conexión simulada; falta probar la creación con persistencia en MySQL real.

**Estado:** ⏳ Pendiente

---

## CP06 — Crear cliente

**Objetivo:** Verificar que un usuario autorizado pueda registrar clientes y que los datos persistan en MySQL.

**Precondiciones:** Usuario Administrador o Vendedor.

**Procedimiento:** Iniciar sesión, abrir Clientes, crear un cliente y consultar la tabla.

**Consulta de verificación:**

```sql
SELECT *
FROM CLIENTE
ORDER BY id_cliente DESC
LIMIT 1;
```

**Resultado esperado:** El cliente aparece en el listado y persiste en la base de datos.

**Resultado obtenido:** La ruta CRUD se verificó con conexión simulada; falta probar la creación con persistencia en MySQL real.

**Estado:** ⏳ Pendiente

---

## CP07 — Venta con stock suficiente

**Objetivo:** Comprobar que una venta válida pueda registrarse y que el inventario se actualice.

**Precondiciones:** Existen producto con stock suficiente, cliente, empleado y sucursal válidos; también están creados `sp_registrar_venta`, `trg_validar_stock_venta` y `trg_descontar_stock_venta`.

**Procedimiento:** En una base de pruebas, consultar el stock, registrar una venta con el procedimiento y volver a consultar el stock, la venta y el detalle. Sustituir los IDs de ejemplo por IDs existentes y usar un número de factura único.

```sql
SELECT id_producto, nombre, stock_actual
FROM PRODUCTO
WHERE id_producto = 1;

CALL sp_registrar_venta(
    'PRUEBA', 9001, 'Efectivo',
    1, 1, 1, 1, 2, 100.00, 0.00
);

SELECT id_producto, nombre, stock_actual
FROM PRODUCTO
WHERE id_producto = 1;

SELECT * FROM VENTA ORDER BY id_venta DESC LIMIT 1;
SELECT * FROM DETALLE_VENTA ORDER BY id_detalle_venta DESC LIMIT 1;
```

**Resultado esperado:** Se crean cabecera y detalle, el total coincide y el stock baja en dos unidades.

**Resultado obtenido:** Pendiente de ejecutar contra MySQL. No se ejecutó esta operación porque modifica inventario y genera una venta.

**Estado:** ⏳ Pendiente

---

## CP08 — Venta con stock insuficiente

**Objetivo:** Verificar que no se registre una venta superior al stock disponible.

**Precondiciones:** Producto existente y activos el trigger `trg_validar_stock_venta` y el procedimiento `sp_registrar_venta`.

**Procedimiento:** En una base de pruebas y usando IDs válidos, intentar vender una cantidad mayor al stock:

```sql
CALL sp_registrar_venta(
    'PRUEBA', 9002, 'Efectivo',
    1, 1, 1, 1, 99999, 100.00, 0.00
);
```

**Resultado esperado:** MySQL informa que el stock es insuficiente, la transacción se revierte y no queda una venta incompleta.

**Mensaje esperado:**

```text
Stock insuficiente para realizar la venta
```

**Resultado obtenido:** Pendiente de ejecutar contra MySQL.

**Estado:** ⏳ Pendiente

---

# Resumen de resultados

| Código | Caso de prueba | Resultado |
|---|---|---|
| CP01 | Login correcto | ✅ Aprobado |
| CP02 | Login incorrecto | ⏳ Pendiente |
| CP03 | Restricción de Productos para Vendedor | ✅ Aprobado |
| CP04 | Restricción de Clientes para Bodega | ✅ Aprobado |
| CP05 | Crear producto con persistencia MySQL | ⏳ Pendiente |
| CP06 | Crear cliente con persistencia MySQL | ⏳ Pendiente |
| CP07 | Venta con stock suficiente | ⏳ Pendiente |
| CP08 | Venta con stock insuficiente | ⏳ Pendiente |

## Conclusión

Se comprobó el inicio de sesión de los usuarios de prueba y el control de acceso por cargo en las rutas de Inventario, Productos y Clientes. Las pruebas de login incorrecto, persistencia real de los CRUD y transacciones de ventas todavía deben ejecutarse antes de declarar esos casos aprobados.
