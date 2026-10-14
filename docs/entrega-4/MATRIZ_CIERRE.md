# Matriz de cierre — Entrega 4

Estados: ✅ evidencia disponible en el repositorio; 🟡 avance parcial o falta evidencia; 🔴 no implementado/documentado en esta revisión.

| Criterio del enunciado | Estado observado | Acción de cierre |
|---|---|---|
| Aplicación web 100% completa | 🟡 Están implementados Inventario, Productos, Clientes, Proveedores, Compras, Ventas, Sucursal, Empleado y Categoría; falta validación funcional integral. | Ejecutar los casos de aceptación en MySQL y Railway. |
| CRUD para todas las tablas principales | 🟡 CRUD web existe para catálogos; detalles de compra/venta se crean transaccionalmente y ya tienen consulta web de solo lectura. | Confirmar con el catedrático que las tablas de detalle, al ser asociativas históricas, no requieren edición/borrado aislado. |
| Compras y ventas completas | 🟡 Formularios y procedimientos mult producto agregados; falta ejecutar casos con MySQL y validar VIN/motor para motocicletas. | Probar varias líneas, rollback por stock insuficiente y unicidad de VIN/motor en esquema temporal. |
| Manual técnico | 🟡 Borrador agregado en `MANUAL_TECNICO.md`. | Completar con configuración y evidencia reales de Railway, respaldo y pruebas. |
| Manual de usuario | 🟡 Borrador agregado en `MANUAL_USUARIO.md`. | Alinear con funciones finales y validar cada flujo. |
| Informe final e integridad | 🟡 Borrador agregado en `INFORME_FINAL.md`. | Actualizar resultados, limitaciones, URL/tag y obtener revisión/firma del equipo. |
| Estándares de aplicación | 🟡 Consultas parametrizadas, validaciones, token CSRF y flags de cookie configurados; falta revisión integrada final. | Probar formularios y sesiones en despliegue de aceptación y revisar manejo de errores. |
| Despliegue Railway + Gunicorn | 🟡 Código, health check y guía preparados; no hay evidencia de publicación. | Configurar servicios, inicializar MySQL remoto y guardar evidencia de aceptación. |
| Instalación limpia y flujos del manual probados | 🟡 Evidencia de Entrega 3 existe en esquema temporal. | Repetir con la versión candidata de Entrega 4 y documentar resultados. |
| Certificación y bitácora consolidada | 🟡 Borrador de certificación Entrega 4 y bitácora iniciados; las firmas y validaciones del equipo siguen pendientes. | Completar casillas, firmar y consolidar evidencia de las cuatro entregas. |
| Tag Git `entrega-4` y participación del equipo | 🔴 Aún no existe tag. | Revisar commits de ambos integrantes y crear el tag al aprobar la versión final. |
