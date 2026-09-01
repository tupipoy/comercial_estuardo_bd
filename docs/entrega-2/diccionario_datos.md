# Diccionario de Datos: Sistema Comercial Estuardo
**Base de Datos:** `comercial_estuardo_db`  
**Motor de Almacenamiento:** InnoDB  
**Juego de Caracteres:** utf8mb4 / Collation: utf8mb4_unicode_ci  
**Documento:** Entrega 2 - Diccionario de Datos  
**Fecha:** Septiembre 2026  

---

## 1. Tabla: `SUCURSAL`
Almacena las sedes y puntos de venta físicos de la empresa.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Restricciones / Reglas | Descripción |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `id_sucursal` | INT | NO | PK | AUTO_INCREMENT | Clave primaria | Identificador único de sucursal |
| `nombre` | VARCHAR(100) | NO | | | NOT NULL | Nombre comercial de la sede |
| `direccion` | VARCHAR(255) | NO | | | NOT NULL | Dirección fiscal y física |
| `telefono` | VARCHAR(15) | NO | | | NOT NULL | Número telefónico de atención |
| `municipio` | VARCHAR(100) | NO | | 'San Juan Ostuncalco' | NOT NULL | Municipio de ubicación |
| `estado` | ENUM('Activo','Inactivo') | NO | | 'Activo' | NOT NULL | Estado operativo de la sucursal |

---

## 2. Tabla: `EMPLEADO`
Registra el personal administrativo, vendedores y encargados de inventario.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Restricciones / Reglas | Descripción |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `id_empleado` | INT | NO | PK | AUTO_INCREMENT | Clave primaria | Identificador del empleado |
| `cui` | VARCHAR(13) | NO | | | UNIQUE, NOT NULL | Código Único de Identificación (DPI) |
| `nombres` | VARCHAR(100) | NO | | | NOT NULL | Nombres del trabajador |
| `apellidos` | VARCHAR(100) | NO | | | NOT NULL | Apellidos del trabajador |
| `cargo` | VARCHAR(50) | NO | | | NOT NULL | Puesto asignado (Vendedor, Bodeguero, Admin) |
| `telefono` | VARCHAR(15) | YES | | NULL | | Número de contacto |
| `correo` | VARCHAR(120) | YES | | NULL | | Correo electrónico de contacto |
| `fecha_ingreso` | DATE | NO | | (CURRENT_DATE) | NOT NULL | Fecha de alta laboral |
| `id_sucursal` | INT | NO | FK | | FK -> SUCURSAL(id_sucursal) ON DELETE RESTRICT | Sucursal asignada de trabajo |
| `estado` | ENUM('Activo','Inactivo') | NO | | 'Activo' | NOT NULL | Estado laboral |

---

## 3. Tabla: `CLIENTE`
Directorio unificado de compradores y clientes registrados.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Restricciones / Reglas | Descripción |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `id_cliente` | INT | NO | PK | AUTO_INCREMENT | Clave primaria | Identificador único del cliente |
| `nit` | VARCHAR(15) | NO | | 'CF' | NOT NULL | Número de Identificación Tributaria / CF |
| `cui` | VARCHAR(13) | YES | | NULL | UNIQUE | Documento Personal de Identificación |
| `nombres` | VARCHAR(100) | NO | | | NOT NULL | Nombres del cliente |
| `apellidos` | VARCHAR(100) | NO | | | NOT NULL | Apellidos del cliente |
| `telefono` | VARCHAR(15) | YES | | NULL | | Teléfono de contacto |
| `correo` | VARCHAR(120) | YES | | NULL | | Correo para facturación |
| `direccion` | VARCHAR(255) | YES | | 'Ciudad' | | Dirección de entrega / domicilio |
| `estado` | ENUM('Activo','Inactivo') | NO | | 'Activo' | NOT NULL | Estado del registro |

---

## 4. Tabla: `CATEGORIA`
Clasificación de productos comercializados.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Restricciones / Reglas | Descripción |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `id_categoria` | INT | NO | PK | AUTO_INCREMENT | Clave primaria | Identificador de categoría |
| `nombre` | VARCHAR(80) | NO | | | UNIQUE, NOT NULL | Nombre (Motocicletas, Repuestos, etc.) |
| `descripcion` | TEXT | YES | | NULL | | Detalle general de la categoría |
| `estado` | ENUM('Activo','Inactivo') | NO | | 'Activo' | NOT NULL | Disponibilidad en catálogo |

---

## 5. Tabla: `PRODUCTO`
Catálogo general de motocicletas, repuestos, lubricantes y accesorios.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Restricciones / Reglas | Descripción |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `id_producto` | INT | NO | PK | AUTO_INCREMENT | Clave primaria | Identificador de producto |
| `codigo_barra` | VARCHAR(50) | YES | | NULL | UNIQUE | Código de barras o SKU |
| `nombre` | VARCHAR(150) | NO | | | NOT NULL | Nombre descriptivo del producto |
| `descripcion` | TEXT | YES | | NULL | | Especificaciones técnicas o cilindraje |
| `precio_venta` | DECIMAL(10,2) | NO | | | NOT NULL, CHECK (precio_venta > 0) | Precio unitario al público (Q) |
| `stock_actual` | INT | NO | | 0 | NOT NULL, CHECK (stock_actual >= 0) | Existencias actuales físicas |
| `stock_minimo` | INT | NO | | 5 | NOT NULL, CHECK (stock_minimo >= 0) | Umbral de alerta de reabastecimiento |
| `id_categoria` | INT | NO | FK | | FK -> CATEGORIA(id_categoria) ON DELETE RESTRICT | Clasificación asignada |
| `estado` | ENUM('Activo','Inactivo') | NO | | 'Activo' | NOT NULL | Estado en catálogo |

---

## 6. Tabla: `PROVEEDOR`
Directorio de importadores y distribuidores mayoristas.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Restricciones / Reglas | Descripción |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `id_proveedor` | INT | NO | PK | AUTO_INCREMENT | Clave primaria | Identificador del proveedor |
| `nit` | VARCHAR(15) | NO | | | UNIQUE, NOT NULL | NIT de la empresa proveedora |
| `razon_social` | VARCHAR(150) | NO | | | NOT NULL | Nombre o razón social |
| `contacto` | VARCHAR(100) | YES | | NULL | | Asesor de ventas asignado |
| `telefono` | VARCHAR(15) | NO | | | NOT NULL | Teléfono corporativo |
| `correo` | VARCHAR(120) | YES | | NULL | | Correo para pedidos |
| `direccion` | VARCHAR(255) | YES | | NULL | | Ubicación del proveedor |
| `estado` | ENUM('Activo','Inactivo') | NO | | 'Activo' | NOT NULL | Estado del proveedor |

---

## 7. Tabla: `COMPRA`
Encabezado de adquisiciones y órdenes de reabastecimiento.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Restricciones / Reglas | Descripción |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `id_compra` | INT | NO | PK | AUTO_INCREMENT | Clave primaria | Identificador único de compra |
| `numero_orden` | VARCHAR(50) | NO | | | UNIQUE, NOT NULL | Folio / Orden de compra fiscal |
| `fecha_compra` | DATETIME | NO | | CURRENT_TIMESTAMP | NOT NULL | Fecha y hora de transacción |
| `total_compra` | DECIMAL(12,2) | NO | | 0.00 | NOT NULL, CHECK (total_compra >= 0) | Monto consolidado de compra |
| `estado_recepcion` | ENUM('Pendiente','Recibido','Cancelado') | NO | | 'Recibido' | NOT NULL | Estado del pedido |
| `id_proveedor` | INT | NO | FK | | FK -> PROVEEDOR(id_proveedor) ON DELETE RESTRICT | Proveedor de la mercadería |
| `id_empleado` | INT | NO | FK | | FK -> EMPLEADO(id_empleado) ON DELETE RESTRICT | Empleado receptor |

---

## 8. Tabla: `DETALLE_COMPRA`
Tabla asociativa que resuelve la relación Muchos a Muchos entre `COMPRA` y `PRODUCTO`.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Restricciones / Reglas | Descripción |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `id_detalle_compra` | INT | NO | PK | AUTO_INCREMENT | Clave primaria | Identificador del ítem |
| `id_compra` | INT | NO | FK | | FK -> COMPRA(id_compra) ON DELETE CASCADE | Compra vinculada |
| `id_producto` | INT | NO | FK | | FK -> PRODUCTO(id_producto) ON DELETE RESTRICT | Producto ingresado |
| `cantidad` | INT | NO | | | NOT NULL, CHECK (cantidad > 0) | Unidades adquiridas |
| `costo_unitario` | DECIMAL(10,2) | NO | | | NOT NULL, CHECK (costo_unitario > 0) | Costo de adquisición por unidad |
| `subtotal` | DECIMAL(12,2) | NO | | | NOT NULL, CHECK (subtotal > 0) | Total por línea (`cantidad * costo_unitario`) |

---

## 9. Tabla: `VENTA`
Encabezado de facturas y transacciones comerciales de salida.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Restricciones / Reglas | Descripción |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `id_venta` | INT | NO | PK | AUTO_INCREMENT | Clave primaria | Identificador de venta |
| `serie_factura` | VARCHAR(10) | NO | | 'A' | NOT NULL | Serie de comprobante |
| `numero_factura` | VARCHAR(20) | NO | | | UNIQUE, NOT NULL | Número correlativo |
| `fecha_venta` | DATETIME | NO | | CURRENT_TIMESTAMP | NOT NULL | Fecha y hora de emisión |
| `total_venta` | DECIMAL(12,2) | NO | | 0.00 | NOT NULL, CHECK (total_venta >= 0) | Monto total a cobrar |
| `tipo_pago` | ENUM('Efectivo','Transferencia','Depósito') | NO | | 'Efectivo' | NOT NULL | Modalidad de liquidación |
| `estado` | ENUM('Completada','Anulada') | NO | | 'Completada' | NOT NULL | Estado de la venta |
| `id_cliente` | INT | NO | FK | | FK -> CLIENTE(id_cliente) ON DELETE RESTRICT | Cliente comprador |
| `id_empleado` | INT | NO | FK | | FK -> EMPLEADO(id_empleado) ON DELETE RESTRICT | Vendedor responsable |
| `id_sucursal` | INT | NO | FK | | FK -> SUCURSAL(id_sucursal) ON DELETE RESTRICT | Sucursal donde se originó |

---

## 10. Tabla: `DETALLE_VENTA`
Tabla asociativa que resuelve la relación Muchos a Muchos entre `VENTA` y `PRODUCTO`, incluyendo control serializado de vehículos.

| Campo | Tipo de Dato | Nulo | Clave | Valor por Defecto | Restricciones / Reglas | Descripción |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| `id_detalle_venta` | INT | NO | PK | AUTO_INCREMENT | Clave primaria | Identificador del ítem vendido |
| `id_venta` | INT | NO | FK | | FK -> VENTA(id_venta) ON DELETE CASCADE | Venta vinculada |
| `id_producto` | INT | NO | FK | | FK -> PRODUCTO(id_producto) ON DELETE RESTRICT | Producto despachado |
| `vin_chasis` | VARCHAR(30) | YES | | NULL | Restricción opcional para motos | Número de VIN/Chasis serializado |
| `numero_motor` | VARCHAR(30) | YES | | NULL | Restricción opcional para motos | Número de motor de la unidad |
| `cantidad` | INT | NO | | 1 | NOT NULL, CHECK (cantidad > 0) | Unidades vendidas |
| `precio_unitario` | DECIMAL(10,2) | NO | | | NOT NULL, CHECK (precio_unitario > 0) | Precio acordado en factura |
| `descuento` | DECIMAL(10,2) | NO | | 0.00 | NOT NULL, CHECK (descuento >= 0) | Rebaja monetaria aplicada |
| `subtotal` | DECIMAL(12,2) | NO | | | NOT NULL, CHECK (subtotal >= 0) | Monto final por línea |