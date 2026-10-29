# Manual técnico — Entrega 4

**Sistema:** Gestión de Ventas, Compras e Inventario — Comercial Estuardo  
**Versión:** Borrador de trabajo para Entrega 4

## Arquitectura

- **Interfaz y lógica web:** Flask en `web/app.py`; plantillas Jinja en `web/templates/`.
- **Acceso a datos:** PyMySQL en `web/db.py`, con credenciales mediante variables de entorno.
- **Base de datos:** MySQL 8+, motor InnoDB; DDL, DML, vistas, triggers, procedimientos y roles en `sql/`.
- **Producción:** Gunicorn sirve el objeto Flask `app`; el servicio web y MySQL ya están desplegados en Railway.

## Resumen y catálogo

`INVENTARIO_SUCURSAL` almacena el stock por producto y sucursal. Administración consulta totales consolidados; Vendedores y Bodega quedan limitados a la sucursal de su empleado. Compras y ventas actualizan existencias en la sucursal del empleado. Los traslados se solicitan sin modificar stock; un administrador los aprueba o rechaza, Bodega de origen confirma el despacho y Bodega de destino registra cantidades recibidas. El despacho descuenta el origen y la recepción acredita solo lo recibido, con auditoría de usuarios, fechas y diferencias. `sp_registrar_traslado`, `sp_resolver_traslado`, `sp_despachar_traslado` y `sp_recibir_traslado` hacen las operaciones transaccionales.

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

La instalación desde cero ejecuta el DDL y los scripts de datos, vistas, triggers, procedimientos y seguridad en el orden documentado en `INSTALL.md`. La migración 07 activa el flujo de aprobaciones en bases existentes y requiere aplicar después `sql/procedures/02_transfer_workflow.sql` y `sql/security/01_roles.sql`. El DDL elimina y crea el esquema, por lo que no debe usarse para actualizar una base con datos que se deban conservar.

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
