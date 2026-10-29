# Verificación del enunciado — Entrega 4

**Fecha:** 29/10/2026. **Fuente:** `Proyecto - Base de datos (7).pdf`, 13 páginas, SHA-256 `ff3e32713c1bf239f21f82db4d14552648f016dbf90b93dec214e00794668f16`. Se usó como criterio de revisión, no como autorización para firmar declaraciones del equipo. La página 12 contiene la rúbrica final. La fecha del 03/11/2026 en la página 13 es sugerida; el usuario indicó que presenta hoy.

## Requisitos mínimos (página 3)

| Criterio | Estado técnico | Evidencia |
|---|---|---|
| 8 entidades principales | Cumple: ocho dominios y 25 tablas físicas | Diccionario y JSON de estructura |
| 2 N:M resueltas | Cumple: compra/producto y venta/producto | DETALLE_COMPRA y DETALLE_VENTA |
| 3FN con ejemplo | Documentado, con importes históricos controlados | Informe final y normalización histórica |
| 15 restricciones explícitas | Superado; incluye PK, 57 FK, UNIQUE, CHECK y NOT NULL | JSON y scripts instalados |
| 2 triggers y 2 procedimientos | Superado: 15 triggers y 8 procedimientos | Instalación y caso directo de procedimientos |
| 3 roles diferenciados | Cumple, con usuarios SQL temporales reales | Caso `test_database_roles_have_different_effective_permissions` |
| 50 filas por tabla principal | Cumple en instalación reproducible, no se exige rellenar producción | 50 en cada una de las ocho tablas; JSON |

## Rúbrica de Entrega 4 (página 12)

| Criterio | Puntos | Evidencia / estado |
|---|---:|---|
| Sistema web completo en su alcance | 1.50 | RF-01–RF-12 implementados, pruebas de roles y transacciones; revisión visual presencial final corresponde al equipo |
| CRUD de todas las tablas principales | 0.50 | Catálogos completos; cabeceras de compras/ventas se corrigen con auditoría y se anulan. Los detalles no requieren CRUD independiente según el texto de la rúbrica |
| Manuales técnico y de usuario | 0.50 | Ambos actualizados a módulos, permisos y flujo vigentes |
| Informe y declaración de integridad | 0.25 | Informe actualizado; ratificación humana identificada, sin generar firmas |
| Estándares web y repo final | 0.50 | Evidencias automáticas; observación S1 y decisión S7 conservadas |
| Certificación y bitácora consolidada | 0.25 | Archivos completos; aprobaciones previas preservadas; revisión personal corresponde al equipo |
| Instalación desde cero y operación | 0.75 | Python 3.11 limpio, SQL completo, datos masivos, usuarios/roles temporales, login y flujos |
| Flujos del manual verificados | 0.25 | Aceptación más casos de inventario, proveedores y cifrado; revisión visual final pendiente de integrantes |
| Defensa grupal e individual | 0.50 | No verificable automáticamente; guía preparada, no se afirma que ya ocurrió |

## Estándares R, S, A y D (páginas 3–6)

| ID | Resultado |
|---|---|
| R1 | Estructura obligatoria presente y comprobada por script |
| R2 | README con proyecto, ambos integrantes, SGBD, instalación y enlaces vigentes |
| R3 | Commits descriptivos, sin crear autorías ficticias |
| R4 | Historial identifica a `elvin`/`tupipoy` y `ELOCHOAXD`; el equipo puede relacionar sus cuentas con los nombres declarados |
| R5 | Se publican los tags entrega-1, entrega-2, entrega-3 y entrega-4 al cerrar esta revisión |
| R6 | Sin patrones conocidos de secretos en archivos e historial revisados; `.env` y claves locales excluidos. Una búsqueda automática no es una garantía absoluta |
| R7 | `.gitignore` excluye entorno, caches, backups y temporales; PNG/PDF son evidencias requeridas |
| R8 | Repositorio público; no es necesario enviar invitaciones adicionales |
| S1 | Observación: tablas UPPER_SNAKE_CASE, columnas snake_case. Falta confirmar aceptación de esa variante si se exige minúscula literal |
| S2 | SQL separado en DDL, DML, vistas, triggers, procedimientos, seguridad y migraciones |
| S3 | Encabezados con archivo, autor, descripción y dependencias revisados |
| S4 | FK con UPDATE/DELETE explícitos en scripts; acciones y relaciones en diccionario |
| S5 | Gunicorn/MySQL publicados en Railway; health check y rutas protegidas comprobables |
| S6 | Reglas de negocio comentadas en triggers/procedimientos y explicadas en manual técnico |
| S7 | Totales/snapshots calculados y preservados como historia; desnormalización controlada documentada para defensa |
| S8 | SQL instalado en copia aislada antes de publicar; pruebas y metadatos conservados |
| A1 | Conexión separada de rutas, interfaz y servicios de negocio |
| A2 | Mensajes controlados, sin mostrar SQL crudo al usuario; errores técnicos se registran en logs |
| A3 | Campos obligatorios, formatos, cantidades y montos validados; restricciones SQL como segunda capa |
| A4 | Valores parametrizados; nombres dinámicos limitados por el código |
| A5 | Servicios y funciones con responsabilidades identificables; código revisado |
| A6 | Docstrings en funciones que acceden a la base |
| D1 | Documentación final revisada y corregida |
| D2 | Entrega final identificada con prefijos ENTREGA4 y carpetas por entrega; se conservan documentos históricos |
| D3 | Chen base recuperado en editable + PNG; relacional vigente editable + PNG/PDF |
| D4 | Matriz de trazabilidad final con rutas, tablas y pruebas |

## Responsabilidades humanas y observaciones

El equipo está formado por dos personas según confirmación del usuario. No se creó un tercer integrante ni una autorización docente ficticia. La constancia de aprobación del ER no fue aportada. Las firmas, comprensión individual y defensa oral deben ser ratificadas por los integrantes. La certificación identifica qué verificaciones son técnicas y cuáles no se pueden acreditar por herramientas.

Esta matriz demuestra evidencias, no garantiza una nota. Las observaciones S1/S7 y los puntos humanos permanecen visibles para que el catedrático evalúe la entrega real.
