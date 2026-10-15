# Instalación — Comercial Estuardo

## Requisitos

- Python 3.11 o superior
- MySQL 8.0 o superior
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
mysql -u root -p < sql/views/01_views.sql
mysql -u root -p < sql/triggers/01_triggers.sql
mysql -u root -p < sql/procedimiento/01_procedures.sql
mysql -u root -p < sql/security/01_roles.sql
```

También puedes abrir y ejecutar cada archivo en MySQL Workbench, respetando el mismo orden.

> **Advertencia:** `sql/ddl/01_schema.sql` elimina y vuelve a crear la base `comercial_estuardo_db`. No lo ejecutes sobre una base que quieras conservar.

`02_bulk_data.sql` está preparado para ejecutarse una vez después del esquema y los datos semilla. Completa 50 registros en las ocho entidades principales y agrega detalles de compra y venta.

La carpeta `sql/migrations/` contiene cambios puntuales para actualizar bases existentes. No ejecutes esas migraciones después de la instalación limpia: los cambios de contraseña y precio de costo ya están incorporados en el DDL actual. En bases antiguas, revisa primero si cada columna ya existe antes de ejecutar su migración.

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

Si Railway asigna otro nombre al servicio de base de datos, reemplaza `MySQL` en las referencias por el nombre del servicio. `DB_NAME` debe conservar `comercial_estuardo_db`, que es el esquema creado por los scripts del proyecto. No publiques un dominio de MySQL ni guardes credenciales en Git.

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

La instalación limpia de la versión anterior (Entrega 3) se verificó el 29 de septiembre de 2026 en un esquema temporal independiente: los diez conjuntos de datos tuvieron 50 filas, y se instalaron tres vistas, dos triggers y dos procedimientos. También se ejecutaron los ocho casos funcionales de esa entrega. Esa evidencia histórica no valida los dos procedimientos mult producto añadidos para Entrega 4. Para aprobar esta entrega, ejecuta de nuevo desde cero los scripts anteriores en MySQL 8 y registra el resultado de los casos de `docs/casos-prueba/CASOS_PRUEBA_ENTREGA_4.md`; la integración Entrega 4 aún está pendiente de esa verificación.

## 10. Detener la aplicación

En la terminal, presiona `Ctrl + C`. Para salir del entorno virtual, ejecuta:

```bash
deactivate
```
