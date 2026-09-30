# CASOS DE PRUEBA — ENTREGA 3

## Proyecto

**Sistema de Gestión de Inventarios y Ventas — Comercial Estuardo**

## Objetivo

Documentar las pruebas funcionales y de seguridad de la base de datos y la aplicación web correspondientes a la Entrega 3, indicando cuáles se ejecutaron y cuáles siguen pendientes.

## Entorno de prueba

- Instalación completa de Flask y MySQL en un esquema temporal independiente, creada con los siete scripts en el orden indicado en `INSTALL.md`.
- Se asignaron hashes PBKDF2 temporales a los empleados Administrador, Vendedor y Bodega del conjunto de datos.
- La prueba no aplicó migraciones: `password_hash` y `precio_costo` ya existen en el DDL actual.
- El esquema y los roles temporales se eliminaron al terminar; no se modificó la base local de trabajo.

---

## CP01 — Inicio de sesión correcto

**Objetivo:** Verificar que un empleado activo con credenciales válidas pueda iniciar sesión.

**Precondiciones:** El empleado existe, tiene `estado = 1` y `password_hash` válido.

**Datos de prueba:** Se inició sesión con las cuentas temporales de Administrador, Vendedor y Bodega usando una contraseña válida de prueba.

**Procedimiento:** Abrir el login, ingresar correo y contraseña válidos y enviar el formulario.

**Resultado esperado:** Se crea la sesión y la aplicación redirige a Inventario.

**Resultado obtenido:** Las tres cuentas devolvieron redirección HTTP `302` a Inventario y permitieron comprobar sus respectivos cargos y permisos.

**Estado:** ✅ Aprobado

---

## CP02 — Inicio de sesión incorrecto

**Objetivo:** Comprobar que el sistema rechace una contraseña incorrecta.

**Precondiciones:** El usuario existe en `EMPLEADO`.

**Datos de prueba:** Usuario válido y contraseña incorrecta.

**Procedimiento:** Enviar el formulario de login con la contraseña incorrecta.

**Resultado esperado:** El sistema rechaza el acceso, muestra un mensaje de credenciales incorrectas y no crea una sesión autenticada.

**Resultado obtenido:** El login respondió HTTP `200`, mostró el mensaje de credenciales incorrectas y no creó `user_id` en la sesión.

**Estado:** ✅ Aprobado

---

## CP03 — Restricción de Productos para Vendedor

**Objetivo:** Verificar que un empleado con cargo `Vendedor` no pueda acceder a Productos.

**Precondiciones:** Existe un Vendedor activo y autenticado.

**Procedimiento:** Iniciar sesión como Vendedor, comprobar el menú e intentar abrir `/productos` directamente.

**Resultado esperado:** Inventario y Clientes son accesibles; Productos no aparece en el menú y la ruta responde HTTP `403`.

**Resultado obtenido:** Inventario, Clientes y Ventas respondieron HTTP `200`; `/productos` y `/compras` respondieron HTTP `403`; el menú omitió Productos.

**Estado:** ✅ Aprobado

---

## CP04 — Restricción de Clientes para Bodega

**Objetivo:** Verificar que un empleado con cargo `Bodega` no pueda acceder a Clientes.

**Precondiciones:** Existe un usuario de Bodega activo y autenticado.

**Procedimiento:** Iniciar sesión como Bodega, comprobar el menú e intentar abrir `/clientes` directamente.

**Resultado esperado:** Inventario y Productos son accesibles; Clientes no aparece en el menú y la ruta responde HTTP `403`.

**Resultado obtenido:** Inventario, Productos, Compras y Proveedores respondieron HTTP `200`; `/clientes` y `/ventas` respondieron HTTP `403`; el menú omitió Clientes.

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

**Resultado esperado:** El producto aparece en la interfaz y en MySQL con `estado = 1`; la edición persiste y la desactivación cambia su estado a `0`.

**Resultado obtenido:** En MySQL temporal se creó el producto, se verificaron los datos persistidos, se editó y se desactivó lógicamente. Cada operación respondió como se esperaba.

**Estado:** ✅ Aprobado

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

**Resultado esperado:** El cliente aparece en el listado y persiste en la base de datos; la edición y desactivación lógica también se guardan.

**Resultado obtenido:** En MySQL temporal se creó el cliente, se verificaron los datos persistidos, se editó y se desactivó lógicamente. Cada operación respondió como se esperaba.

**Estado:** ✅ Aprobado

---

## CP07 — Venta con stock suficiente

**Objetivo:** Comprobar que una venta válida pueda registrarse y que el inventario se actualice.

**Precondiciones:** Existen producto con stock suficiente, cliente, empleado y sucursal válidos; también están creados `sp_registrar_venta`, `trg_validar_stock_venta` y `trg_descontar_stock_venta`.

**Procedimiento:** En el esquema temporal completo, iniciar sesión como Vendedor, consultar el stock del producto 1 y registrar una venta de dos unidades desde `/ventas/nueva`. Después consultar la cabecera, el detalle y el stock en MySQL.

**Resultado esperado:** Se crean cabecera y detalle, el total coincide y el stock baja en dos unidades.

**Resultado obtenido:** La ruta web respondió HTTP `302`; se guardaron la cabecera y el detalle, y el stock bajó exactamente dos unidades mediante el trigger.

**Estado:** ✅ Aprobado

---

## CP08 — Venta con stock insuficiente

**Objetivo:** Verificar que no se registre una venta superior al stock disponible.

**Precondiciones:** Producto existente y activos el trigger `trg_validar_stock_venta` y el procedimiento `sp_registrar_venta`.

**Procedimiento:** En el esquema temporal, iniciar sesión como Vendedor e intentar registrar por la web una cantidad mayor que el stock disponible.

**Resultado esperado:** MySQL informa que el stock es insuficiente, la transacción se revierte y no queda una venta incompleta.

**Mensaje esperado:**

```text
Stock insuficiente para realizar la venta
```

**Resultado obtenido:** La aplicación mostró “Stock insuficiente”. La transacción no dejó una cabecera de venta y el stock quedó sin cambios.

**Estado:** ✅ Aprobado

---

## Verificaciones adicionales

En el mismo entorno temporal se probó el CRUD de Proveedores y el registro de una compra como Bodega. La compra quedó persistida y `sp_registrar_compra` incrementó el stock en dos unidades y actualizó `precio_costo` al valor enviado. El listado y las rutas de Compras/Proveedores también respetaron los permisos.

---

# Resumen de resultados

| Código | Caso de prueba | Resultado |
|---|---|---|
| CP01 | Login correcto | ✅ Aprobado |
| CP02 | Login incorrecto | ✅ Aprobado |
| CP03 | Restricción de Productos para Vendedor | ✅ Aprobado |
| CP04 | Restricción de Clientes para Bodega | ✅ Aprobado |
| CP05 | CRUD de Producto con persistencia MySQL | ✅ Aprobado |
| CP06 | CRUD de Cliente con persistencia MySQL | ✅ Aprobado |
| CP07 | Venta con stock suficiente | ✅ Aprobado |
| CP08 | Venta con stock insuficiente | ✅ Aprobado |

## Conclusión

Los ocho casos se ejecutaron y aprobaron en una instalación temporal completa de MySQL. Se verificaron la autenticación válida e inválida, los permisos por cargo, la persistencia CRUD de Productos y Clientes, y las transacciones de venta con stock suficiente e insuficiente. Las pruebas no alteraron la base de datos local de trabajo.
