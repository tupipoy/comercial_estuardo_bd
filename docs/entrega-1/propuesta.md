# Propuesta del Proyecto: Sistema de Gestión de Ventas, Compras e Inventario
*Empresa:* Comercial Estuardo  
*Documento:* Entrega 1 - Propuesta Técnica, Ficha Comercial y Definición del Problema  
*Fecha:* Agosto 2026  

---

## 1. Ficha Técnica y Perfil Comercial de la Empresa

| Campo | Detalle Institucional |
| :--- | :--- |
| *Nombre Comercial* | Comercial Estuardo |
| *Giro Comercial* | Venta y distribución de motocicletas, repuestos, lubricantes, cascos y accesorios. |
| *Identificación Tributaria (NIT)* | 10154112-0 |
| *Dirección Principal* | 1ra Avenida 1-27, Zona 3, San Juan Ostuncalco, Quetzaltenango, Guatemala |
| *Teléfono de Contacto* | +(502) 4267-1877 |
| *Correo Electrónico* | comercialestuardo@gmail.com |
| *Horario de Atención* | • Lunes a Sábado: 08:00 - 18:00 hrs<br>• Domingo: 08:00 - 13:00 hrs |

---

## 2. Contexto Operativo y Antecedentes
Comercial Estuardo es una empresa comercializadora ubicada en el municipio de San Juan Ostuncalco, Quetzaltenango, dedicada a la venta de motocicletas de diversos modelos y cilindrajes, así como a la distribución de repuestos de alta rotación, lubricantes y equipo de protección para motoristas.

Con el aumento en el volumen de ventas y el crecimiento en el catálogo de productos y sucursales, los métodos operativos tradicionales basados en registros físicos y hojas de cálculo en Excel han comenzado a generar atrasos e inconsistencias operativas en el control diario del negocio.

---

## 3. Definición de la Problemática
El modelo operativo manual actual presenta deficiencias que impactan directamente en el control administrativo y la atención al cliente:

1. *Riesgo en la Trazabilidad de Motocicletas (VIN y Número de Motor):*  
   Cada motocicleta vendida requiere el registro exacto y obligatorio de su número de chasis (VIN) y número de motor vinculado a la factura y al cliente, lo cual resulta difícil de rastrear y validar en hojas de cálculo al momento de gestionar trámites legales de placas y garantías.
2. *Descoordinación de Inventario y Stock:*  
   No existe una actualización automática y en tiempo real de las existencias cuando se concreta una venta o cuando ingresa un pedido de mercadería, provocando discrepancias entre el inventario físico y el registrado.
3. *Falta de Trazabilidad en Compras a Proveedores:*  
   Las recepciones de productos no se enlazan de forma directa con los comprobantes de compra ni con los costos unitarios pactados con distribuidores mayoristas.
4. *Carencia de Historial Centralizado de Clientes:*  
   Dificultad para consultar de forma ágil el historial de compras de clientes recurrentes y el rendimiento en ventas por empleado.
5. *Vulnerabilidad e Inconsistencia de Datos:*  
   El uso de archivos aislados propicia la duplicidad de registros, errores en precios y la ausencia de controles de acceso y seguridad para el personal.

---

## 4. Propuesta de Solución Tecnológica
Se propone el diseño, normalización e implementación de una *Base de Datos Relacional en MySQL, estructurada estrictamente bajo la **Tercera Forma Normal (3FN)[cite: 3], integrada a una **interfaz web modular* para la administración de las operaciones de Comercial Estuardo[cite: 3].

### Estructura del Sistema (8 Entidades Principales y 2 Relaciones N:M):
* *SUCURSAL:* Gestión de puntos de venta y agencias.
* *EMPLEADO:* Control del personal asignado por sucursal.
* *CLIENTE:* Directorio unificado con identificación tributaria (NIT / DPI).
* *VENTA:* Emisión y control de facturación y comprobantes.
* *PRODUCTO:* Catálogo de motocicletas, repuestos y accesorios con control de stock actual y mínimo.
* *CATEGORIA:* Clasificación organizada de los productos.
* *COMPRA:* Registro de órdenes y recepción de mercadería.
* *PROVEEDOR:* Directorio de distribuidores mayoristas e importadores.
* *Relaciones $N:M$ con atributos propios:* CONTIENE (Detalle de Venta) y DETALLA (Detalle de Compra), calculando cantidades, precios unitarios, descuentos y subtotales.

---

## 5. Objetivos del Proyecto

### Objetivo General
Diseñar, implementar y documentar un sistema de base de datos relacional normalizado en 3FN para Comercial Estuardo, que centralice y automatice la gestión de inventario, compras y facturación de ventas, garantizando la integridad de los datos, seguridad por roles y conectividad con una interfaz web[cite: 3].

### Objetivos Específicos
1. *Modelado y Normalización:* Desarrollar el diagrama Entidad-Relación bajo notación Chen formal (8+ entidades y 2 relaciones $N:M$)[cite: 3] y derivar el esquema relacional en 3FN[cite: 3].
2. *Implementación SQL con Estándares de Calidad:* Construir scripts DDL en MySQL con más de 15 restricciones explícitas (PK, FK, UNIQUE, CHECK, NOT NULL)[cite: 3], integridad referencial (ON DELETE / ON UPDATE)[cite: 3] y carga DML de prueba con más de 50 registros por tabla[cite: 3].
3. *Lógica de Negocio y Seguridad:* Programar al menos 2 triggers[cite: 3], 2 procedimientos almacenados[cite: 3] y configurar al menos 3 roles de usuario en base de datos con privilegios diferenciados[cite: 3].
4. *Desarrollo Web Progresivo:* Implementar una interfaz web conectada a MySQL con arquitectura por capas y consultas parametrizadas[cite: 3], con entregas graduales (30% en Entrega 2[cite: 3], 70% en Entrega 3[cite: 3], 100% en Entrega 4[cite: 3]).
5. *Aseguramiento de Calidad:* Respaldar cada entrega con bitácoras de herramientas de IA[cite: 3], casos de prueba[cite: 3] y certificados de calidad firmados en el repositorio Git[cite: 3].

---

## 6. Alcance y Delimitación
* *Incluye:* Modelado formal, scripts SQL completos, seguridad por roles, interfaz web de consumo de BD, pruebas de persistencia y manuales técnico/usuario[cite: 3].
* *Excluye:* Integración con pasarelas de pago electrónico con tarjetas ni facturación electrónica directa vía Web Service con SAT para esta fase del proyecto.