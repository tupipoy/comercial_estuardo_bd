# Registro de Apoyo con Inteligencia Artificial - Entrega 3

**Proyecto:** Sistema de Gestión de Ventas, Compras e Inventario  
**Empresa:** Comercial Estuardo  
**Etapa:** Entrega 3 — Desarrollo Avanzado, Seguridad, Procedimientos y Aplicación Web  
**Periodo evaluado:** 19 al 29 de septiembre de 2026

---

## Propósito del Documento

El presente registro tiene como finalidad dejar evidencia del uso de herramientas de inteligencia artificial durante las actividades correspondientes a la **Entrega 3** del proyecto.

Estas herramientas fueron utilizadas como apoyo para analizar código, plantear posibles soluciones, revisar consultas SQL, detectar errores, proponer estructuras de módulos y facilitar la elaboración de documentación técnica.

La implementación definitiva, las decisiones de diseño, las pruebas, los ajustes y la validación de los resultados permanecieron bajo responsabilidad del equipo de desarrollo.

---

## Historial de Actividades

| Fecha | Tarea desarrollada | Uso de Inteligencia Artificial | Actividad realizada por el equipo |
|---|---|---|---|
| 19/09/2026 | Análisis del estado del proyecto | Se utilizó IA para revisar el avance existente y contrastarlo con los requisitos de la Entrega 3. | Se inspeccionó el repositorio y se definieron las tareas prioritarias. |
| 20/09/2026 | Ajustes en la estructura del repositorio | Se consultaron recomendaciones para mejorar `.gitignore`, `.env.example` y la organización general del proyecto. | Se aplicaron los cambios seleccionados y se verificaron mediante Git. |
| 21/09/2026 | Revisión de autenticación | Se analizó con apoyo de IA el manejo de credenciales, contraseñas y sesiones. | Se incorporó `password_hash`, manejo de sesiones y validación de usuarios. |
| 22/09/2026 | Desarrollo de Productos | Se utilizaron sugerencias para organizar formularios, rutas y consultas SQL parametrizadas. | El módulo fue adaptado a la estructura de la tabla `PRODUCTO` y posteriormente probado. |
| 22/09/2026 | Desarrollo de Clientes | Se solicitó apoyo para definir la estructura inicial y reglas de validación. | Se desarrollaron funciones de registro, consulta, modificación y desactivación lógica. |
| 23/09/2026 | Preparación de datos de prueba | Se utilizó IA para revisar la organización de datos y relaciones entre entidades. | Los registros fueron ajustados según las restricciones y llaves foráneas existentes. |
| 24/09/2026 | Creación de vistas SQL | Se analizaron posibles vistas útiles para inventario, productos y ventas. | Las vistas seleccionadas fueron implementadas y probadas en MySQL Workbench. |
| 24/09/2026 | Implementación de triggers | Se utilizó IA para revisar reglas relacionadas con control de existencias. | Se configuraron y probaron triggers para validar y descontar stock. |
| 25/09/2026 | Desarrollo de procedimientos almacenados | Se solicitaron propuestas para organizar transacciones de compras y ventas. | Los procedimientos fueron modificados, ejecutados y comprobados en MySQL. |
| 25/09/2026 | Configuración de roles | Se analizaron alternativas para distribuir privilegios según las funciones de los usuarios. | Los roles fueron creados y sus permisos se comprobaron mediante `SHOW GRANTS`. |
| 26/09/2026 | Restricción de rutas en Flask | Se revisaron estrategias para limitar rutas según el perfil del usuario. | Se implementaron permisos para Administrador, Vendedor y Bodega y se verificaron respuestas HTTP 200 y 403. |
| 27/09/2026 | Integración del módulo de Ventas | Se utilizó IA para revisar la comunicación entre Flask, procedimientos y triggers. | Se completó la funcionalidad de ventas y se validó la actualización automática del inventario. |
| 28/09/2026 | Integración del módulo de Compras | Se analizaron propuestas para organizar el flujo de compra y conexión con procedimientos almacenados. | Se conectaron productos, proveedores y actualización de existencias. |
| 28/09/2026 | Desarrollo de Proveedores | Se solicitaron sugerencias para la organización de rutas y formularios. | Se desarrolló el CRUD y se relacionó con el módulo de Compras. |
| 29/09/2026 | Ejecución de pruebas | La IA permitió plantear diferentes escenarios funcionales y de seguridad. | Se ejecutaron pruebas y se compararon los resultados obtenidos con los esperados. |
| 29/09/2026 | Preparación de documentación | Se utilizó IA como apoyo para ordenar y mejorar la presentación de documentos técnicos. | Se revisaron la bitácora, matriz de trazabilidad, certificación y documentación del avance web. |

---

## Formas de Uso de la IA

Durante esta etapa, la inteligencia artificial se utilizó como herramienta de consulta y apoyo técnico.

Las principales actividades realizadas con asistencia de IA fueron:

1. Análisis de código existente.
2. Propuesta de estructuras de programación.
3. Interpretación de mensajes de error.
4. Revisión de sentencias SQL.
5. Orientación sobre procedimientos almacenados.
6. Revisión de triggers.
7. Análisis de roles y permisos.
8. Recomendaciones relacionadas con seguridad.
9. Diseño de posibles casos de prueba.
10. Organización de documentación técnica.

Ninguna propuesta fue incorporada de manera automática al proyecto.

Antes de utilizar cualquier sugerencia, el equipo verificó su compatibilidad con la estructura real del sistema y realizó los ajustes necesarios.

---

## Distribución del Trabajo

La Entrega 3 fue desarrollada mediante trabajo directo del equipo combinado con herramientas de inteligencia artificial utilizadas como asistencia.

De forma aproximada, la distribución considerada fue:

**50% asistencia mediante herramientas de inteligencia artificial**  
**50% implementación, revisión, pruebas y validación por parte del equipo**

El porcentaje correspondiente a IA se relaciona principalmente con orientación, revisión, generación de ideas iniciales y explicación de posibles soluciones.

Por su parte, el equipo se encargó directamente de:

- configurar el entorno de desarrollo;
- ejecutar scripts SQL;
- implementar y adaptar código;
- establecer la comunicación entre Flask y MySQL;
- realizar pruebas funcionales;
- corregir errores detectados;
- validar roles y privilegios;
- verificar controles de seguridad;
- administrar cambios mediante Git;
- confirmar el funcionamiento final.

---

## Áreas Técnicas Apoyadas con IA

### Autenticación y Seguridad

La inteligencia artificial fue utilizada como referencia para revisar aspectos relacionados con el manejo de contraseñas y sesiones.

Se implementó almacenamiento mediante hash utilizando Werkzeug y se realizaron los ajustes necesarios para mantener compatibilidad con la versión de Python utilizada.

El equipo comprobó el funcionamiento del inicio de sesión, cierre de sesión y protección de rutas.

---

### Base de Datos

Se utilizó IA como apoyo en la revisión de los siguientes elementos:

- consultas SQL;
- vistas;
- triggers;
- procedimientos almacenados;
- roles;
- privilegios;
- relaciones entre entidades.

Los scripts definitivos fueron ejecutados y comprobados en MySQL Workbench.

---

### Aplicación Web

La IA se utilizó principalmente para revisar la estructura inicial de distintos módulos:

- Productos;
- Clientes;
- Proveedores;
- Ventas;
- Compras.

La adaptación definitiva de rutas, formularios, consultas y reglas de acceso fue realizada por el equipo.

---

### Pruebas del Sistema

La inteligencia artificial permitió generar propuestas de escenarios de prueba.

El equipo realizó directamente verificaciones sobre:

- autenticación;
- restricciones de acceso;
- operaciones CRUD;
- registro de ventas;
- registro de compras;
- control de inventario;
- funcionamiento de triggers;
- ejecución de procedimientos almacenados.

---

## Incidencias Encontradas Durante el Desarrollo

Durante la implementación se presentaron diferentes situaciones que requirieron correcciones y ajustes.

Las principales fueron:

1. La tabla `EMPLEADO` inicialmente no contaba con el campo `password_hash`.
2. El algoritmo de hash configurado al inicio presentó incompatibilidades con la versión de Python disponible.
3. La tabla `PRODUCTO` necesitó incorporar el campo `precio_costo`.
4. Fue necesario comprobar la existencia de los triggers antes de habilitar las operaciones de venta.
5. Las pruebas del módulo de Compras requerían contar previamente con proveedores activos.
6. Algunas propuestas generadas inicialmente debieron modificarse para coincidir con los nombres y estructuras reales de las tablas.

La inteligencia artificial ayudó a evaluar alternativas, pero las soluciones definitivas fueron implementadas y verificadas por el equipo.

---

## Herramientas y Métodos de Validación

Para comprobar el correcto funcionamiento de la Entrega 3 se utilizaron los siguientes mecanismos:

- MySQL Workbench.
- `SELECT`.
- `SHOW TRIGGERS`.
- `SHOW GRANTS`.
- `SHOW PROCEDURE STATUS`.
- Pruebas de autenticación.
- Pruebas de cierre de sesión.
- Comprobación de roles.
- Validación de respuestas HTTP 200.
- Validación de respuestas HTTP 403.
- Creación de registros.
- Actualización de registros.
- Desactivación lógica.
- Registro de ventas.
- Registro de compras.
- Comprobación de existencias.
- `git diff --check`.
- Inspección manual del código.

---

## Uso Responsable de Inteligencia Artificial

La IA fue utilizada únicamente como herramienta de soporte para complementar el trabajo técnico del equipo.

Cada propuesta fue revisada antes de integrarse al proyecto. Las sugerencias que no coincidían con la arquitectura, las tablas o las necesidades reales del sistema fueron corregidas o descartadas.

Antes de aceptar una modificación se verificó:

1. compatibilidad con MySQL;
2. correspondencia con el modelo de datos;
3. mantenimiento de la integridad referencial;
4. funcionamiento adecuado desde Flask;
5. cumplimiento de permisos y restricciones;
6. posibilidad de reproducir los resultados mediante pruebas.

---

## Integrantes Responsables

| Integrante | Responsabilidad |
|---|---|
| Elvin Miranda | Desarrollo Web, integración, pruebas y validación |
| Carlos Ochoa | Base de Datos, documentación y validación SQL |
| Elvin y Carlos | Control de versiones, pruebas y revisión general |

---

## Resultado Final

El uso de inteligencia artificial facilitó distintas actividades de la Entrega 3, principalmente en la revisión de código, análisis de errores, orientación técnica, elaboración de propuestas y organización de documentación.

A pesar de utilizar estas herramientas como apoyo, la implementación, adaptación y verificación de las soluciones fue realizada directamente por los integrantes del proyecto.

De esta manera, el trabajo realizado corresponde a un proceso colaborativo entre herramientas de asistencia basadas en inteligencia artificial y el desarrollo técnico efectuado por el equipo.