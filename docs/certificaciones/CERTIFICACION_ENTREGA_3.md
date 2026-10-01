# Certificado de Calidad Técnica - Entrega 3

**Proyecto:** Sistema de Gestión de Ventas, Compras e Inventario  
**Empresa:** Comercial Estuardo  
**Fase:** Entrega 3 — Desarrollo Avanzado, Seguridad, Procedimientos y Aplicación Web  
**Fecha:** Septiembre 2026

---

## Declaración de Conformidad

Mediante el presente documento, el equipo de desarrollo deja constancia de que los componentes implementados durante la **Entrega 3** cumplen con los requerimientos técnicos y académicos definidos para esta etapa del sistema.

1. **Carga de Datos y Operaciones DML:** Se prepararon scripts para realizar cargas iniciales y masivas de información sobre las principales entidades del sistema, procurando mantener la integridad referencial y la correcta relación entre los registros.

2. **Vistas SQL:** Se implementaron vistas orientadas a facilitar la consulta del inventario valorizado, identificar productos con existencias reducidas y consultar el detalle de las ventas, reuniendo información proveniente de distintas tablas.

3. **Triggers de Base de Datos:** Se incorporaron los triggers `trg_validar_stock_venta` y `trg_descontar_stock_venta`. Estos permiten verificar la existencia disponible antes de procesar una venta y realizar el descuento automático del inventario una vez registrada la operación.

4. **Procedimientos Almacenados:** Se desarrollaron los procedimientos `sp_registrar_venta` y `sp_registrar_compra`, utilizados para centralizar las operaciones relacionadas con ventas y compras. Su implementación contempla validaciones, manejo de transacciones, actualización del inventario y control de posibles errores.

5. **Roles y Seguridad en la Base de Datos:** Se configuraron los roles `rol_administrador`, `rol_ventas` y `rol_bodega`, asignando permisos específicos de acuerdo con las actividades y responsabilidades correspondientes a cada tipo de usuario.

6. **Autenticación y Control de Acceso:** La aplicación web desarrollada en Flask cuenta con un sistema de inicio de sesión, almacenamiento seguro de contraseñas mediante hash, manejo de sesiones y control de acceso de acuerdo con los perfiles Administrador, Vendedor y Bodega.

7. **Módulos Web Disponibles:** Se implementaron los módulos de Inventario, Productos, Clientes, Proveedores, Ventas y Compras. Cada módulo permite realizar las operaciones correspondientes y aplica restricciones dependiendo del rol del usuario autenticado.

8. **Conexión con MySQL:** Las operaciones de ventas y compras se encuentran vinculadas con los procedimientos almacenados definidos en MySQL, permitiendo que parte de la lógica transaccional y el control del inventario se gestione directamente desde la base de datos.

9. **Pruebas Funcionales Realizadas:** Se llevaron a cabo pruebas sobre el inicio de sesión, permisos de acceso, operaciones CRUD, registro de ventas, validación de existencias y protección de rutas restringidas.

10. **Documentación del Proyecto:** Se realizaron actualizaciones en la documentación de la Entrega 3, incluyendo el avance de la aplicación web, los casos de prueba, la matriz de trazabilidad y el registro correspondiente al uso de herramientas de inteligencia artificial.

11. **Revisión Técnica:** Los módulos desarrollados y los scripts SQL fueron revisados mediante pruebas locales utilizando Flask y MySQL. Asimismo, se utilizó el comando `git diff --check` como apoyo para detectar posibles errores de formato antes de integrar los cambios al repositorio.

---

## Firmas del Equipo

| Nombre del Integrante | Rol / Responsabilidad | Firma / Carné |
|---|---|---|
| Elvin Miranda | Desarrollo Web, Seguridad e Integración SQL | 2690-24-16072 |
| Carlos Ochoa | Base de Datos, DML y Documentación | 2690-23-7592 |
| Elvin, Carlos | Pruebas, Validación Técnica y Control de Versiones | 2690-24-16072 / 2690-23-7592 |