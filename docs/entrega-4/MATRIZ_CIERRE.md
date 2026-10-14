# Matriz de cierre — Entrega 4

Estados: ✅ evidencia disponible en el repositorio; 🟡 avance parcial o falta evidencia; 🔴 no implementado/documentado en esta revisión.

| Criterio del enunciado | Estado observado | Acción de cierre |
|---|---|---|
| Aplicación web 100% completa | 🟡 Están implementados Inventario, Productos, Clientes, Proveedores, Compras, Ventas, Sucursal, Empleado y Categoría; falta validación funcional integral. | Ejecutar los casos de aceptación en MySQL y Railway. |
| CRUD para todas las tablas principales | 🟡 CRUD web existe para las entidades principales; detalles de compra/venta son asociativos, se crean transaccionalmente y tienen consulta web de solo lectura. | Confirmar si el criterio también abarca tablas asociativas; si es así, implementar ajustes que mantengan stock, totales y trazabilidad. |
| Compras y ventas completas | 🟡 Formularios y procedimientos mult producto agregados; las ventas usan triggers con `SELECT ... FOR UPDATE` y las compras actualizan stock mediante `UPDATE` InnoDB dentro de la transacción, que toma bloqueos de fila. Falta probar concurrencia y flujos con MySQL, además de validar VIN/motor. | Verificar compras/ventas concurrentes, varias líneas, rollback por stock insuficiente y unicidad de VIN/motor en esquema temporal; confirmar que el bloqueo de `UPDATE` satisface RNF-04. |
| Manual técnico | 🟡 Borrador agregado en `MANUAL_TECNICO.md`. | Completar con configuración y evidencia reales de Railway, respaldo y pruebas. |
| Manual de usuario | 🟡 Borrador agregado en `MANUAL_USUARIO.md`. | Alinear con funciones finales y validar cada flujo. |
| Informe final e integridad | 🟡 Borrador agregado en `INFORME_FINAL.md`. | Actualizar resultados, limitaciones, URL/tag y obtener revisión/firma del equipo. |
| Estándares de aplicación | 🟡 Consultas parametrizadas, validaciones, token CSRF y flags de cookie configurados; falta revisión integrada final. | Probar formularios y sesiones en despliegue de aceptación y revisar manejo de errores. |
| Despliegue Railway + Gunicorn | 🟡 Código, health check y guía preparados; no hay evidencia de publicación. | Configurar servicios, inicializar MySQL remoto y guardar evidencia de aceptación. |
| Instalación limpia y flujos del manual probados | 🟡 Evidencia de Entrega 3 existe en esquema temporal. | Repetir con la versión candidata de Entrega 4 y documentar resultados. |
| Certificación y bitácora consolidada | 🟡 Borrador de certificación Entrega 4 y bitácora iniciados; las firmas y validaciones del equipo siguen pendientes. | Completar casillas, firmar y consolidar evidencia de las cuatro entregas. |
| Tag Git `entrega-4` y participación del equipo | 🔴 Aún no existe tag. | Revisar commits de ambos integrantes y crear el tag al aprobar la versión final. |
