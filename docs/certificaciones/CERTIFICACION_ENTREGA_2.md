# Certificado de Calidad Técnica - Entrega 2
**Proyecto:** Sistema de Gestión de Ventas, Compras e Inventario  
**Empresa:** Comercial Estuardo  
**Fase:** Entrega 2 — Diseño Lógico, Normalización y Esquema Físico DDL  
**Fecha:** Septiembre 2026  

---

### Declaración de Conformidad
El equipo de desarrollo certifica que los entregables correspondientes a la **Entrega 2** cumplen rigurosamente con los estándares técnicos y académicos establecidos:

1. **Normalización (3FN):** El esquema lógico de 10 tablas fue derivado formalmente a partir del Diagrama Chen, garantizando atomicidad (1FN), dependencia funcional completa (2FN) y eliminación de dependencias transitivas (3FN).
2. **Diccionario de Datos:** Se detallan todas las entidades, tipos de datos compatibles con MySQL 8.0, llaves primarias, llaves foráneas y descripciones funcionales.
3. **Script DDL (`sql/ddl/01_schema.sql`):** Implementa el motor de almacenamiento transaccional `InnoDB`, codificación `utf8mb4`, orden estricto de dependencias por claves foráneas y más de 15 restricciones explícitas (`PK`, `FK`, `UNIQUE`, `CHECK`, `NOT NULL`).
4. **Validación de Ejecución:** El script fue probado en entorno MySQL local sin generar advertencias ni errores de sintaxis.

---

### Firmas del Equipo

| Nombre del Integrante | Rol / Responsabilidad | Firma |
| :--- | :--- | :---: |
| Elvin Miranda | Modelado Lógico y 3FN | 2690-24-16072|
| Carlos Ochoa | Diccionario de Datos y DDL | 2690-23-7592 |
| Elvin, Carlos | Validación SQL y Control de Versiones | 2690-24-16072 |