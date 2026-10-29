# Matriz de trazabilidad — Entrega 4

| Requisito | Implementación vigente | Evidencia ejecutable |
|---|---|---|
| RF-01 Sucursales | `/sucursales`; SUCURSAL | Aceptación: CRUD de catálogos |
| RF-02 Empleados por sucursal | `/empleados`; EMPLEADO, hash y rol | Aceptación: alta/edición/baja, hash y autoprotección |
| RF-03 Clientes | `/clientes`; CLIENTE | Aceptación: CRUD persistente |
| RF-04 Categorías | `/categorias`; CATEGORIA | Aceptación: CRUD persistente |
| RF-05 Productos y stock | `/productos`, `/inventario`; PRODUCTO, INVENTARIO_SUCURSAL | Aceptación y pruebas de inventario |
| RF-06 VIN y motor | `/unidades`; UNIDAD_PRODUCTO, historial y vínculo con DETALLE_VENTA | Compra identificada, venta, traslado y reventa tras devolución |
| RF-07 Stock mínimo | `/inventario`, `/alertas`, `/conteos`; mínimo por sucursal y disponible | Consulta por rol; filtros y mínimos en servicios |
| RF-08 Proveedores autorizados | `/proveedores`, propuestas y auditoría | Siete casos de proveedores; Bodega no aprueba ni modifica |
| RF-09 Compras | `/compras`; COMPRA | Compra web de varias líneas, cabecera corregible y reverso |
| RF-10 N:M de compras | DETALLE_COMPRA | Dos detalles por compra y total/stock correctos |
| RF-11 Ventas | `/ventas`; VENTA | Venta web multlínea, correlativo, corrección auditada y anulación |
| RF-12 N:M de ventas | DETALLE_VENTA | Dos detalles, stock descontado y serial ligado a cliente |
| RD-01 Identidad y unicidad | PK, UNIQUE de documentos, personas y unidades | Metadatos, duplicados y reventa de una misma unidad |
| RD-02 Dos N:M | Detalles de compra y venta | Diccionario/diagrama y pruebas multlínea |
| RD-03 Integridad | 57 FK, CHECK, NOT NULL y claves | Instalación completa en MySQL 8.4 y metadatos |
| RD-04 Reglas SQL | 15 triggers, 8 procedimientos | Caso de procedimientos y rollback por falta de stock |
| RNF-01 Tres roles | Scripts de seguridad 01–03 | Usuarios SQL temporales y restricciones por rol |
| RNF-02 Capas / parametrización | db.py, servicios y rutas protegidas | Revisión de código y pruebas de formularios |
| RNF-03 InnoDB / atomicidad | Todas las tablas InnoDB; commit/rollback | Compra fallida, devolución y anulación sin cambios parciales |
| RNF-04 Concurrencia | Bloqueos de inventario, unidades y propuestas | Dos aprobaciones de reserva / proveedor simultáneas |
| RN-01 Conservar historia | Baja lógica, reversos y triggers contra borrado destructivo | Historial de compras/ventas conservado |
| RN-02 Disponibilidad | Físico menos reservado | Venta de unidades reservadas rechazada |
| RN-03 Actualización de stock | Trigger de venta y servicio transaccional de compra | Compra/venta de dos líneas y Kardex |
| RN-04 Precio positivo y margen | CHECK y triggers de precio/costo | Restricciones instaladas; aplicación valida importes |
| RN-05 Venta con detalle | Procedimiento detallado y validación web | Alta transaccional con rollback al fallar una línea |
| RN-06 Serial único | UNIQUE en UNIDAD_PRODUCTO | Duplicado rechazado; historia de reventa conservada |
| Extensión: traslados | Solicitud → reserva → despacho → recepción | Stock y seriales por sucursal, recepción acumulada |
| Extensión: Kardex/conteos | MOVIMIENTO_INVENTARIO y CONTEO_INVENTARIO | Conteo obsoleto rechazado y ajuste autorizado |
| Extensión: correcciones | CORRECCION_DOCUMENTO | Se actualizan cabeceras sin alterar importes ni stock |
| Extensión: respaldo | Workflow cifrado y restauración aislada | Actions 40946013024 y prueba de manipulación criptográfica |

Las tablas asociativas se gestionan mediante sus transacciones. El texto de Entrega 4 exige CRUD en las tablas principales; no se introduce una edición destructiva de detalles históricos para simular un CRUD genérico.
