# Sistema de Gestión de Ventas, Compras e Inventario
## Entrega 1 — Especificación de Requerimientos del Sistema
**Empresa:** Comercial Estuardo
**Fecha:** Agosto 2026

---

## 1. Introducción

El presente documento detalla la especificación de requerimientos funcionales, requerimientos de diseño de datos, reglas de negocio y restricciones técnicas para la base de datos de Comercial Estuardo. Su objetivo es servir de base formal para el modelado conceptual (Diagrama Entidad-Relación en Notación Chen), el diseño lógico normalizado en 3FN y la posterior implementación en MySQL, en cumplimiento con los requisitos mínimos establecidos en el enunciado del curso.

---

## 2. Requerimientos Funcionales (RF)

### Módulo de Sucursales y Personal

**RF-01 (Gestión de Sucursales):** El sistema debe registrar y administrar la información de las sucursales físicas de la empresa (id_sucursal, nombre, dirección, teléfono, municipio).

**RF-02 (Gestión de Empleados):** El sistema debe registrar los datos del personal (id_empleado, CUI/DPI, nombre, apellido, cargo/puesto, teléfono, correo, fecha de ingreso) y asociar obligatoriamente a cada empleado con la sucursal en la que labora.

### Módulo de Clientes

**RF-03 (Registro y Directorio de Clientes):** El sistema debe permitir la creación y mantenimiento del catálogo de clientes, almacenando su código único (id_cliente), identificación tributaria (NIT o DPI), nombres, apellidos, teléfono, correo electrónico y dirección.

### Módulo de Inventarios y Productos

**RF-04 (Categorización de Productos):** El sistema debe organizar el catálogo en categorías (id_categoria, nombre de categoría, descripción), tales como Motocicletas, Repuestos, Lubricantes y Equipo de Protección.

**RF-05 (Catálogo General de Productos):** El sistema debe registrar cada producto comercializado (id_producto, código de barra, nombre, descripción técnica, precio de venta, stock actual y stock mínimo).

**RF-06 (Trazabilidad de Unidades Serializadas — Motocicletas):** El sistema debe registrar, para cada motocicleta vendida, su número de chasis (VIN) y número de motor de forma individual, vinculando ambos datos de manera obligatoria a la venta y al cliente comprador. Este registro debe quedar disponible para trámites posteriores de placas y garantías. *(A diferencia de repuestos, lubricantes o accesorios, que se gestionan por cantidad de stock genérico, cada motocicleta es una unidad física individual identificable.)*

**RF-07 (Consulta de Stock Mínimo):** El sistema debe permitir consultar en cualquier momento los productos cuyo stock actual sea igual o menor a su stock mínimo definido, mediante una consulta parametrizada disponible desde la interfaz.

### Módulo de Compras y Proveedores

**RF-08 (Gestión de Proveedores):** El sistema debe almacenar el directorio de proveedores autorizados (id_proveedor, NIT, razón social, contacto, teléfono, dirección).

**RF-09 (Registro de Órdenes de Compra):** El sistema debe registrar las compras de mercadería ingresadas (id_compra, número de orden, fecha de compra, total de compra, estado de recepción), vinculando al proveedor que suministra y al empleado que autoriza/recibe.

**RF-10 (Detalle de Compra — Relación N:M):** El sistema debe permitir registrar múltiples productos en una misma compra, almacenando la cantidad recibida, el costo unitario de adquisición y el subtotal calculado por línea.

### Módulo de Facturación y Ventas

**RF-11 (Emisión de Ventas):** El sistema debe generar ventas (id_venta, serie de factura, número correlativo, fecha de emisión, total de venta, estado), asociando al cliente comprador, al vendedor asignado y a la sucursal donde se concreta la operación.

**RF-12 (Detalle de Venta — Relación N:M):** El sistema debe permitir registrar múltiples productos por factura, almacenando la cantidad vendida, el precio unitario pactado, descuento aplicable y subtotal por producto.

---

## 3. Requerimientos de Diseño y Restricciones de Datos (RD)

**RD-01 (Claves Primarias e Identificación):** Todas las entidades deben contar con una clave primaria única (PK artificial autoincremental). Los valores de CUI/DPI, NIT, código de barras, VIN, número de motor y series/números de factura deben contar con restricción UNIQUE.

**RD-02 (Resolución de Relaciones N:M):** Se deben resolver formalmente las dos relaciones transaccionales muchos a muchos: CONTIENE (detalle de venta, entre VENTA y PRODUCTO) y DETALLA (detalle de compra, entre COMPRA y PRODUCTO).

**RD-03 (Integridad Referencial y Restricciones):** Todas las llaves foráneas (FK) deben definir políticas explícitas de integridad referencial (ON DELETE RESTRICT / ON UPDATE CASCADE). Se deben implementar al menos 15 restricciones explícitas (PK, FK, CHECK, UNIQUE, NOT NULL).

**RD-04 (Lógica de Negocio en Base de Datos):** El sistema debe implementar al menos 2 triggers y 2 procedimientos almacenados (o funciones), cada uno con una regla de negocio explícita y documentada que justifique su necesidad (por ejemplo: actualización de stock, validación de disponibilidad, cálculo de totales).

---

## 4. Requerimientos No Funcionales (RNF)

**RNF-01 (Seguridad y Roles en Base de Datos):** El sistema debe contar con al menos 3 roles de base de datos diferenciados:
- **Rol_Administrador:** acceso y control total del esquema DDL/DML.
- **Rol_Vendedor:** permisos de consulta en catálogo/clientes e inserción en ventas y detalle.
- **Rol_Bodeguero:** permisos de consulta en productos y registro en compras/entradas de stock.

**RNF-02 (Arquitectura e Integración Web):** La interfaz web debe estructurarse bajo arquitectura en capas (separando la conexión a la base de datos de la interfaz de usuario) y utilizar consultas parametrizadas para mitigar vulnerabilidades de inyección SQL.

**RNF-03 (Rendimiento e Integridad Transaccional):** La base de datos en MySQL debe operar bajo el motor de almacenamiento InnoDB para asegurar propiedades ACID (Atomicidad, Consistencia, Aislamiento y Durabilidad).

**RNF-04 (Concurrencia en Operaciones de Stock):** Las operaciones que modifican el stock (venta y recepción de compra) deben ejecutarse dentro de una transacción con bloqueo a nivel de fila (SELECT ... FOR UPDATE o equivalente en InnoDB), a fin de evitar condiciones de carrera cuando dos operaciones concurrentes afectan el mismo producto.

---

## 5. Reglas de Negocio (RN)

**RN-01 (Restricción de Eliminación):** No se puede eliminar a un cliente ni a un empleado si poseen registros de ventas o transacciones históricas vinculadas.

**RN-02 (Validación de Stock Disponible):** No se puede concretar una venta si la cantidad solicitada supera el stock actual disponible del producto en inventario.

**RN-03 (Actualización Automática de Stock):** El stock de un producto se actualizará de forma automática, mediante trigger a nivel de base de datos, tras registrar una venta (decremento) o tras confirmar una recepción de compra (incremento).

**RN-04 (Validez del Precio de Venta):** El precio de venta de cualquier producto debe ser un valor positivo y mayor a cero (CHECK (precio_venta > 0)).

**RN-05 (Venta con Detalle Obligatorio):** Toda venta debe contener al menos un producto registrado en su detalle para considerarse válida.

**RN-06 (Unicidad de Identificación Vehicular):** El VIN y el número de motor de una motocicleta no pueden repetirse en el sistema; cada valor debe ser único a nivel de base de datos.

---

## 6. Alcance del Modelo de Datos

El diseño conceptual y relacional se basa estrictamente en 8 entidades principales:

| Entidad | Rol en el modelo |
|---|---|
| SUCURSAL | Punto físico de operación; agrupa empleados y ventas. |
| EMPLEADO | Personal asociado a una sucursal; autoriza compras o vende. |
| CLIENTE | Comprador registrado en el catálogo de clientes. |
| VENTA | Encabezado de la transacción de venta (factura). |
| PRODUCTO | Ítem comercializado, con stock y precio. |
| CATEGORIA | Clasificación del producto. |
| COMPRA | Encabezado de la transacción de compra a proveedor. |
| PROVEEDOR | Origen de la mercadería adquirida. |

A partir de estas 8 entidades se derivan dos entidades asociativas para resolver las relaciones N:M señaladas en RD-02: **CONTIENE** (detalle de venta) y **DETALLA** (detalle de compra). Adicionalmente, se evaluará una entidad o atributos específicos para el registro serializado de VIN/número de motor (RF-06), según la decisión de modelado del equipo.

---

## 7. Plan de Carga de Datos de Prueba

Para la fase de carga de datos (DML) se poblará un **mínimo de 50 registros por tabla principal**, en cumplimiento con el requisito mínimo del enunciado del curso.

---

## 8. Fuera de Alcance

Los siguientes puntos quedan explícitamente excluidos del alcance de este proyecto:

- Integración con pasarelas de pago electrónico con tarjetas.
- Facturación electrónica directa vía Web Service con la SAT.