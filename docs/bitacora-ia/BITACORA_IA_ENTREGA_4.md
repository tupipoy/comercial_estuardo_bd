# Bitácora de herramientas de IA — Entrega 4

**Proyecto:** Sistema de Gestión de Ventas, Compras e Inventario — Comercial Estuardo  
**Periodo registrado:** 14 de octubre de 2026 en adelante

| Fecha | Herramienta | Objetivo y solicitud | Resultado asistido | Validación del equipo | Responsable |
|---|---|---|---|---|---|
| 14/10/2026 | OpenAI Codex | Revisar requisitos de Entrega 4 y preparar Gunicorn/Railway, además de completar CRUD administrativos y operaciones de compra/venta con varios productos. | Cambios propuestos en Flask, plantillas Jinja, procedimientos MySQL, roles y manuales de la Entrega 4. | Se ejecutó compilación de Python, carga de rutas y análisis sintáctico de plantillas. Falta que el equipo pruebe las operaciones y procedimientos en un esquema MySQL temporal; no se desplegó a Railway. | Elvin Miranda y Carlos Ochoa deben revisar y asignar quién valida cada cambio antes del commit. |
| 14/10/2026 | OpenAI Codex | Revisar formularios, accesos y administración de cuentas antes de continuar. | Se añadió token CSRF a solicitudes POST, flags de cookies de sesión, validación de seriales de motocicleta y protección del último Administrador activo. | Flask test client verificó rechazo HTTP 400 sin token, paso de la solicitud con token hasta la validación normal de credenciales y redirección de rutas protegidas. La conexión SQL no pudo verificarse: no había servidor MySQL disponible y `mysqld --initialize-insecure` terminó con SIGSEGV en instancia aislada. | El equipo debe repetir pruebas en MySQL 8 compatible y revisar el flujo completo. |
| 14/10/2026 | OpenAI Codex | Cerrar el flujo de compras/ventas y preparar operación Railway. | Se agregaron páginas de detalle transaccional y ruta `/health`, más límites y validaciones de listas de líneas. | Flask cargó las rutas y plantillas; MySQL/Railway siguen sin validación integrada. | El equipo debe repetir pruebas en MySQL 8 compatible y Railway. |
| 14/10/2026 | OpenAI Codex | Verificar configuración de producción local antes de seguir con la integración. | Se instalaron las dependencias fijadas en `web/requirements.txt` en un entorno temporal y se inició Gunicorn con `--chdir web`. | Gunicorn 23.0.0 inició la aplicación; una petición HTTP a `/health` devolvió `{"status":"ok"}`. Es una prueba local, no acredita Railway ni conectividad a MySQL. | Repetir la aceptación web en Railway una vez inicializada la base. |

## Cambios asistidos que requieren revisión

- Configuración para iniciar Flask con Gunicorn en Railway y lectura de variables de MySQL.
- CRUD administrativo de Categorías, Sucursales y Empleados.
- Nuevos procedimientos de compra/venta mult producto que reciben JSON.
- Formularios con líneas agregables para compra y venta; captura opcional de VIN/chasis y motor.
- Borradores del manual técnico, manual de usuario, informe final y matriz de cierre.

## Verificaciones registradas

- `py_compile` de `web/app.py` y `web/db.py`.
- Importación de Flask y enumeración de rutas con clave local temporal.
- Carga de todas las plantillas Jinja.
- `git diff --check`.
- Flask test client: login GET, CSRF faltante/válido y acceso anónimo a ruta protegida.
- Inicio local de Gunicorn 23.0.0 con `--chdir web` y respuesta HTTP 200 de `/health`.

Estas comprobaciones no sustituyen la prueba integrada con MySQL. El equipo debe ejecutar instalación limpia, casos de varias líneas, reversión por stock insuficiente, permisos MySQL y aceptación en Railway, y actualizar esta bitácora con los resultados reales.
