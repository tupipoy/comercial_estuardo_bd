# Certificación de calidad — Entrega 4

**Proyecto:** Sistema de Gestión de Ventas, Compras e Inventario — Comercial Estuardo.
**Fecha de verificación técnica:** 29 de octubre de 2026.
**Versión:** tag `entrega-4`.
**Equipo:** los dos integrantes indicados por el usuario.

Las casillas técnicas se sustentan en el repositorio y las ejecuciones enlazadas. Esta revisión no firma por los estudiantes ni acredita una defensa oral.

- [x] Estructura obligatoria, README, INSTALL y ejemplo de entorno presentes.
- [x] Instalación desde cero con datos y roles comprobada en MySQL temporal.
- [x] Ocho entidades principales con al menos 50 registros de demostración y dos N:M.
- [x] Restricciones, tres roles diferenciados y objetos SQL instalados y probados.
- [x] Casos ejecutados y documentados: 28 pruebas automatizadas en las cuatro suites.
- [x] CRUD de catálogos y cabeceras, operaciones, permisos y conservación de historial verificados.
- [x] Aplicación publicada en Railway con Gunicorn y endpoints protegidos.
- [x] Manuales, diccionario, diagramas, informe y trazabilidad actualizados.
- [x] Consultas parametrizadas, validaciones, CSRF y manejo de errores revisados.
- [x] Sin patrones sensibles conocidos encontrados en la revisión de archivos e historial; secretos y respaldos locales excluidos de Git.
- [x] Bitácora de Entrega 4 e índice consolidado actualizados, distinguiendo validación automática de validación personal.
- [x] Entrega preparada en rama principal y publicada con etiqueta `entrega-4` al cerrar la revisión.
- [ ] Cada integrante ratifica personalmente la declaración de integridad y puede defender las decisiones.
- [ ] El equipo conserva la constancia de aprobación del ER y cualquier autorización organizativa requerida por el catedrático.

## Observaciones de estándares

Las tablas usan UPPER_SNAKE_CASE y las columnas snake_case: se declara la variante frente a S1; no se certifica un renombrado a minúsculas que no ocurrió. Los importes históricos se calculan y mantienen transaccionalmente como decisión de desnormalización controlada frente a S7. Ver [Verificación del enunciado](../entrega-4/ENTREGA4_VERIFICACION_REQUISITOS.md).

## Declaración de integridad académica para ratificación del equipo

Los integrantes deben confirmar que revisaron los cambios, que el apoyo de IA está identificado en la bitácora y que pueden explicar individualmente el diseño, SQL, roles, operaciones y despliegue. Las marcas de aprobación siguientes ya figuraban en el archivo antes de esta revisión; se conservan y no se presentan como nuevas firmas generadas por el agente. No consta una fecha individual de ratificación de esta versión final.

| Integrante | Carné | Aprobación previamente registrada |
|---|---|---|
| Elvin Guillermo Miranda Gómez | 2690-24-16072 | aprobado |
| Juan Carlos Ochoa Samayoa | 2690-23-7592 | aprobado |

Evidencia: [casos](../casos-prueba/CASOS_PRUEBA_ENTREGA_4.md), [estructura instalada](../entrega-4/evidencias/VERIFICACION_ENTREGA4.json), [registro de pruebas](../entrega-4/evidencias/PRUEBAS_ENTREGA4.txt) y [bitácora consolidada](../bitacora-ia/BITACORA_IA_CONSOLIDADA.md).
