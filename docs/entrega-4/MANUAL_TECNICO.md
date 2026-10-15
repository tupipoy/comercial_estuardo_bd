# Manual técnico — Entrega 4

**Sistema:** Gestión de Ventas, Compras e Inventario — Comercial Estuardo  
**Versión:** Borrador de trabajo para Entrega 4

## Arquitectura

- **Interfaz y lógica web:** Flask en `web/app.py`; plantillas Jinja en `web/templates/`.
- **Acceso a datos:** PyMySQL en `web/db.py`, con credenciales mediante variables de entorno.
- **Base de datos:** MySQL 8+, motor InnoDB; DDL, DML, vistas, triggers, procedimientos y roles en `sql/`.
- **Producción:** Gunicorn sirve el objeto Flask `app`; Railway alojará el servicio web y MySQL.

## Ejecución local

Consulta [INSTALL.md](../../INSTALL.md) para crear el entorno, inicializar MySQL, generar la clave secreta, configurar `.env` e iniciar Flask.

## Despliegue en Railway

1. Crear un proyecto Railway y agregar un servicio MySQL.
2. Conectar el repositorio al servicio web y configurar **Root Directory** como `web`, donde está `requirements.txt`.
3. Definir el Start Command:

   ```bash
   gunicorn --bind 0.0.0.0:$PORT app:app
   ```

   Configurar `/health` como ruta de health check del servicio.

4. Configurar `SECRET_KEY` y las variables `DB_HOST`, `DB_PORT`, `DB_USER` y `DB_PASSWORD` mediante referencias a `MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER` y `MYSQLPASSWORD` del servicio MySQL. Definir `DB_NAME=comercial_estuardo_db`, el esquema creado por el DDL. No guardar valores reales en el repositorio.
5. Inicializar el esquema remoto con los scripts descritos en `INSTALL.md`, generar el hash del usuario administrador y verificar los flujos web.
6. Generar un dominio para el servicio web y revisar los logs de despliegue.

## Objetos SQL

La instalación desde cero ejecuta el DDL y los scripts de datos, vistas, triggers, procedimientos y seguridad en el orden documentado en `INSTALL.md`. `sp_registrar_venta_detallada` y `sp_registrar_compra_detallada` reciben un arreglo JSON de líneas para registrar una transacción con varios productos; la venta activa los triggers de stock por cada detalle. El DDL elimina y crea el esquema: no usarlo para actualizar una base con datos que se deban conservar.

## Módulos administrativos

Las rutas `/categorias`, `/sucursales` y `/empleados` se limitan al cargo Administrador. Usan consultas parametrizadas y desactivación lógica. Las contraseñas de empleados se crean o cambian con `generate_password_hash` (PBKDF2-SHA256); nunca se muestran en el formulario de edición. El formulario impide la auto desactivación de la cuenta en sesión.

## Operación y seguridad

- Mantener `SECRET_KEY` y credenciales únicamente en el gestor de variables de Railway o en `.env` local ignorado por Git.
- Mantener `FLASK_DEBUG` desactivado en producción.
- Los formularios POST incluyen un token CSRF asociado a la sesión; el servidor rechaza solicitudes sin un token válido.
- El cierre de sesión usa POST y también requiere token CSRF.
- Las cookies de sesión usan `HttpOnly` y `SameSite=Lax`; en Railway se activa `Secure`.
- Revisar logs de Railway ante errores de conexión o despliegue; la aplicación registra excepciones del servidor sin mostrar el SQL al usuario.
- Hacer respaldos de MySQL antes de cambios de esquema y verificar restauración según el procedimiento del equipo.

## Estado de cierre

Este manual se completará con la configuración realmente usada, capturas/evidencias del despliegue y el resultado de la instalación limpia y las pruebas de aceptación. No se declara un despliegue en Railway hasta que el equipo lo ejecute y documente.
