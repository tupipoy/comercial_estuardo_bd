# Diccionario de datos actualizado — Entrega 4

Fuente: instalación limpia de `sql/ddl/01_schema.sql` más migraciones 08, 09 y 10, comprobada en MySQL 8.4. La evidencia estructural completa está en [VERIFICACION_ENTREGA4.json](evidencias/VERIFICACION_ENTREGA4.json).

El modelo vigente contiene **25 tablas**, 3 vistas, 15 triggers y 8 procedimientos. Las ocho entidades principales del negocio son SUCURSAL, EMPLEADO, CLIENTE, CATEGORIA, PRODUCTO, PROVEEDOR, COMPRA y VENTA. Las restantes resuelven relaciones, existencias, auditoría y operaciones.

Convención conservada: tablas `UPPER_SNAKE_CASE`, columnas `snake_case`. No se renombraron tablas productivas para corregir estilo.

## CATEGORIA

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_categoria | int | No | PRI | auto_increment |
| nombre | varchar(100) | No | UNI |  |
| descripcion | varchar(255) | Sí | — |  |
| estado | tinyint(1) | No | — | DEFAULT 1 |

Restricciones adicionales:
- `chk_categoria_estado` (CHECK): `(`estado` in (0,1))`
- `nombre` (UNIQUE).

## CLIENTE

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_cliente | int | No | PRI | auto_increment |
| nit | varchar(15) | No | UNI |  |
| cui | varchar(13) | Sí | UNI |  |
| nombres | varchar(100) | No | — |  |
| apellidos | varchar(100) | Sí | — |  |
| telefono | varchar(15) | No | — |  |
| correo | varchar(100) | Sí | — |  |
| direccion | varchar(200) | No | — |  |
| estado | tinyint(1) | No | — | DEFAULT 1 |

Restricciones adicionales:
- `chk_cliente_cui` (CHECK): `((`cui` is null) or (length(`cui`) = 13))`
- `chk_cliente_estado` (CHECK): `(`estado` in (0,1))`
- `cui` (UNIQUE).
- `nit` (UNIQUE).

## COMPRA

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_compra | int | No | PRI | auto_increment |
| numero_orden | varchar(30) | No | UNI |  |
| fecha_compra | datetime | No | — | DEFAULT CURRENT_TIMESTAMP; DEFAULT_GENERATED |
| total_compra | decimal(12,2) | No | — | DEFAULT 0.00 |
| estado_recepcion | varchar(20) | No | — |  |
| id_proveedor | int | No | MUL | FK PROVEEDOR.id_proveedor; UPDATE CASCADE; DELETE RESTRICT |
| id_empleado | int | No | MUL | FK EMPLEADO.id_empleado; UPDATE CASCADE; DELETE RESTRICT |
| id_sucursal | int | No | MUL | FK SUCURSAL.id_sucursal; UPDATE CASCADE; DELETE RESTRICT |

Restricciones adicionales:
- `chk_compra_estado` (CHECK): `(`estado_recepcion` in (_utf8mb4\'Pendiente\',_utf8mb4\'Recibido\',_utf8mb4\'Cancelado\'))`
- `chk_compra_total` (CHECK): `(`total_compra` >= 0)`
- `numero_orden` (UNIQUE).

## CONTEO_INVENTARIO

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_conteo | int | No | PRI | auto_increment |
| id_sucursal | int | No | MUL | FK SUCURSAL.id_sucursal; UPDATE RESTRICT; DELETE RESTRICT |
| id_producto | int | No | MUL | FK PRODUCTO.id_producto; UPDATE RESTRICT; DELETE RESTRICT |
| stock_sistema | int | No | — |  |
| reservado_sistema | int | No | — |  |
| revision_sistema | bigint | No | — |  |
| cantidad_contada | int | No | — |  |
| unidades_snapshot | json | Sí | — |  |
| unidades_presentes | json | Sí | — |  |
| unidades_nuevas | json | Sí | — |  |
| motivo | varchar(500) | No | — |  |
| estado | varchar(20) | No | — | DEFAULT Pendiente |
| id_solicitante | int | No | MUL | FK EMPLEADO.id_empleado; UPDATE RESTRICT; DELETE RESTRICT |
| id_responsable | int | Sí | MUL | FK EMPLEADO.id_empleado; UPDATE RESTRICT; DELETE RESTRICT |
| fecha | datetime | No | — | DEFAULT CURRENT_TIMESTAMP; DEFAULT_GENERATED |
| fecha_resolucion | datetime | Sí | — |  |
| observacion | varchar(500) | Sí | — |  |

Restricciones adicionales:
- `CONTEO_INVENTARIO_chk_1` (CHECK): `(`cantidad_contada` >= 0)`
- `CONTEO_INVENTARIO_chk_2` (CHECK): `(`estado` in (_utf8mb4\'Pendiente\',_utf8mb4\'Aprobado\',_utf8mb4\'Rechazado\'))`

## CORRECCION_DOCUMENTO

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_correccion | bigint | No | PRI | auto_increment |
| id_venta | int | Sí | MUL | FK VENTA.id_venta; UPDATE RESTRICT; DELETE RESTRICT |
| id_compra | int | Sí | MUL | FK COMPRA.id_compra; UPDATE RESTRICT; DELETE RESTRICT |
| id_empleado | int | No | MUL | FK EMPLEADO.id_empleado; UPDATE RESTRICT; DELETE RESTRICT |
| fecha | datetime(6) | No | — | DEFAULT CURRENT_TIMESTAMP(6); DEFAULT_GENERATED |
| motivo | varchar(500) | No | — |  |
| datos_anteriores | json | No | — |  |
| datos_nuevos | json | No | — |  |

Restricciones adicionales:
- `CORRECCION_DOCUMENTO_chk_1` (CHECK): `(((`id_venta` is not null) and (`id_compra` is null)) or ((`id_venta` is null) and (`id_compra` is not null)))`

## DETALLE_COMPRA

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_detalle_compra | int | No | PRI | auto_increment |
| id_compra | int | No | MUL | FK COMPRA.id_compra; UPDATE CASCADE; DELETE CASCADE |
| id_producto | int | No | MUL | FK PRODUCTO.id_producto; UPDATE CASCADE; DELETE RESTRICT |
| cantidad | int | No | — |  |
| costo_unitario | decimal(10,2) | No | — |  |
| subtotal | decimal(12,2) | No | — |  |

Restricciones adicionales:
- `chk_detcompra_cantidad` (CHECK): `(`cantidad` > 0)`
- `chk_detcompra_costo` (CHECK): `(`costo_unitario` > 0)`
- `chk_detcompra_subtotal` (CHECK): `(`subtotal` >= 0)`

## DETALLE_REVERSO

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_detalle_reverso | int | No | PRI | auto_increment |
| id_reverso | int | No | MUL | FK REVERSO_DOCUMENTO.id_reverso; UPDATE RESTRICT; DELETE RESTRICT |
| id_producto | int | No | MUL | FK PRODUCTO.id_producto; UPDATE RESTRICT; DELETE RESTRICT |
| id_detalle_venta | int | Sí | MUL | FK DETALLE_VENTA.id_detalle_venta; UPDATE RESTRICT; DELETE RESTRICT |
| id_detalle_compra | int | Sí | MUL | FK DETALLE_COMPRA.id_detalle_compra; UPDATE RESTRICT; DELETE RESTRICT |
| cantidad | int | No | — |  |
| importe | decimal(12,2) | No | — |  |

Restricciones adicionales:
- `DETALLE_REVERSO_chk_1` (CHECK): `(`cantidad` > 0)`

## DETALLE_TRASLADO

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_detalle_traslado | int | No | PRI | auto_increment |
| id_traslado | int | No | MUL | FK TRASLADO.id_traslado; UPDATE CASCADE; DELETE CASCADE |
| id_producto | int | No | MUL | FK PRODUCTO.id_producto; UPDATE CASCADE; DELETE RESTRICT |
| cantidad | int | No | — |  |
| cantidad_recibida | int | Sí | — |  |

Restricciones adicionales:
- `chk_dettraslado_cantidad` (CHECK): `(`cantidad` > 0)`
- `chk_dettraslado_recibida` (CHECK): `((`cantidad_recibida` is null) or ((`cantidad_recibida` >= 0) and (`cantidad_recibida` <= `cantidad`)))`
- `uq_dettraslado_producto` (UNIQUE).

## DETALLE_VENTA

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_detalle_venta | int | No | PRI | auto_increment |
| id_venta | int | No | MUL | FK VENTA.id_venta; UPDATE CASCADE; DELETE CASCADE |
| id_producto | int | No | MUL | FK PRODUCTO.id_producto; UPDATE CASCADE; DELETE RESTRICT |
| vin_chasis | varchar(50) | Sí | MUL |  |
| numero_motor | varchar(50) | Sí | MUL |  |
| cantidad | int | No | — |  |
| precio_unitario | decimal(10,2) | No | — |  |
| descuento | decimal(10,2) | No | — | DEFAULT 0.00 |
| subtotal | decimal(12,2) | No | — |  |
| id_unidad | int | Sí | MUL | FK UNIDAD_PRODUCTO.id_unidad; UPDATE RESTRICT; DELETE RESTRICT |

Restricciones adicionales:
- `chk_detventa_cantidad` (CHECK): `(`cantidad` > 0)`
- `chk_detventa_descuento` (CHECK): `(`descuento` >= 0)`
- `chk_detventa_precio` (CHECK): `(`precio_unitario` > 0)`
- `chk_detventa_subtotal` (CHECK): `(`subtotal` >= 0)`

## EMPLEADO

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_empleado | int | No | PRI | auto_increment |
| cui | varchar(13) | No | UNI |  |
| nombres | varchar(100) | No | — |  |
| apellidos | varchar(100) | No | — |  |
| cargo | varchar(50) | No | — |  |
| telefono | varchar(15) | No | — |  |
| correo | varchar(100) | Sí | UNI |  |
| password_hash | varchar(255) | Sí | — |  |
| intentos_login_fallidos | tinyint unsigned | No | — | DEFAULT 0 |
| bloqueado_hasta | datetime | Sí | — |  |
| fecha_ingreso | date | No | — |  |
| id_sucursal | int | No | MUL | FK SUCURSAL.id_sucursal; UPDATE CASCADE; DELETE RESTRICT |
| estado | tinyint(1) | No | — | DEFAULT 1 |

Restricciones adicionales:
- `chk_empleado_cui` (CHECK): `(length(`cui`) = 13)`
- `chk_empleado_estado` (CHECK): `(`estado` in (0,1))`
- `correo` (UNIQUE).
- `cui` (UNIQUE).

## EVENTO_PROVEEDOR

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_evento | bigint | No | PRI | auto_increment |
| id_propuesta | int | Sí | MUL | FK PROPUESTA_PROVEEDOR.id_propuesta; UPDATE RESTRICT; DELETE RESTRICT |
| id_proveedor | int | Sí | MUL | FK PROVEEDOR.id_proveedor; UPDATE RESTRICT; DELETE RESTRICT |
| id_empleado | int | No | MUL | FK EMPLEADO.id_empleado; UPDATE RESTRICT; DELETE RESTRICT |
| accion | varchar(30) | No | — |  |
| fecha | datetime(6) | No | — | DEFAULT CURRENT_TIMESTAMP(6); DEFAULT_GENERATED |
| observacion | varchar(500) | Sí | — |  |
| datos_anteriores | json | Sí | — |  |
| datos_nuevos | json | Sí | — |  |

Restricciones adicionales:
- `EVENTO_PROVEEDOR_chk_1` (CHECK): `((`id_propuesta` is not null) or (`id_proveedor` is not null))`

## EVENTO_TRASLADO

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_evento | bigint | No | PRI | auto_increment |
| id_traslado | int | No | MUL | FK TRASLADO.id_traslado; UPDATE RESTRICT; DELETE RESTRICT |
| accion | varchar(50) | No | — |  |
| id_empleado | int | No | MUL | FK EMPLEADO.id_empleado; UPDATE RESTRICT; DELETE RESTRICT |
| observacion | varchar(500) | Sí | — |  |
| fecha | datetime(6) | No | — | DEFAULT CURRENT_TIMESTAMP(6); DEFAULT_GENERATED |

## HISTORIAL_UNIDAD

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_historial | bigint | No | PRI | auto_increment |
| id_unidad | int | No | MUL | FK UNIDAD_PRODUCTO.id_unidad; UPDATE RESTRICT; DELETE RESTRICT |
| fecha | datetime(6) | No | — | DEFAULT CURRENT_TIMESTAMP(6); DEFAULT_GENERATED |
| id_sucursal_origen | int | Sí | — |  |
| id_sucursal_destino | int | No | — |  |
| estado_anterior | varchar(30) | Sí | — |  |
| estado_nuevo | varchar(30) | No | — |  |
| id_empleado | int | Sí | MUL | FK EMPLEADO.id_empleado; UPDATE RESTRICT; DELETE RESTRICT |
| referencia | varchar(100) | Sí | — |  |
| motivo | varchar(500) | Sí | — |  |

## INVENTARIO_SUCURSAL

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_sucursal | int | No | PRI | FK SUCURSAL.id_sucursal; UPDATE CASCADE; DELETE RESTRICT |
| id_producto | int | No | PRI | FK PRODUCTO.id_producto; UPDATE CASCADE; DELETE RESTRICT |
| stock_actual | int | No | — | DEFAULT 0 |
| actualizado_en | datetime | No | — | DEFAULT CURRENT_TIMESTAMP; DEFAULT_GENERATED on update CURRENT_TIMESTAMP |
| stock_reservado | int | No | — | DEFAULT 0 |
| stock_minimo | int | Sí | — |  |
| revision | bigint | No | — | DEFAULT 0 |

Restricciones adicionales:
- `chk_inventario_stock` (CHECK): `(`stock_actual` >= 0)`
- `chk_minimo_sucursal` (CHECK): `((`stock_minimo` is null) or (`stock_minimo` >= 0))`
- `chk_reservas` (CHECK): `((`stock_reservado` >= 0) and (`stock_reservado` <= `stock_actual`))`

## MOVIMIENTO_INVENTARIO

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_movimiento | bigint | No | PRI | auto_increment |
| fecha | datetime(6) | No | — | DEFAULT CURRENT_TIMESTAMP(6); DEFAULT_GENERATED |
| id_sucursal | int | No | MUL | FK SUCURSAL.id_sucursal; UPDATE RESTRICT; DELETE RESTRICT |
| id_producto | int | No | MUL | FK PRODUCTO.id_producto; UPDATE RESTRICT; DELETE RESTRICT |
| tipo | varchar(50) | No | — |  |
| referencia | varchar(100) | Sí | — |  |
| id_empleado | int | Sí | MUL | FK EMPLEADO.id_empleado; UPDATE RESTRICT; DELETE RESTRICT |
| cantidad | int | No | — |  |
| saldo_anterior | int | No | — |  |
| saldo_posterior | int | No | — |  |
| reservado_anterior | int | No | — |  |
| reservado_posterior | int | No | — |  |
| motivo | varchar(500) | Sí | — |  |

## PRODUCTO

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_producto | int | No | PRI | auto_increment |
| codigo_barra | varchar(50) | Sí | UNI |  |
| nombre | varchar(150) | No | — |  |
| descripcion | text | Sí | — |  |
| precio_costo | decimal(10,2) | No | — | DEFAULT 0.00 |
| precio_venta | decimal(10,2) | No | — |  |
| stock_minimo | int | No | — | DEFAULT 1 |
| id_categoria | int | No | MUL | FK CATEGORIA.id_categoria; UPDATE CASCADE; DELETE RESTRICT |
| estado | tinyint(1) | No | — | DEFAULT 1 |
| requiere_serie | tinyint | No | — | DEFAULT 0 |

Restricciones adicionales:
- `chk_producto_estado` (CHECK): `(`estado` in (0,1))`
- `chk_producto_margen` (CHECK): `(`precio_venta` >= `precio_costo`)`
- `chk_producto_precio` (CHECK): `(`precio_venta` > 0)`
- `chk_producto_precio_costo` (CHECK): `(`precio_costo` >= 0)`
- `chk_producto_serie` (CHECK): `(`requiere_serie` in (0,1))`
- `chk_producto_stock_minimo` (CHECK): `(`stock_minimo` >= 0)`
- `codigo_barra` (UNIQUE).

## PROPUESTA_PROVEEDOR

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_propuesta | int | No | PRI | auto_increment |
| nit | varchar(15) | No | — |  |
| razon_social | varchar(150) | No | — |  |
| contacto | varchar(100) | Sí | — |  |
| telefono | varchar(15) | No | — |  |
| correo | varchar(100) | Sí | — |  |
| direccion | varchar(200) | Sí | — |  |
| estado | varchar(20) | No | — | DEFAULT Pendiente |
| id_solicitante | int | No | MUL | FK EMPLEADO.id_empleado; UPDATE RESTRICT; DELETE RESTRICT |
| fecha_solicitud | datetime(6) | No | — | DEFAULT CURRENT_TIMESTAMP(6); DEFAULT_GENERATED |
| id_responsable | int | Sí | MUL | FK EMPLEADO.id_empleado; UPDATE RESTRICT; DELETE RESTRICT |
| fecha_resolucion | datetime(6) | Sí | — |  |
| observacion | varchar(500) | Sí | — |  |
| id_proveedor | int | Sí | UNI | FK PROVEEDOR.id_proveedor; UPDATE RESTRICT; DELETE RESTRICT |
| nit_pendiente | varchar(15) | Sí | UNI | STORED GENERATED; (case when (`estado` = _utf8mb4\'Pendiente\') then `nit` else NULL end) |

Restricciones adicionales:
- `id_proveedor` (UNIQUE).
- `PROPUESTA_PROVEEDOR_chk_1` (CHECK): `(`estado` in (_utf8mb4\'Pendiente\',_utf8mb4\'Aprobada\',_utf8mb4\'Rechazada\'))`
- `PROPUESTA_PROVEEDOR_chk_2` (CHECK): `(((`estado` = _utf8mb4\'Pendiente\') and (`id_responsable` is null) and (`fecha_resolucion` is null) and (`id_proveedor` is null)) or ((`estado` = _utf8mb4\'Aprobada\') and (`id_responsable` is not null) and (`fecha_resolucion` is not null) and (`id_proveedor` is not null)) or ((`estado` = _utf8mb4\'Rechazada\') and (`id_responsable` is not null) and (`fecha_resolucion` is not null) and (`id_proveedor` is null)))`
- `uq_propuesta_nit_pendiente` (UNIQUE).

## PROVEEDOR

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_proveedor | int | No | PRI | auto_increment |
| nit | varchar(15) | No | UNI |  |
| razon_social | varchar(150) | No | — |  |
| contacto | varchar(100) | Sí | — |  |
| telefono | varchar(15) | No | — |  |
| correo | varchar(100) | Sí | — |  |
| direccion | varchar(200) | Sí | — |  |
| estado | tinyint(1) | No | — | DEFAULT 1 |

Restricciones adicionales:
- `chk_proveedor_estado` (CHECK): `(`estado` in (0,1))`
- `nit` (UNIQUE).

## RESPALDO_EJECUCION

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_respaldo | bigint | No | PRI | auto_increment |
| inicio | datetime | No | — | DEFAULT CURRENT_TIMESTAMP; DEFAULT_GENERATED |
| fin | datetime | Sí | — |  |
| estado | varchar(20) | No | — | DEFAULT En proceso |
| restauracion_verificada | tinyint | No | — | DEFAULT 0 |
| archivo | varchar(200) | Sí | — |  |
| sha256 | varchar(64) | Sí | — |  |
| enlace | varchar(300) | Sí | — |  |
| detalle | varchar(500) | Sí | — |  |

## REVERSO_DOCUMENTO

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_reverso | int | No | PRI | auto_increment |
| tipo | varchar(30) | No | — |  |
| id_venta | int | Sí | MUL | FK VENTA.id_venta; UPDATE RESTRICT; DELETE RESTRICT |
| id_compra | int | Sí | MUL | FK COMPRA.id_compra; UPDATE RESTRICT; DELETE RESTRICT |
| id_empleado | int | No | MUL | FK EMPLEADO.id_empleado; UPDATE RESTRICT; DELETE RESTRICT |
| fecha | datetime | No | — | DEFAULT CURRENT_TIMESTAMP; DEFAULT_GENERATED |
| motivo | varchar(500) | No | — |  |
| importe | decimal(12,2) | No | — | DEFAULT 0.00 |

Restricciones adicionales:
- `REVERSO_DOCUMENTO_chk_1` (CHECK): `(`tipo` in (_utf8mb4\'DevoluciÃ³n venta\',_utf8mb4\'AnulaciÃ³n venta\',_utf8mb4\'DevoluciÃ³n compra\',_utf8mb4\'AnulaciÃ³n compra\'))`
- `REVERSO_DOCUMENTO_chk_2` (CHECK): `(((`id_venta` is not null) and (`id_compra` is null)) or ((`id_compra` is not null) and (`id_venta` is null)))`

## SUCURSAL

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_sucursal | int | No | PRI | auto_increment |
| nombre | varchar(100) | No | UNI |  |
| direccion | varchar(200) | No | — |  |
| telefono | varchar(15) | No | — |  |
| municipio | varchar(100) | No | — |  |
| estado | tinyint(1) | No | — | DEFAULT 1 |

Restricciones adicionales:
- `chk_sucursal_estado` (CHECK): `(`estado` in (0,1))`
- `chk_sucursal_telefono` (CHECK): `(length(`telefono`) >= 8)`
- `nombre` (UNIQUE).

## TRASLADO

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_traslado | int | No | PRI | auto_increment |
| numero_traslado | varchar(30) | No | UNI |  |
| fecha_traslado | datetime | No | — | DEFAULT CURRENT_TIMESTAMP; DEFAULT_GENERATED |
| estado | varchar(30) | No | — | DEFAULT Pendiente de aprobación |
| id_sucursal_origen | int | No | MUL | FK SUCURSAL.id_sucursal; UPDATE RESTRICT; DELETE RESTRICT |
| id_sucursal_destino | int | No | MUL | FK SUCURSAL.id_sucursal; UPDATE RESTRICT; DELETE RESTRICT |
| id_empleado | int | No | MUL | FK EMPLEADO.id_empleado; UPDATE CASCADE; DELETE RESTRICT |
| id_empleado_aprobacion | int | Sí | MUL | FK EMPLEADO.id_empleado; UPDATE CASCADE; DELETE RESTRICT |
| fecha_aprobacion | datetime | Sí | — |  |
| observacion_resolucion | varchar(500) | Sí | — |  |
| id_empleado_despacho | int | Sí | MUL | FK EMPLEADO.id_empleado; UPDATE CASCADE; DELETE RESTRICT |
| fecha_despacho | datetime | Sí | — |  |
| id_empleado_recepcion | int | Sí | MUL | FK EMPLEADO.id_empleado; UPDATE CASCADE; DELETE RESTRICT |
| fecha_recepcion | datetime | Sí | — |  |
| observacion_recepcion | varchar(500) | Sí | — |  |

Restricciones adicionales:
- `chk_traslado_estado` (CHECK): `(`estado` in (_utf8mb4\'Pendiente de aprobaciÃ³n\',_utf8mb4\'Rechazado\',_utf8mb4\'Aprobado\',_utf8mb4\'En trÃ¡nsito\',_utf8mb4\'Con diferencias\',_utf8mb4\'Completado\',_utf8mb4\'Anulado\'))`
- `chk_traslado_sucursales` (CHECK): `(`id_sucursal_origen` <> `id_sucursal_destino`)`
- `numero_traslado` (UNIQUE).

## TRASLADO_UNIDAD

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_traslado | int | No | PRI | FK TRASLADO.id_traslado; UPDATE RESTRICT; DELETE RESTRICT |
| id_unidad | int | No | PRI | FK UNIDAD_PRODUCTO.id_unidad; UPDATE RESTRICT; DELETE RESTRICT |
| recibida | tinyint | No | — | DEFAULT 0 |

Restricciones adicionales:
- `TRASLADO_UNIDAD_chk_1` (CHECK): `(`recibida` in (0,1))`

## UNIDAD_PRODUCTO

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_unidad | int | No | PRI | auto_increment |
| id_producto | int | No | MUL | FK PRODUCTO.id_producto; UPDATE RESTRICT; DELETE RESTRICT |
| vin_chasis | varchar(50) | No | UNI |  |
| numero_motor | varchar(50) | No | UNI |  |
| id_sucursal | int | No | MUL | FK SUCURSAL.id_sucursal; UPDATE RESTRICT; DELETE RESTRICT |
| estado | varchar(30) | No | — | DEFAULT Disponible |
| id_detalle_compra | int | Sí | MUL | FK DETALLE_COMPRA.id_detalle_compra; UPDATE RESTRICT; DELETE RESTRICT |
| id_detalle_venta | int | Sí | MUL | FK DETALLE_VENTA.id_detalle_venta; UPDATE RESTRICT; DELETE RESTRICT |
| id_traslado | int | Sí | MUL | FK TRASLADO.id_traslado; UPDATE RESTRICT; DELETE RESTRICT |
| fecha_registro | datetime | No | — | DEFAULT CURRENT_TIMESTAMP; DEFAULT_GENERATED |

Restricciones adicionales:
- `chk_unidad_estado` (CHECK): `(`estado` in (_utf8mb4\'Disponible\',_utf8mb4\'Reservada\',_utf8mb4\'En trÃ¡nsito\',_utf8mb4\'Vendida\',_utf8mb4\'Baja\',_utf8mb4\'Devuelta a proveedor\'))`
- `numero_motor` (UNIQUE).
- `vin_chasis` (UNIQUE).

## VENTA

| Campo | Tipo | Nulo | Clave | Predeterminado / detalle |
|---|---|---|---|---|
| id_venta | int | No | PRI | auto_increment |
| serie_factura | varchar(10) | No | MUL |  |
| numero_factura | int | No | — |  |
| fecha_venta | datetime | No | — | DEFAULT CURRENT_TIMESTAMP; DEFAULT_GENERATED |
| total_venta | decimal(12,2) | No | — | DEFAULT 0.00 |
| tipo_pago | varchar(30) | No | — |  |
| estado | varchar(20) | No | — | DEFAULT Emitida |
| id_cliente | int | No | MUL | FK CLIENTE.id_cliente; UPDATE CASCADE; DELETE RESTRICT |
| id_empleado | int | No | MUL | FK EMPLEADO.id_empleado; UPDATE CASCADE; DELETE RESTRICT |
| id_sucursal | int | No | MUL | FK SUCURSAL.id_sucursal; UPDATE CASCADE; DELETE RESTRICT |

Restricciones adicionales:
- `chk_venta_estado` (CHECK): `(`estado` in (_utf8mb4\'Emitida\',_utf8mb4\'Anulada\'))`
- `chk_venta_tipo_pago` (CHECK): `(`tipo_pago` in (_utf8mb4\'Efectivo\',_utf8mb4\'Transferencia\',_utf8mb4\'DepÃ³sito Bancario\'))`
- `chk_venta_total` (CHECK): `(`total_venta` >= 0)`
- `uq_venta_factura` (UNIQUE).

## Reglas de interpretación

- `UNIDAD_PRODUCTO` impone unicidad global de VIN y motor. Los seriales de DETALLE_VENTA se conservan como dato histórico y no son únicos allí: una unidad devuelta puede venderse de nuevo.
- `stock_actual` representa existencias físicas; `stock_reservado` las unidades apartadas. Disponible se calcula como físico menos reservado; tránsito se deriva de traslados pendientes.
- Los totales y subtotales se calculan en procedimientos/servicios dentro de la misma transacción. Se conservan como importes históricos y se comprueba su consistencia. Es una desnormalización controlada que el equipo debe justificar frente a S7.
- `CORRECCION_DOCUMENTO` permite actualizar cabeceras con versiones anteriores y nuevas. Las correcciones de cantidades se realizan con reversos, sin borrar líneas emitidas.
- Los JSON de auditoría conservan versiones históricas; no sustituyen las entidades relacionales ni las dos relaciones N:M principales.
- Las acciones RESTRICT declaradas explícitamente en los scripts nuevos conservan la semántica restrictiva de las referencias previas.
