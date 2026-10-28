# Manual técnico — Entrega 4

**Sistema:** Gestión de Ventas, Compras e Inventario — Comercial Estuardo  
**Versión:** Borrador de trabajo para Entrega 4

## Arquitectura

- **Interfaz y lógica web:** Flask en `web/app.py`; plantillas Jinja en `web/templates/`.
- **Acceso a datos:** PyMySQL en `web/db.py`, con credenciales mediante variables de entorno.
- **Base de datos:** MySQL 8+, motor InnoDB; DDL, DML, vistas, triggers, procedimientos y roles en `sql/`.
- **Producción:** Gunicorn sirve el objeto Flask `app`; el servicio web y MySQL ya están desplegados en Railway.

## Resumen y catálogo

`/resumen` consulta totales de productos, alertas por el stock mínimo configurado, costos disponibles, compras/ventas por rango seleccionado y productos por categoría. No se presenta un historial de movimientos porque el esquema no tiene una tabla de movimientos; la actividad reciente muestra únicamente compras y ventas existentes. `/productos` aplica búsqueda, filtros y orden parametrizados y pagina a 24 resultados. La navegación común se renderiza desde parciales Jinja y usa CSS responsive sin dependencias adicionales.

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

La instalación desde cero ejecuta el DDL y los scripts de datos, vistas, triggers, procedimientos y seguridad en el orden documentado en `INSTALL.md`. `sp_registrar_venta_detallada` y `sp_registrar_compra_detallada` reciben un arreglo JSON de líneas para registrar una transacción con varios productos; los triggers validan stock, costo y descuentos. Para una base ya desplegada, aplicar `sql/migrations/04_enforce_product_margin.sql` en Railway/MySQL antes de probar ventas; el DDL elimina y crea el esquema, por lo que no debe usarse para actualizar una base con datos que se deban conservar.

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

La aplicación está desplegada y accesible en Railway en https://comercialestuardobd-production.up.railway.app. El usuario confirmó el dominio, login, módulos y alta/edición de clientes. No se registran credenciales ni valores de configuración productiva en este manual. Falta registrar la evidencia de compras/ventas, instalación limpia y aceptación completa antes de certificar la versión final.
