# Manual técnico — Entrega 4

**Sistema:** Gestión de Ventas, Compras e Inventario — Comercial Estuardo
**Versión:** Borrador de trabajo para Entrega 4

## Arquitectura

- **Interfaz y lógica web:** Flask en `web/app.py`; plantillas Jinja en `web/templates/`.
- **Acceso a datos:** PyMySQL en `web/db.py`, con credenciales mediante variables de entorno.
- **Base de datos:** MySQL 8+, motor InnoDB; DDL, DML, vistas, triggers, procedimientos y roles en `sql/`.
- **Producción:** Gunicorn sirve el objeto Flask `app`; el servicio web y MySQL ya están desplegados en Railway.

## Resumen y catálogo

`INVENTARIO_SUCURSAL` conserva existencias físicas, reservas, mínimo por sucursal y una revisión que invalida conteos desactualizados. `web/inventory_control.py` procesa compras identificadas, traslados, conteos y reversos dentro de la transacción del llamador. Cada mutación valida el empleado activo, su cargo, sucursal y el estado actual; las filas de inventario y unidades se bloquean para evitar doble consumo. `sql/triggers/02_inventory_control.sql` impide ventas sobre stock reservado, vincula la unidad exacta y registra saldos e historial automáticamente. `UNIDAD_PRODUCTO`, `TRASLADO_UNIDAD`, `MOVIMIENTO_INVENTARIO`, `HISTORIAL_UNIDAD`, `CONTEO_INVENTARIO` y `REVERSO_DOCUMENTO` conservan trazabilidad. Los procedimientos de traslados de la versión 07 quedan como compatibilidad histórica y se revoca su ejecución al rol Bodega; los nuevos flujos se realizan desde la aplicación.

La migración 08 es aditiva y completa las identidades de ventas históricas que ya tenían VIN y motor. No inventa datos de motocicletas existentes sin identificación. El Kardex arranca con un saldo inicial, no con una reconstrucción histórica. Las recepciones parciales de traslados son acumuladas y mantienen visibles los faltantes. Las anulaciones conservan documentos y líneas.

## Ejecución local

Consulta [INSTALL.md](../../INSTALL.md) para crear el entorno, inicializar MySQL, generar la clave secreta, configurar `.env` e iniciar Flask.

## Despliegue en Railway

1. El proyecto ya cuenta con servicio web y servicio MySQL en Railway. URL pública: https://comercialestuardobd-production.up.railway.app. Para reproducir el despliegue, usar el mismo repositorio y configurar **Root Directory** como `web`, donde está `requirements.txt`.
2. Definir el Start Command:

   ```bash
   gunicorn --bind 0.0.0.0:$PORT app:app
   ```

   Configurar `/health` como ruta de health check del servicio.

3. Configurar `SECRET_KEY` y las variables `DB_HOST`, `DB_PORT`, `DB_USER` y `DB_PASSWORD` mediante referencias a `MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER` y `MYSQLPASSWORD` del servicio MySQL. Definir `DB_NAME=comercial_estuardo_db`, el esquema creado por el DDL. No guardar valores reales en el repositorio.
4. No ejecutar el DDL destructivo sobre la base productiva. Inicializar una base de aceptación separada con los scripts de `INSTALL.md`, crear su administrador y verificar los flujos.
5. Confirmar el dominio actual del servicio web y revisar los logs del despliegue aceptado.

## Objetos SQL

La instalación desde cero ejecuta el DDL y los scripts de datos, vistas, triggers, procedimientos y seguridad en el orden documentado en `INSTALL.md`. Después de la migración 07, aplicar la 08, los triggers 02, vistas y los scripts de seguridad 01 y 02. Las instalaciones limpias también aplican la 08 después del DDL base. El DDL elimina y crea el esquema, por lo que no debe usarse para actualizar una base con datos que se deban conservar.

## Módulos administrativos

Las rutas `/categorias`, `/sucursales` y `/empleados` se limitan al cargo Administrador. Usan consultas parametrizadas y desactivación lógica. Las contraseñas de empleados se crean o cambian con `generate_password_hash` (PBKDF2-SHA256); nunca se muestran en el formulario de edición. El formulario impide la auto desactivación de la cuenta en sesión.

## Operación y seguridad

- Mantener `SECRET_KEY` y credenciales únicamente en el gestor de variables de Railway o en `.env` local ignorado por Git.
- Mantener `FLASK_DEBUG` desactivado en producción.
- Los formularios POST incluyen un token CSRF asociado a la sesión; el servidor rechaza solicitudes sin un token válido.
- El cierre de sesión usa POST y también requiere token CSRF.
- Las cookies de sesión usan `HttpOnly` y `SameSite=Lax`; en Railway se activa `Secure`.
- Después de cinco contraseñas incorrectas, la cuenta queda suspendida temporalmente. Los intentos posteriores aumentan la suspensión progresivamente (1, 5, 15 y hasta 30 minutos); un inicio correcto restablece el contador. El aviso de login es genérico para no confirmar si una cuenta existe. En bases ya desplegadas, ejecutar una sola vez `sql/migrations/05_login_lockout.sql` antes de desplegar esta versión; en instalaciones nuevas las columnas vienen en el DDL.
- Revisar logs de Railway ante errores de conexión o despliegue; la aplicación registra excepciones del servidor sin mostrar el SQL al usuario.
- Hacer respaldos de MySQL antes de cambios de esquema y verificar restauración según el procedimiento del equipo.

## Estado de cierre

La aplicación está desplegada y accesible en Railway en https://comercialestuardobd-production.up.railway.app. El usuario confirmó el dominio, login, módulos y alta/edición de clientes; también reportó la instalación en MySQL de Railway de los tres triggers de venta requeridos. No se registran credenciales ni valores de configuración productiva en este manual. Falta registrar la aceptación de compras/ventas, instalación limpia y pruebas integrales antes de certificar la versión final.


## Comprobación y recuperación

La migración 09 agrega `PROPUESTA_PROVEEDOR` y `EVENTO_PROVEEDOR`. `web/supplier_control.py` consulta el cargo activo en cada mutación, bloquea la propuesta durante su resolución y crea el proveedor aprobado y su auditoría dentro de una sola transacción. Una clave única impide propuestas simultáneas pendientes para el mismo NIT. Las rutas de edición y desactivación exigen Administración y vuelven a verificar el cargo en el servicio. Bodega tiene consulta del catálogo e inserción de propuestas, sin permisos SQL para insertar o actualizar proveedores ni resolver propuestas. `sql/security/03_supplier_proposals.sql` revoca privilegios anteriores y debe aplicarse después de los roles base. Las compras solo referencian el catálogo aprobado y activo; los proveedores existentes se conservan. `tests/test_supplier_proposals.py --isolated` comprueba la matriz de permisos, concurrencia, duplicados, auditoría y selección en Compras.

`tests/test_inventory_control.py --isolated` crea un esquema temporal `ce_acceptance_*`, instala los objetos SQL y comprueba reservas concurrentes, permisos, seriales, recepción parcial, devoluciones, anulaciones, conteos obsoletos y las pantallas. Lo elimina al terminar. `tests/test_backup_crypto.py` valida cifrado, recuperación y rechazo de archivos alterados. El workflow diario restaura cada copia en MySQL 8.4 aislado y registra el resultado; ver `docs/operaciones/RESPALDOS.md`.


## Actualización auditada de documentos

La migración 10 crea `CORRECCION_DOCUMENTO`. `correct_document` bloquea la cabecera, consulta el cargo activo y permite únicamente cliente/pago en ventas o proveedor/número de orden en compras. El motivo es obligatorio, las opciones deben pertenecer al catálogo y el documento debe estar vigente. La modificación y sus snapshots se confirman en una misma transacción. Las líneas y movimientos no cambian. Esta operación completa la actualización de las tablas principales sin exponer edición libre del historial financiero.

El reconocimiento automático de motocicletas usa palabras completas `moto`, `motos`, `motocicleta` o `motocicletas`, evitando exigir seriales a **Repuestos de Motor**. Un producto también puede marcarse explícitamente para identificación por unidad. La corrección no desactiva el seguimiento de unidades existentes.

## Evidencia de la versión final

La instalación completa tiene 25 tablas, 3 vistas, 15 triggers, 8 procedimientos y 57 claves foráneas. El JSON de `evidencias/VERIFICACION_ENTREGA4.json` registra tipos, acciones referenciales, versiones y hashes de scripts. `tests/test_delivery4_acceptance.py --isolated` carga semilla y datos masivos, comprueba 50 filas por entidad y usa los tres roles con cuentas MySQL temporales. El registro completo de pruebas está en `evidencias/PRUEBAS_ENTREGA4.txt`.
