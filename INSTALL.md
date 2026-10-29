# Instalación — Comercial Estuardo

## Requisitos

- Python 3.11 o superior
- MySQL 8.0.30 o superior (Railway usa MySQL 8.4)
- Git
- Navegador web

## 1. Clonar el repositorio

```bash
git clone https://github.com/tupipoy/comercial_estuardo_bd.git
cd comercial_estuardo_bd
```

## 2. Crear y activar el entorno virtual

En macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

En Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## 3. Instalar dependencias

Desde la raíz del proyecto y con el entorno virtual activo:

```bash
pip install -r web/requirements.txt
```

## 4. Crear e inicializar la base de datos

Ejecuta los siguientes archivos **en este orden**. Los comandos de ejemplo solicitan la contraseña del usuario MySQL `root`:

```bash
mysql -u root -p < sql/ddl/01_schema.sql
mysql -u root -p < sql/dml/01_seed_data.sql
mysql -u root -p < sql/dml/02_bulk_data.sql
mysql -u root -p < sql/migrations/08_inventory_control.sql
mysql -u root -p < sql/migrations/09_supplier_proposals.sql
mysql -u root -p < sql/migrations/10_document_corrections.sql
mysql -u root -p < sql/views/01_views.sql
mysql -u root -p < sql/triggers/01_triggers.sql
mysql -u root -p < sql/triggers/02_inventory_control.sql
mysql -u root -p < sql/procedures/01_procedures.sql
mysql -u root -p < sql/procedures/02_transfer_workflow.sql
mysql -u root -p < sql/security/01_roles.sql
mysql -u root -p < sql/security/02_inventory_control.sql
mysql -u root -p < sql/security/03_supplier_proposals.sql
```

También puedes abrir y ejecutar cada archivo en MySQL Workbench, respetando el mismo orden.

> **Advertencia:** `sql/ddl/01_schema.sql` elimina y vuelve a crear la base `comercial_estuardo_db`. No lo ejecutes sobre una base que quieras conservar.

`02_bulk_data.sql` está preparado para ejecutarse una vez después del esquema y los datos semilla. Completa 50 registros en las ocho entidades principales y agrega detalles de compra y venta; asigna el inventario de demostración a las dos sucursales.

### Actualizar una base existente

No se vuelve a ejecutar el DDL sobre una base con datos. Las migraciones 02–07 ya están incorporadas en el DDL base para una instalación nueva. Cada migración se aplica una sola vez sobre una base anterior:

- Base con stock global: respaldar y aplicar 06, que asigna el stock a Sucursal Central, y después 07 para aprobación/despacho/recepción. Actualizar los objetos necesarios según la versión previa.
- Base con migración 07: aplicar 08, triggers 02 y vistas actualizadas.
- Base con migración 08: aplicar 09 y seguridad 03 para propuestas de proveedores.
- Base con migración 09: aplicar 10 y triggers 02 para correcciones de cabecera y detección precisa de motocicletas.

Al reinstalar permisos se aplican seguridad 01, 02 y 03 en orden. No reinstalar triggers 01 sin volver a aplicar triggers 02: los últimos protegen reservas, unidades e historial. Los procedimientos de traslados de la versión 07 no se utilizan desde la aplicación actual.

`scripts/migrate_inventory_control.py` respalda y prueba una copia antes de aplicar la 08; `--suppliers` selecciona la 09 y `--document-corrections` la 10. En Railway se ejecuta con las variables del servicio MySQL mediante `railway run --service MySQL -- python scripts/migrate_inventory_control.py OPCION`. Las credenciales no se imprimen ni se guardan en Git.

## 5. Crear una contraseña inicial para el administrador

Los empleados de prueba de `02_bulk_data.sql` tienen `password_hash = NULL`, por lo que no pueden iniciar sesión hasta asignar una contraseña. Con el entorno virtual activo, genera un hash para una contraseña elegida por ti:

```bash
python -c 'from werkzeug.security import generate_password_hash; print(generate_password_hash("TU_CONTRASEÑA", method="pbkdf2:sha256"))'
```

Copia el hash generado y úsalo en MySQL para habilitar el empleado Administrador inicial:

```sql
USE comercial_estuardo_db;

UPDATE EMPLEADO
SET correo = 'admin@comercialestuardo.com',
    password_hash = 'PEGA_AQUI_EL_HASH_GENERADO'
WHERE id_empleado = 1
  AND cargo = 'Administrador';
```

Inicia sesión con ese correo y la contraseña que elegiste. Para habilitar usuarios de prueba de Ventas o Bodega, genera hashes propios y asígnalos a empleados con esos cargos.

El script de roles crea los roles MySQL diferenciados. Las cuentas MySQL y su asignación a esos roles se administran aparte; el control web por cargo usa `EMPLEADO.cargo`.

## 6. Configurar la conexión Flask

Copia `.env.example` como `.env` en la raíz del repositorio, junto a `README.md`, y reemplaza los valores de ejemplo:

```bash
cp .env.example .env
```

No subas `.env` al repositorio. La aplicación lo carga al iniciar desde la raíz del proyecto.

## 7. Iniciar la aplicación

Con el entorno virtual activo y desde la raíz del proyecto:

```bash
python web/app.py
```

Configura `SECRET_KEY` en `.env` con un valor aleatorio antes de iniciar la aplicación. Abre <http://localhost:5050> en el navegador. El cargo del empleado habilita los módulos correspondientes.

## 8. Despliegue en Railway

El servicio web se ejecuta con Gunicorn desde la carpeta `web/`:

```bash
gunicorn --bind 0.0.0.0:$PORT app:app
```

En Railway, crea un proyecto con un servicio **MySQL** y un servicio web conectado al repositorio GitHub. Configura **Root Directory** como `web` para que Railpack detecte `requirements.txt` e instale las dependencias Python. Configura el comando anterior como **Start Command** del servicio web. Agrega estas variables en el servicio web:

Configura la ruta de health check de Railway como `/health`; responde cuando el proceso web está activo y no consulta MySQL.

| Variable | Valor en Railway |
|---|---|
| `SECRET_KEY` | Secreto aleatorio único para la aplicación |
| `DB_HOST` | `${{MySQL.MYSQLHOST}}` |
| `DB_PORT` | `${{MySQL.MYSQLPORT}}` |
| `DB_USER` | `${{MySQL.MYSQLUSER}}` |
| `DB_PASSWORD` | `${{MySQL.MYSQLPASSWORD}}` |
| `DB_NAME` | `comercial_estuardo_db` |

Si Railway asigna otro nombre al servicio de base de datos, reemplaza `MySQL` en las referencias por el nombre del servicio. `DB_NAME` debe conservar `comercial_estuardo_db`, que es el esquema creado por los scripts del proyecto. La aplicación usa la red privada de MySQL; las tareas externas autorizadas y respaldos pueden usar el proxy TCP con credenciales protegidas. No guardar esas URL en Git.

Para inicializar la base remota, conecta temporalmente MySQL Workbench o el cliente `mysql` mediante la conexión autorizada de Railway y ejecuta los scripts de las secciones 4 y 5, en el mismo orden. Revisa dos veces el nombre del esquema antes de ejecutar `01_schema.sql`, ya que ese archivo elimina y recrea `comercial_estuardo_db`. Después genera el hash del administrador y asígnalo como indica la sección 5. Finalmente, genera un dominio público para el servicio web y comprueba login, inventario, compras y ventas.

El archivo `.env` se usa solo en desarrollo local. Railway inyecta las variables configuradas en el servicio al arrancar el proceso.

## 9. Comprobar los objetos de base de datos

En MySQL Workbench puedes revisar las tablas, vistas, triggers y procedimientos:

```sql
USE comercial_estuardo_db;
SHOW TABLES;
SHOW FULL TABLES WHERE Table_type = 'VIEW';
SHOW TRIGGERS;
SHOW PROCEDURE STATUS WHERE Db = 'comercial_estuardo_db';
```

La instalación completa de Entrega 4 se verificó en MySQL 8.4 temporal y un entorno Python 3.11 recién creado con `requirements.txt`: 25 tablas, 3 vistas, 15 triggers, 8 procedimientos, tres roles y 50 filas por cada entidad principal. La aceptación verificó login, permisos efectivos, CRUD de catálogos, operaciones multiproducto, cabeceras auditadas y rollback. Ver `docs/entrega-4/evidencias/VERIFICACION_ENTREGA4.json` y `PRUEBAS_ENTREGA4.txt`. Los esquemas, usuarios y roles de prueba se eliminaron al terminar.

Para repetir la comprobación, configura una URL MySQL autorizada en `TEST_MYSQL_URL` o `MYSQL_PUBLIC_URL` y ejecuta `python tests/test_delivery4_acceptance.py --isolated`. Requiere el cliente `mysql` y permiso para crear/eliminar exclusivamente los recursos temporales de prueba. Los datos de demostración se instalan en ese esquema, no en el esquema productivo.

## 10. Detener la aplicación

En la terminal, presiona `Ctrl + C`. Para salir del entorno virtual, ejecuta:

```bash
deactivate
```
