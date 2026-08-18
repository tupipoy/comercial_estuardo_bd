# Requerimientos del Sistema: Comercial Estuardo
**Proyecto:** Sistema de Gestión de Ventas e Inventario de Motocicletas  
**Documento:** Entrega 1 - Especificación de Requerimientos  
**Fecha:** Agosto 2026  

---

## 1. Introducción
El presente documento detalla la especificación de requerimientos funcionales, requerimientos de datos, reglas de negocio y restricciones técnicas para la base de datos de **Comercial Estuardo**. Su objetivo es serví de base para la construcción del modelo conceptual (Diagrama Entidad-Relación) y posterior implementación relacional.

---

## 2. Requerimientos Funcionales (RF)

### Módulo de Gestión de Personal y Accesos
* **RF-01 (Gestión de Puestos):** El sistema debe permitir la definición de puestos de trabajo dentro de la empresa (ej. Vendedor, Administrador de Bodega, Gerente) asignando un salario base.
* **RF-02 (Gestión de Empleados):** El sistema debe registrar la información general del personal (DPI, nombres, apellidos, teléfono) y vincularlo obligatoriamente a un puesto de trabajo y asignar un código de empleado único.

### Módulo de Clientes
* **RF-03 (Registro de Clientes):** El sistema debe permitir la gestión de clientes, almacenando su documento de identificación (DPI o NIT), nombres, apellidos, dirección de residencia, teléfono y correo electrónico.

### Módulo de Inventarios y Productos
* **RF-04 (Categorización de Productos):** El sistema debe clasificar la oferta comercial en categorías (ej. Motocicletas de Trabajo, Scooters, Repuestos, Cascos, Aceites).
* **RF-05 (Gestión del Catálogo General):** El sistema debe almacenar el código único del producto, nombre, descripción, precio de venta al público y stock actual disponible.
* **RF-06 (Detalle Específico para Motocicletas):** Para aquellos productos pertenecientes a la categoría de motocicletas, el sistema debe registrar individualmente el número de chasis (VIN), número de motor, color, cilindraje (cc) y año del modelo.

### Módulo de Compras y Proveedores
* **RF-07 (Gestión de Proveedores):** El sistema debe almacenar la información de los proveedores autorizados (NIT, nombre fiscal, contacto principal, teléfono, dirección).
* **RF-08 (Registro de Órdenes de Compra):** El sistema debe registrar las compras realizadas a proveedores, indicando el número de orden, fecha, el empleado responsable de la recepción y el proveedor adjudicado.
* **RF-09 (Detalle de Compra - Reposición):** Permite registrar el desglose de productos ingresados en cada orden de compra, guardando la cantidad adquirida, el precio de costo unitario y recalculando el costo total.

### Módulo de Ventas e Historial
* **RF-10 (Emisión de Ventas):** El sistema debe registrar transacciones de venta asignando un número de factura correlativo, fecha de emisión, cliente comprador y empleado vendedor.
* **RF-11 (Detalle de Venta):** Permite asociar múltiples productos a una misma venta, indicando la cantidad vendida, precio unitario de transacción y subtotal por línea.
* **RF-12 (Asignación de Vehículo):** Al realizar la venta de una motocicleta, el sistema debe permitir la selección explícita del número de chasis (VIN) y número de motor vendido para la emisión de garantías y trámites de placas.

---

## 3. Requerimientos de Datos (RD)

* **RD-01 (Unicidad e Identificación):** Cada entidad debe poseer una clave primaria unívoca (`id_entidad`). Los registros de DPI, NIT, VIN de motocicletas y números de factura no pueden duplicarse.
* **RD-02 (Volumen Mínimo de Entidades):** El modelo debe constar de al menos 8 entidades principales alineadas al proyecto (se incluyen 9: `CLIENTE`, `EMPLEADO`, `PUESTO`, `PROVEEDOR`, `CATEGORIA`, `PRODUCTO`, `MOTOCICLETA`, `VENTA`, `COMPRA`).
* **RD-03 (Relaciones Transaccionales N:M):** El diseño debe modelar correctamente mediante tablas intermedias las relaciones Muchos a Muchos ($N:M$) correspondientes a:
  1. `DETALLE_VENTA` (entre `VENTA` y `PRODUCTO`).
  2. `DETALLE_COMPRA` (entre `COMPRA` y `PRODUCTO`).
* **RD-04 (Integridad Referencial):** Toda clave foránea debe hacer referencia a una clave primaria existente, impidiendo el borrado en cascada descontrolado de datos transaccionales históricos.

---

## 4. Reglas de Negocio (RN)

* **RN-01:** Un cliente no puede ser eliminado del sistema si posee ventas asociadas registradas.
* **RN-02:** Una motocicleta no puede asignarse a una venta si su estado en inventario figura como "Vendida".
* **RN-03:** El stock de un producto no puede ser inferior a 0 tras la realización de una venta.
* **RN-04:** El precio de venta de un producto debe ser mayor al precio de costo registrado en la última compra.