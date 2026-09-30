# Certificado de Calidad Técnica - Entrega 3

**Proyecto:** Sistema de Gestión de Ventas, Compras e Inventario  
**Empresa:** Comercial Estuardo  
**Fase:** Entrega 3 — Implementación Avanzada, Seguridad, Procedimientos y Aplicación Web  
**Fecha:** Septiembre 2026

---

### Declaración de Conformidad

El equipo de desarrollo certifica que los entregables correspondientes a la **Entrega 3** cumplen con los estándares técnicos y académicos establecidos para esta fase:

1. **Datos de Prueba y Operaciones DML:** Se incorporaron scripts de carga inicial y carga masiva de datos para las entidades principales del sistema, manteniendo integridad referencial y coherencia entre registros relacionados.

2. **Vistas SQL:** Se implementaron vistas para facilitar consultas de inventario valorizado, productos con stock crítico y ventas detalladas, permitiendo centralizar información proveniente de varias tablas.

3. **Triggers:** Se implementaron los triggers `trg_validar_stock_venta` y `trg_descontar_stock_venta`, encargados de impedir ventas con inventario insuficiente y actualizar automáticamente las existencias después de registrar una venta.

4. **Procedimientos Almacenados:** Se desarrollaron los procedimientos `sp_registrar_venta` y `sp_registrar_compra`, los cuales encapsulan operaciones transaccionales de ventas y compras, incluyendo validaciones, actualización de inventario y manejo de errores mediante transacciones.

5. **Seguridad y Roles de Base de Datos:** Se configuraron los roles `rol_administrador`, `rol_ventas` y `rol_bodega`, cada uno con privilegios diferenciados según sus responsabilidades dentro del sistema.

6. **Autenticación y Control de Acceso Web:** La aplicación Flask incorpora inicio de sesión mediante contraseñas almacenadas con hash, manejo de sesiones y restricciones de acceso según los cargos Administrador, Vendedor y Bodega.

7. **Módulos Web Implementados:** Se encuentran funcionales los módulos de Inventario, Productos, Clientes, Proveedores, Ventas y Compras, incluyendo operaciones CRUD y restricciones de acceso según el rol correspondiente.

8. **Integración con la Base de Datos:** Las operaciones de ventas y compras se encuentran integradas con los procedimientos almacenados de MySQL, permitiendo mantener la lógica transaccional y el control del inventario desde la base de datos.

9. **Pruebas Funcionales:** Se realizaron pruebas de autenticación, permisos por rol, operaciones CRUD, registro de ventas, validación de stock y acceso restringido a rutas no autorizadas.

10. **Documentación y Trazabilidad:** Se actualizó la documentación correspondiente a la Entrega 3, incluyendo avance web, matriz de trazabilidad, casos de prueba y bitácora del uso de inteligencia artificial.

11. **Validación Técnica:** Los scripts SQL y módulos desarrollados fueron revisados en el entorno local de MySQL y Flask. También se utilizó `git diff --check` para detectar posibles problemas de formato antes de incorporar cambios al repositorio.

---

### Firmas del Equipo

| **Nombre del Integrante** | **Rol / Responsabilidad** | **Firma / Carné** |
| ------------------------- | ------------------------- | ----------------- |
| Elvin Miranda | Desarrollo Web, Seguridad e Integración SQL | 2690-24-16072 |
| Carlos Ochoa | Base de Datos, DML y Documentación | 2690-23-7592 |
| Elvin, Carlos | Pruebas, Validación Técnica y Control de Versiones | 2690-24-16072 / 2690-23-7592 |