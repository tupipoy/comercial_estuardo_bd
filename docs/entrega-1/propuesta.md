# Propuesta del Proyecto: Sistema de Gestión de Ventas e Inventario de Motocicletas
**Empresa:** Comercial Estuardo  
**Documento:** Entrega 1 - Propuesta Técnica  
**Fecha:** Agosto 2026  

---

## 1. Contexto Institucional y Antecedentes
*Comercial Estuardo* es una empresa guatemalteca dedicada a la comercialización, importación y distribución de motocicletas de diversos cilindrajes, así como de repuestos, cascos y accesorios relacionados. A lo largo de su trayectoria, la empresa ha incrementado su volumen de ventas e inventario, lo que ha puesto de manifiesto las limitaciones de sus procesos operativos actuales.

Actualmente, el control operativo se realiza de forma manual y mediante hojas de cálculo descentralizadas, lo que genera inconsistencias en la información financiera, retrasos en la atención al cliente y falta de control sobre las existencias físicas.

---

## 2. Definición del Problema
La ausencia de un sistema de base de datos relacional centralizado genera las siguientes problemáticas críticas dentro de Comercial Estuardo:

* **Pérdida de Trazabilidad en Series Únicas (VIN y Motor):** A diferencia de otros productos, las motocicletas requieren la identificación obligatoria e inequívoca de su número de chasis (VIN) y número de motor. El registro manual actual dificulta la asociación exacta de una motocicleta vendida con su comprador, afectando la emisión de garantías y el trámite legal de placas.
* **Desfases e Inconsistencias en Inventario:** No existe un mecanismo en tiempo real que descuente el stock disponible al momento de efectuar una venta o que registre automáticamente el reabastecimiento tras una compra a proveedores.
* **Procesamiento de Ventas e Historial Desconectado:** La falta de una entidad centralizada de clientes impide consultar el historial de compras, saldos pendientes (ventas al crédito) y la efectividad de los vendedores.
* **Riesgo de Redundancia y Corrupción de Datos:** La duplicación de información en hojas de cálculo aisladas genera registros contradictorios de precios, clientes e inventario.

---

## 3. Propuesta de Solución
Se propone el diseño e implementación de una **Base de Datos Relacional robusta en MySQL**, estructurada bajo la **Tercera Forma Normal (3FN)**, orientada a automatizar y centralizar la gestión operativa de Comercial Estuardo. 

El sistema organizará los datos en entidades clave (Clientes, Empleados, Puestos, Proveedores, Categorías, Productos, Motocicletas, Compras y Ventas) permitiendo:
1. Registrar la información de cada venta y compra con sus respectivos detalles en relaciones $N:M$.
2. Mantener un control individualizado de las motocicletas en inventario mediante sus atributos únicos (VIN, motor, color, cilindraje, modelo).
3. Garantizar la integridad referencial de los datos y restringir acciones según el rol del usuario dentro del sistema.

---

## 4. Objetivos del Proyecto

### Objetivo General
Diseñar e implementar una base de datos relacional normalizada (3FN) que optimice y centralice el control de inventarios, compras y ventas para la empresa Comercial Estuardo, garantizando la integridad de la información y la trazabilidad de las motocicletas vendidas.

### Objetivos Específicos
1. **Garantizar la Trazabilidad:** Implementar un esquema de datos que vincule de forma unívoca cada número de chasis (VIN) y motor con la venta y el cliente correspondiente.
2. **Normalizar el Esquema de Datos:** Diseñar la estructura cumpliendo estrictamente con la 3FN, incluyendo un mínimo de 8 entidades principales y al menos 2 relaciones Muchos a Muchos ($N:M$).
3. **Optimizar las Operaciones de Compra e Inventario:** Registrar la entrada de mercadería mediante la relación con proveedores y la actualización de existencias de productos.
4. **Documentar el Proceso Operativo:** Mantener la evidencia de desarrollo en el repositorio Git oficial, incluyendo la Bitácora de Agentes de IA y la Certificación de Calidad solicitadas.

---

## 5. Alcance del Proyecto
El proyecto abarcará el análisis de requerimientos, el modelado conceptual (Diagrama Chen), el diseño lógico (3FN), la implementación en script DDL/DML de MySQL, y la creación de una interfaz web funcional para la interacción con la base de datos.
