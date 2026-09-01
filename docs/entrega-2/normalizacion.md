# Justificación del Modelo Relacional y Normalización (3FN)
**Proyecto:** Sistema de Gestión de Ventas, Compras e Inventario  
**Empresa:** Comercial Estuardo  
**Documento:** Entrega 2 - Diseño Lógico y Normalización  
**Fecha:** Septiembre 2026  

---

## 1. Transformación Conceptual a Lógico
A partir del Diagrama Entidad-Relación (Notación Chen) de la Entrega 1, se derivó el modelo relacional compuesto por 10 tablas (8 entidades fuertes/débiles y 2 tablas asociativas para resolver las relaciones $N:M$):

1. **SUCURSAL** (`id_sucursal` [PK], `nombre`, `direccion`, `telefono`, `municipio`, `estado`)
2. **EMPLEADO** (`id_empleado` [PK], `cui`, `nombres`, `apellidos`, `cargo`, `telefono`, `correo`, `fecha_ingreso`, `id_sucursal` [FK], `estado`)
3. **CLIENTE** (`id_cliente` [PK], `nit`, `cui`, `nombres`, `apellidos`, `telefono`, `correo`, `direccion`, `estado`)
4. **CATEGORIA** (`id_categoria` [PK], `nombre`, `descripcion`, `estado`)
5. **PRODUCTO** (`id_producto` [PK], `codigo_barra`, `nombre`, `descripcion`, `precio_venta`, `stock_actual`, `stock_minimo`, `id_categoria` [FK], `estado`)
6. **PROVEEDOR** (`id_proveedor` [PK], `nit`, `razon_social`, `contacto`, `telefono`, `correo`, `direccion`, `estado`)
7. **COMPRA** (`id_compra` [PK], `numero_orden`, `fecha_compra`, `total_compra`, `estado_recepcion`, `id_proveedor` [FK], `id_empleado` [FK])
8. **DETALLE_COMPRA** (`id_detalle_compra` [PK], `id_compra` [FK], `id_producto` [FK], `cantidad`, `costo_unitario`, `subtotal`)
9. **VENTA** (`id_venta` [PK], `serie_factura`, `numero_factura`, `fecha_venta`, `total_venta`, `tipo_pago`, `estado`, `id_cliente` [FK], `id_empleado` [FK], `id_sucursal` [FK])
10. **DETALLE_VENTA** (`id_detalle_venta` [PK], `id_venta` [FK], `id_producto` [FK], `vin_chasis`, `numero_motor`, `cantidad`, `precio_unitario`, `descuento`, `subtotal`)

---

## 2. Demostración del Proceso de Normalización

### Primera Forma Normal (1FN)
* **Atomicidad:** Todos los atributos almacenan un único dato indivisible.
* **Eliminación de Grupos Repetitivos:** Las listas de productos dentro de compras o ventas se trasladaron a las tablas asociativas `DETALLE_COMPRA` y `DETALLE_VENTA`.
* **Identificador Único:** Cada tabla posee una clave primaria autoincremental única.

### Segunda Forma Normal (2FN)
* Cumple estrictamente con 1FN.
* Todos los atributos no clave tienen dependencia funcional completa respecto a la clave primaria. En `DETALLE_VENTA`, los atributos `precio_unitario`, `cantidad` y `subtotal` describen la transacción del ítem en esa factura específica.

### Tercera Forma Normal (3FN)
* Cumple estrictamente con 2FN.
* Se eliminaron dependencias transitivas ($X \rightarrow Y$ y $Y \rightarrow Z$).
  * En `VENTA` no se almacenan nombres ni direcciones del cliente, únicamente `id_cliente`.
  * En `PRODUCTO` no se almacena el nombre de la categoría, únicamente `id_categoria`.
  * En `EMPLEADO` no se guardan datos de la sucursal, únicamente `id_sucursal`.

---

## 3. Manejo de Trazabilidad Serializada (RF-06 / RN-06)
Para cumplir con la trazabilidad obligatoria de motocicletas vendidas sin desnormalizar la tabla `PRODUCTO`, los atributos opcionales `vin_chasis` y `numero_motor` se almacenan en `DETALLE_VENTA`. Esto permite que los repuestos e insumos se manejen por stock numérico estándar, mientras que las unidades vehiculares registran su serial único al facturarse.