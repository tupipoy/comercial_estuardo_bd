# Bitácora de herramientas de IA — Entrega 4

**Proyecto:** Sistema de Gestión de Ventas, Compras e Inventario — Comercial Estuardo  
**Periodo registrado:** 14 al 28 de octubre de 2026

Esta bitácora registra el apoyo de IA, los cambios realizados y la evidencia disponible. Las validaciones pendientes se mantienen explícitas para que el equipo pueda completar el cierre con resultados verificables.

## Registro de sesiones

### 14 de octubre de 2026

#### Revisión de requisitos y preparación de despliegue

- **Herramienta:** OpenAI Codex.
- **Objetivo:** Revisar requisitos de Entrega 4 y preparar Gunicorn/Railway, además de completar CRUD administrativos y operaciones de compra/venta con varios productos.
- **Resultado:** Cambios propuestos en Flask, plantillas Jinja, procedimientos MySQL, roles y manuales de la Entrega 4.
- **Criterios revisados:** A1, A2, A3, A4, S2 y S5; persistencia MySQL y despliegue final seguían pendientes en esa fecha.
- **Validación:** Se ejecutó compilación de Python, carga de rutas y análisis sintáctico de plantillas. No se desplegó a Railway durante esa sesión; el despliegue activo se confirmó posteriormente. Faltaba probar las operaciones y procedimientos en un esquema MySQL temporal.
- **Seguimiento:** Elvin Miranda y Carlos Ochoa debían revisar los cambios y asignar quién los validaría antes del commit.

#### Formularios, accesos y administración de cuentas

- **Herramienta:** OpenAI Codex.
- **Objetivo:** Revisar formularios, accesos y administración de cuentas antes de continuar.
- **Resultado:** Se añadió token CSRF a solicitudes POST, flags de cookies de sesión, validación de seriales de motocicleta y protección del último Administrador activo.
- **Criterios revisados:** A2, A3 y A5; los controles requerían aceptación integrada.
- **Validación:** Flask test client verificó rechazo HTTP 400 sin token, paso de la solicitud con token hasta la validación normal de credenciales y redirección de rutas protegidas. No se pudo verificar la conexión SQL: no había servidor MySQL y `mysqld --initialize-insecure` terminó con SIGSEGV en la instancia aislada.
- **Seguimiento:** Repetir pruebas en MySQL 8 compatible y revisar el flujo completo.

#### Cierre de compra/venta y operación en Railway

- **Herramienta:** OpenAI Codex.
- **Objetivo:** Cerrar el flujo de compras/ventas y preparar la operación en Railway.
- **Resultado:** Se agregaron páginas de detalle transaccional y ruta `/health`, además de límites y validaciones para listas de líneas.
- **Criterios revisados:** A2, A3, A4 y S5 en código; integración pendiente en esa fecha.
- **Validación:** Flask cargó las rutas y plantillas. No se validó la integración con MySQL ni el despliegue en esa sesión; el despliegue se confirmó posteriormente.
- **Seguimiento:** Repetir pruebas con MySQL 8 compatible y en Railway.

#### Configuración local de producción

- **Herramienta:** OpenAI Codex.
- **Objetivo:** Revisar la configuración local de producción antes de continuar con la integración.
- **Resultado:** Se instalaron las dependencias fijadas en `web/requirements.txt` en un entorno temporal y se inició Gunicorn con `--chdir web`.
- **Criterios revisados:** A1 y S5 en entorno local.
- **Validación:** Gunicorn 23.0.0 inició la aplicación; una petición HTTP a `/health` devolvió `{"status":"ok"}`. Es una prueba local, no acredita Railway ni conectividad a MySQL.
- **Seguimiento:** El equipo confirmó después que Railway estaba activo; quedaba registrar la aceptación funcional completa.

#### Trazabilidad y límites del esquema SQL

- **Herramienta:** OpenAI Codex.
- **Objetivo:** Revisar la trazabilidad con requisitos de Entrega 1 y los límites del esquema SQL.
- **Resultado:** Se confirmó el alcance de ocho entidades principales y se añadieron validaciones web para rangos INT/DECIMAL y stock máximo en compras.
- **Criterios revisados:** A3, S7 y D4; validación en MySQL pendiente.
- **Validación:** Pendiente revisar los bordes con el equipo y probar persistencia/transacciones contra MySQL 8.
- **Seguimiento:** Ejecutar los casos ampliados y revisar la matriz antes del cierre.

#### Despliegue y flujo de clientes

- **Herramienta:** OpenAI Codex.
- **Objetivo:** Validar el despliegue real y el flujo de clientes, después de que el usuario confirmara que el dominio Railway abría.
- **Resultado:** Se corrigió la detección de categorías de motocicleta para no confundir `Repuestos de Motor` con motos; se amplió el caso de prueba asociado.
- **Criterios revisados:** A3 y D4. La confirmación del despliegue corresponde a evidencia reportada por el usuario.
- **Validación:** El usuario confirmó login, acceso a módulos, alta y edición de cliente en Railway. La corrección de categoría aún requería push, redeploy y prueba; compra/venta seguían pendientes.
- **Seguimiento:** Publicar el commit y continuar las pruebas.

### 19 de octubre de 2026

#### Criterios actualizados y documentación

- **Herramienta:** OpenAI Codex.
- **Objetivo:** Mejorar la operación, búsqueda y cumplimiento de los criterios del PDF actualizado.
- **Resultado:** Se agregaron importes estimados y filtros a catálogos e historiales; se renombró la carpeta a `sql/procedures`, se completaron encabezados de scripts SQL y docstrings de acceso a BD, y se actualizaron la matriz de cierre y los manuales.
- **Criterios revisados:** A1–A6, R1–R7, S1–S8 y D1–D4. S1/ER y la autorización del grupo seguían pendientes de evidencia.
- **Validación:** No se ejecutaron pruebas funcionales en esa sesión; `git diff --check` no reportó errores. Railway estaba desplegado; compras/ventas y los cambios locales recientes requerían aceptación en ese entorno.
- **Seguimiento:** Validar el código y obtener las autorizaciones pendientes antes de certificar.

### 27 de octubre de 2026

#### Revisión del estado de entrega

- **Herramienta:** OpenAI Codex.
- **Objetivo:** Revisar qué faltaba para entregar ese día, contrastando los criterios del PDF con el estado del repositorio y Railway.
- **Resultado:** Se confirmó que los PDF adjuntos eran idénticos; se precisó que Railway estaba activo, se actualizaron las notas de entrega y se advirtió que la instalación DDL debía ejecutarse solo en una base temporal por ser destructiva.
- **Criterios revisados:** S5, D1, D4 y R5; tag, aceptación integral, firmas y autorizaciones aún pendientes.
- **Validación:** Revisión documental y `git diff --check`; no se ejecutaron pruebas funcionales ni se modificó la base de Railway.
- **Seguimiento:** Completar aceptación, guardar evidencia, firmar y crear el tag sobre la versión final.

#### URL de Railway y consistencia documental

- **Herramienta:** OpenAI Codex.
- **Objetivo:** Registrar la URL Railway proporcionada por el usuario y dejar consistentes los documentos antes de subir los cambios locales.
- **Resultado:** Se agregó la URL pública en informe, manuales y casos de prueba; se corrigió la numeración del manual técnico y la declaración de integridad quedó explícitamente pendiente de aprobación/firma.
- **Criterios revisados:** D1, D2, D4 y S5.
- **Validación:** Revisión documental y `git diff --check`; no se ejecutaron pruebas funcionales ni se consultó o modificó la base productiva.
- **Seguimiento:** Ejecutar aceptación funcional, confirmar el commit desplegado, completar firmas/autorizaciones y crear el tag final.

### 28 de octubre de 2026

#### Rediseño SaaS responsive

- **Herramienta:** OpenAI Codex.
- **Objetivo:** Implementar el rediseño SaaS responsive solicitado para escritorio y móvil, conservando rutas, permisos y datos reales.
- **Resultado:** Se creó `/resumen`, navegación lateral e inferior compartidas, filtros/orden/paginación de productos, tarjetas móviles, indicadores y distribución por categoría sin inventar movimientos ni costos.
- **Criterios revisados:** A1–A5, D1 y D4 en presentación y consultas.
- **Validación:** `py_compile`, carga de 24 plantillas, redirección anónima y 403 del Vendedor en Productos. El Flask test client renderizó resumen/inventario/productos con un conector MySQL simulado; no se probó MySQL real ni se hizo inspección visual en navegador.
- **Seguimiento:** Revisar la interfaz en Railway y distintos tamaños, y aceptar filtros/consultas con datos reales.

#### Validación de margen en ventas y compras

- **Herramienta:** OpenAI Codex.
- **Objetivo:** Corregir ventas bajo costo y revisar la preparación para el cierre de Entrega 4.
- **Resultado:** Se validó el precio mínimo en Flask y MySQL; se impidieron descuentos bajo costo y compras que elevarían el costo vigente sobre el precio de venta; se añadió migración para bases existentes. Commit `641e1af`.
- **Criterios revisados:** A3, S4, S6 y A5 en código y SQL.
- **Validación:** El usuario ejecutó la migración en el MySQL de Railway. La consulta inicialmente detectó Casco con costo Q100 y venta Q50; luego reportó cero productos bajo costo y verificó los tres triggers de venta. No se había documentado una venta funcional posterior a la migración ni las pruebas multiproducto.
- **Seguimiento:** Completar aceptación funcional, guardar capturas/logs sin secretos y revisar los documentos antes de etiquetar la entrega.

#### Lista de recibos en móvil

- **Herramienta:** OpenAI Codex.
- **Objetivo:** Mejorar la consulta de recibos en pantallas móviles tras detectar que la tabla obligaba a desplazarse horizontalmente.
- **Resultado:** Se añadieron tarjetas de recibo con total, fecha, cliente, empleado, sucursal, pago, estado y acceso visible a la factura; el filtro se reorganizó para pantallas estrechas y se conservó la tabla de escritorio.
- **Criterios revisados:** A1, A2 y D4 en estructura semántica, áreas táctiles y adaptación responsive.
- **Validación:** Cambio de plantilla y CSS; inspección visual en navegador/dispositivo y aceptación en Railway pendientes.
- **Seguimiento:** Revisar la lista de ventas y apertura/impresión de factura en móvil antes de cerrar CP4-20.

#### Endurecimiento del inicio de sesión

- **Herramienta:** OpenAI Codex.
- **Objetivo:** Endurecer el inicio de sesión ante intentos repetidos, con suspensión temporal progresiva.
- **Resultado:** Se añadió contador persistente por empleado, suspensión tras cinco fallos, demoras de 1/5/15/30 minutos, respuesta genérica y hash de relleno para identificadores inexistentes o cuentas suspendidas. Se agregó migración 05 para bases existentes.
- **Criterios revisados:** A2 y S5 en autenticación, persistencia y mensajes de error.
- **Validación:** Revisión estática y `git diff --check`; no se ejecutaron pruebas de autenticación ni se aplicó la migración 05 a Railway.
- **Seguimiento:** Aplicar la migración 05 en Railway antes del despliegue y validar intentos fallidos, tiempos de suspensión, acceso correcto y restablecimiento del contador.

## Cambios asistidos que requieren revisión

- Configuración para iniciar Flask con Gunicorn en Railway y lectura de variables de MySQL.
- CRUD administrativo de Categorías, Sucursales y Empleados.
- Nuevos procedimientos de compra/venta multiproducto que reciben JSON.
- Formularios con líneas agregables para compra y venta; captura opcional de VIN/chasis y motor.
- Búsqueda en catálogos/inventario y cálculo visual estimado en formularios transaccionales; requieren aceptación funcional integrada.
- Borradores del manual técnico, manual de usuario, informe final y matriz de cierre.

## Verificaciones registradas

- `py_compile` de `web/app.py` y `web/db.py`.
- Importación de Flask y enumeración de rutas con clave local temporal.
- Carga de todas las plantillas Jinja.
- `git diff --check`.
- Flask test client: login GET, CSRF faltante/válido y acceso anónimo a ruta protegida.
- Inicio local de Gunicorn 23.0.0 con `--chdir web` y respuesta HTTP 200 de `/health`.
- MySQL de Railway: el usuario reportó la aplicación de `sql/migrations/04_enforce_product_margin.sql`, consulta sin productos con precio bajo costo y presencia de `trg_validar_stock_venta`, `trg_descontar_stock_venta` y `trg_validar_margen_venta` el 28/10/2026.

Estas comprobaciones no sustituyen la prueba integrada completa con MySQL. Aunque los triggers de margen se verificaron en la base productiva, el equipo debe ejecutar una instalación limpia en un esquema temporal, probar casos de compra/venta con varias líneas, reversión por stock insuficiente, permisos MySQL y aceptación visual en Railway, y actualizar esta bitácora con los resultados reales.


### 29 de octubre de 2026

#### Inventario y traslados entre sucursales

- **Herramienta:** OpenAI Codex.
- **Objetivo:** Separar existencias por sucursal, habilitar traslados y permitir que Administración consulte el consolidado.
- **Resultado:** Snapshot local `version1/` del commit `9467202`; cambios de modelo con `INVENTARIO_SUCURSAL`, compras/ventas por sucursal, traslados multiproducto y filtrado por rol. La migración propuesta asigna el stock existente a Sucursal Central, según decisión del usuario.
- **Validación:** `py_compile`, compilación Jinja de plantillas nuevas y `git diff --check`; no se ejecutó MySQL ni se modificó Railway.
- **Seguimiento:** Respaldar MySQL, ejecutar la migración en base temporal, probar CP4-21 a CP4-24 y aplicar objetos SQL actualizados antes de desplegar.
