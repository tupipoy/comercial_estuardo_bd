# Requerimientos del Sistema: Comercial Estuardo
**Proyecto:** Sistema de Gestión de Ventas, Compras e Inventario  
**Documento:** Entrega 1 - Especificación de Requerimientos del Sistema  
**Fecha:** Agosto 2026  

---

## 1. Introducción
El presente documento detalla la especificación de requerimientos funcionales, requerimientos de datos, reglas de negocio y restricciones técnicas para la base de datos de **Comercial Estuardo**. Su objetivo es servir de base formal para el modelado conceptual (Diagrama Entidad-Relación en Notación Chen), el diseño lógico normalizado en 3FN y la posterior implementación en MySQL.

---

## 2. Requerimientos Funcionales (RF)

### Módulo de Sucursales y Personal
* **RF-01 (Gestión de Sucursales):** El sistema debe registrar y administrar la información de las sucursales físicas de la empresa (`id_sucursal`, nombre, dirección, teléfono, municipio).
* **RF-02 (Gestión de Empleados):** El sistema debe registrar los datos del personal (`id_empleado`, CUI/DPI, nombre, apellido, cargo/puesto, teléfono, correo, fecha de ingreso) y asociar obligatoriamente a cada empleado con la sucursal en la que labora.

### Módulo de Clientes
* **RF-03 (Registro y Directorio de Clientes):** El sistema debe permitir la creación y mantenimiento del catálogo de clientes, almacenando su código único (`id_cliente`), identificación tributaria (NIT o DPI), nombres, apellidos, teléfono, correo electrónico y dirección.

### Módulo de Inventarios y Productos
* **RF-04 (Categorización de Productos):** El sistema debe organizar el catálogo en categorías (`id_categoria`, nombre de categoría, descripción), tales como Motocicletas, Repuestos, Lubricantes y Equipo de Protección.
* **RF-05 (Catálogo General de Productos):** El sistema debe registrar cada producto comercializado (`id_producto`, código de barra, nombre, descripción técnica/serie, precio de venta, stock actual y stock mínimo).
* **RF-06 (Control y Alertas de Stock):** El sistema debe permitir consultar existencias en tiempo real y alertar cuando el stock actual de un producto sea igual o menor a su stock mínimo definido.

### Módulo de Compras y Proveedores
* **RF-07 (Gestión de Proveedores):** El sistema debe almacenar el directorio de proveedores autorizados (`id_proveedor`, NIT, razón social, contacto, teléfono, dirección).
* **RF-08 (Registro de Órdenes de Compra):** El sistema debe registrar las compras de mercadería ingresadas (`id_compra`, número de orden, fecha de compra, total de compra, estado de recepción), vinculando al proveedor que suministra y al empleado que autoriza/recibe.
* **RF-09 (Detalle de Compra - Relación N:M):** El sistema debe permitir registrar múltiples productos en una misma compra, almacenando la cantidad recibida, el costo unitario de adquisición y el subtotal calculado por línea.

### Módulo de Facturación y Ventas
* **RF-10 (Emisión de Ventas):** El sistema debe generar ventas (`id_venta`, serie de factura, número correlativo, fecha de emisión, total de venta, estado), asociando al cliente comprador, al vendedor asignado y a la sucursal donde se concreta la operación.
* **RF-11 (Detalle de Venta - Relación N:M):** El sistema debe permitir registrar múltiples productos por factura, almacenando la cantidad vendida, el precio unitario pactado, descuento aplicable y subtotal por producto.

---

## 3. Requerimientos de Datos e Integridad (RD)

* **RD-01 (Claves Primarias e Identificación):** Todas las entidades deben contar con una clave primaria única (`PK` artificial autoincremental). Los valores de CUI/DPI, NIT, código de barras y series/números de factura deben contar con restricción `UNIQUE`.
* **RD-02 (Modelo de 8 Entidades Principales):** El diseño conceptual y relacional debe basarse estrictamente en 8 entidades principales: `SUCURSAL`, `EMPLEADO`, `CLIENTE`, `VENTA`, `PRODUCTO`, `CATEGORIA`, `COMPRA` y `PROVEEDOR`.
* **RD-03 (Resolución de Relaciones N:M):** Se deben resolver formalmente las dos relaciones transaccionales Muchos a Muchos:
  1. `CONTIENE` (Detalle de Venta entre `VENTA` y `PRODUCTO`).
  2. `DETALLA` (Detalle de Compra entre `COMPRA` y `PRODUCTO`).
* **RD-04 (Integridad Referencial y Restricciones):** Todas las llaves foráneas (`FK`) deben definir políticas explícitas de integridad referencial (`ON DELETE RESTRICT` / `ON UPDATE CASCADE`). Se deben implementar al menos 15 restricciones explícitas (`PK`, `FK`, `CHECK`, `UNIQUE`, `NOT NULL`).
* **RD-05 (Datos de Prueba):** El sistema debe prepararse para poblar un mínimo de 50 registros por tabla principal en la fase de carga de datos DML.

---

## 4. Requerimientos No Funcionales (RNF)

* **RNF-01 (Seguridad y Roles en BD):** El sistema debe contar con al menos 3 roles de base de datos diferenciados:
  * `Rol_Administrador`: Acceso y control total del esquema DDL/DML.
  * `Rol_Vendedor`: Permisos de consulta en catálogo/clientes e inserción en ventas y detalle.
  * `Rol_Bodeguero`: Permisos de consulta en productos y registro en compras/entradas de stock.
* **RNF-02 (Arquitectura e Integración Web):** La interfaz web debe estructurarse bajo arquitectura en capas (separando conexión a BD de la interfaz de usuario) y utilizar consultas parametrizadas para mitigar vulnerabilidades de Inyección SQL.
* **RNF-03 (Rendimiento e Integridad Transaccional):** La base de datos en MySQL debe operar bajo el motor de almacenamiento `InnoDB` para asegurar propiedades ACID (Atomicidad, Consistencia, Aislamiento y Durabilidad).

---

## 5. Reglas de Negocio (RN)

* **RN-01:** No se puede eliminar a un cliente ni a un empleado si poseen registros de ventas o transacciones históricas vinculadas.
* **RN-02:** No se puede concretar una venta si la cantidad solicitada supera el stock actual disponible del producto en inventario.
* **RN-03:** El stock de un producto se actualizará de forma automática tras registrar una venta (decremento) o tras confirmar una recepción de compra (incremento).
* **RN-04:** El precio de venta de cualquier producto debe ser un valor positivo y mayor a cero (`CHECK (precio_venta > 0)`).
* **RN-05:** Toda venta debe contener al menos un producto registrado en su detalle para considerarse válida.