# Diccionario de datos actualizado — Entrega 4

**Fuente vigente:** `sql/ddl/01_schema.sql`  
**Motor:** InnoDB · **Codificación:** `utf8mb4` · **SGBD:** MySQL 8+

Este documento refleja el DDL actual. `docs/entrega-2/diccionario_datos.md` conserva el diccionario histórico entregado en la fase 2.

## SUCURSAL

| Campo | Tipo | Nulo | Clave / regla |
|---|---|---|---|
| id_sucursal | INT AUTO_INCREMENT | No | PK |
| nombre | VARCHAR(100) | No | UNIQUE |
| direccion | VARCHAR(200) | No | |
| telefono | VARCHAR(15) | No | CHECK longitud >= 8 |
| municipio | VARCHAR(100) | No | |
| estado | TINYINT(1) | No | DEFAULT 1; CHECK 0/1 |

## EMPLEADO

| Campo | Tipo | Nulo | Clave / regla |
|---|---|---|---|
| id_empleado | INT AUTO_INCREMENT | No | PK |
| cui | VARCHAR(13) | No | UNIQUE; CHECK longitud = 13 |
| nombres, apellidos | VARCHAR(100) | No | |
| cargo | VARCHAR(50) | No | Aplicación permite Administrador, Vendedor o Bodega |
| telefono | VARCHAR(15) | No | |
| correo | VARCHAR(100) | Sí | UNIQUE |
| password_hash | VARCHAR(255) | Sí | Hash PBKDF2; nulo para cuentas deshabilitadas |
| fecha_ingreso | DATE | No | |
| id_sucursal | INT | No | FK SUCURSAL; UPDATE CASCADE, DELETE RESTRICT |
| estado | TINYINT(1) | No | DEFAULT 1; CHECK 0/1 |

## CLIENTE

| Campo | Tipo | Nulo | Clave / regla |
|---|---|---|---|
| id_cliente | INT AUTO_INCREMENT | No | PK |
| nit | VARCHAR(15) | No | UNIQUE |
| cui | VARCHAR(13) | Sí | UNIQUE; CHECK nulo o longitud = 13 |
| nombres | VARCHAR(100) | No | |
| apellidos | VARCHAR(100) | Sí | |
| telefono | VARCHAR(15) | No | |
| correo | VARCHAR(100) | Sí | |
| direccion | VARCHAR(200) | No | |
| estado | TINYINT(1) | No | DEFAULT 1; CHECK 0/1 |

## CATEGORIA

| Campo | Tipo | Nulo | Clave / regla |
|---|---|---|---|
| id_categoria | INT AUTO_INCREMENT | No | PK |
| nombre | VARCHAR(100) | No | UNIQUE |
| descripcion | VARCHAR(255) | Sí | |
| estado | TINYINT(1) | No | DEFAULT 1; CHECK 0/1 |

## PRODUCTO

| Campo | Tipo | Nulo | Clave / regla |
|---|---|---|---|
| id_producto | INT AUTO_INCREMENT | No | PK |
| codigo_barra | VARCHAR(50) | Sí | UNIQUE |
| nombre | VARCHAR(150) | No | |
| descripcion | TEXT | Sí | |
| precio_costo | DECIMAL(10,2) | No | DEFAULT 0; CHECK >= 0 |
| precio_venta | DECIMAL(10,2) | No | CHECK > 0 |
| stock_minimo | INT | No | DEFAULT 1; CHECK >= 0 |
| id_categoria | INT | No | FK CATEGORIA; UPDATE CASCADE, DELETE RESTRICT |
| estado | TINYINT(1) | No | DEFAULT 1; CHECK 0/1 |

## INVENTARIO_SUCURSAL

| Campo | Tipo | Nulo | Clave / regla |
|---|---|---|---|
| id_sucursal | INT | No | PK compuesta; FK SUCURSAL |
| id_producto | INT | No | PK compuesta; FK PRODUCTO |
| stock_actual | INT | No | DEFAULT 0; CHECK >= 0 |
| actualizado_en | DATETIME | No | Actualización automática |

Cada fila representa las existencias de un producto en una sucursal. Administración consulta la suma; los demás cargos consultan su sucursal asignada.

## TRASLADO

| Campo | Tipo | Nulo | Clave / regla |
|---|---|---|---|
| id_traslado | INT AUTO_INCREMENT | No | PK |
| numero_traslado | VARCHAR(30) | No | UNIQUE |
| fecha_traslado | DATETIME | No | DEFAULT CURRENT_TIMESTAMP |
| estado | VARCHAR(20) | No | Completado o Anulado |
| id_sucursal_origen | INT | No | FK SUCURSAL; distinto del destino |
| id_sucursal_destino | INT | No | FK SUCURSAL |
| id_empleado | INT | No | FK EMPLEADO |

## DETALLE_TRASLADO

| Campo | Tipo | Nulo | Clave / regla |
|---|---|---|---|
| id_detalle_traslado | INT AUTO_INCREMENT | No | PK |
| id_traslado | INT | No | FK TRASLADO; DELETE CASCADE |
| id_producto | INT | No | FK PRODUCTO |
| cantidad | INT | No | UNIQUE con traslado y producto; CHECK > 0 |

## PROVEEDOR

| Campo | Tipo | Nulo | Clave / regla |
|---|---|---|---|
| id_proveedor | INT AUTO_INCREMENT | No | PK |
| nit | VARCHAR(15) | No | UNIQUE |
| razon_social | VARCHAR(150) | No | |
| contacto | VARCHAR(100) | Sí | |
| telefono | VARCHAR(15) | No | |
| correo | VARCHAR(100) | Sí | |
| direccion | VARCHAR(200) | Sí | |
| estado | TINYINT(1) | No | DEFAULT 1; CHECK 0/1 |

## COMPRA

| Campo | Tipo | Nulo | Clave / regla |
|---|---|---|---|
| id_compra | INT AUTO_INCREMENT | No | PK |
| numero_orden | VARCHAR(30) | No | UNIQUE |
| fecha_compra | DATETIME | No | DEFAULT CURRENT_TIMESTAMP |
| total_compra | DECIMAL(12,2) | No | DEFAULT 0; CHECK >= 0 |
| estado_recepcion | VARCHAR(20) | No | CHECK: Pendiente, Recibido o Cancelado |
| id_proveedor | INT | No | FK PROVEEDOR; UPDATE CASCADE, DELETE RESTRICT |
| id_empleado | INT | No | FK EMPLEADO; UPDATE CASCADE, DELETE RESTRICT |
| id_sucursal | INT | No | FK SUCURSAL; sucursal receptora |

## DETALLE_COMPRA

| Campo | Tipo | Nulo | Clave / regla |
|---|---|---|---|
| id_detalle_compra | INT AUTO_INCREMENT | No | PK |
| id_compra | INT | No | FK COMPRA; UPDATE CASCADE, DELETE CASCADE |
| id_producto | INT | No | FK PRODUCTO; UPDATE CASCADE, DELETE RESTRICT |
| cantidad | INT | No | CHECK > 0 |
| costo_unitario | DECIMAL(10,2) | No | CHECK > 0 |
| subtotal | DECIMAL(12,2) | No | CHECK >= 0 |

## VENTA

| Campo | Tipo | Nulo | Clave / regla |
|---|---|---|---|
| id_venta | INT AUTO_INCREMENT | No | PK |
| serie_factura | VARCHAR(10) | No | UNIQUE compuesto con numero_factura |
| numero_factura | INT | No | UNIQUE compuesto con serie_factura |
| fecha_venta | DATETIME | No | DEFAULT CURRENT_TIMESTAMP |
| total_venta | DECIMAL(12,2) | No | DEFAULT 0; CHECK >= 0 |
| tipo_pago | VARCHAR(30) | No | CHECK: Efectivo, Transferencia o Depósito Bancario |
| estado | VARCHAR(20) | No | DEFAULT Emitida; CHECK Emitida/Anulada |
| id_cliente | INT | No | FK CLIENTE; UPDATE CASCADE, DELETE RESTRICT |
| id_empleado | INT | No | FK EMPLEADO; UPDATE CASCADE, DELETE RESTRICT |
| id_sucursal | INT | No | FK SUCURSAL; UPDATE CASCADE, DELETE RESTRICT |

## DETALLE_VENTA

| Campo | Tipo | Nulo | Clave / regla |
|---|---|---|---|
| id_detalle_venta | INT AUTO_INCREMENT | No | PK |
| id_venta | INT | No | FK VENTA; UPDATE CASCADE, DELETE CASCADE |
| id_producto | INT | No | FK PRODUCTO; UPDATE CASCADE, DELETE RESTRICT |
| vin_chasis | VARCHAR(50) | Sí | UNIQUE; serial de motocicleta |
| numero_motor | VARCHAR(50) | Sí | UNIQUE; serial de motocicleta |
| cantidad | INT | No | CHECK > 0 |
| precio_unitario | DECIMAL(10,2) | No | CHECK > 0 |
| descuento | DECIMAL(10,2) | No | DEFAULT 0; CHECK >= 0 |
| subtotal | DECIMAL(12,2) | No | CHECK >= 0 |

## Nota de mantenimiento

El detalle se registra a través de los procedimientos de compra/venta para conservar totales, inventario y atomicidad. Para ajustes futuros, modificar primero el DDL y después actualizar este diccionario y ejecutar la instalación/pruebas en una base temporal.
