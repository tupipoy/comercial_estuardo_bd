## Fuente del modelo

El modelo relacional de esta entrega se deriva del Diagrama Entidad-Relación Chen aprobado en la Entrega 1.

### Entidades principales aprobadas

- SUCURSAL
- EMPLEADO
- CLIENTE
- VENTA
- COMPRA
- PROVEEDOR
- PRODUCTO
- CATEGORIA

### Relaciones N:M

1. VENTA — PRODUCTO, mediante la relación CONTIENE.
2. COMPRA — PRODUCTO, mediante la relación DETALLA.

Estas relaciones se transformarán en tablas asociativas dentro del modelo relacional.