# Instalación del Proyecto - Comercial Estuardo

## Requisitos

Antes de ejecutar el proyecto se necesita:

- Python 3.11 o superior
- MySQL 8.0 o superior
- Git
- Navegador web

## 1. Clonar el repositorio

```bash
git clone https://github.com/tupipoy/comercial_estuardo_bd.git
cd comercial_estuardo_bd
```

## 2. Crear el entorno virtual

En macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

En Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## 3. Instalar dependencias

Con el entorno virtual activado:

```bash
pip install -r web/requirements.txt
```

## 4. Crear la base de datos

El script principal se encuentra en `sql/ddl/01_schema.sql`. Puede ejecutarse desde MySQL Workbench o desde la terminal:

```bash
mysql -u root -p < sql/ddl/01_schema.sql
```

El script crea la base de datos `comercial_estuardo_db`. **Advertencia:** el script elimina y vuelve a crear esa base de datos, por lo que borra cualquier dato previo que contenga.

## 5. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto, en el mismo directorio desde el que ejecutarás la aplicación. Agrega la configuración de tu MySQL:

```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_NAME=comercial_estuardo_db
SECRET_KEY=una_clave_secreta_local
```

El archivo `.env` contiene credenciales locales y no debe subirse al repositorio. La aplicación usa valores predeterminados para la conexión a la base de datos si alguna variable `DB_*` no está definida.

## 6. Ejecutar la aplicación

Desde la raíz del proyecto, con el entorno virtual activado:

```bash
python web/app.py
```

La aplicación estará disponible normalmente en:

```text
http://localhost:5050
```

## 7. Verificar la base de datos

Desde MySQL:

```sql
USE comercial_estuardo_db;
SHOW TABLES;
SELECT * FROM PRODUCTO;
```

La consulta a `PRODUCTO` puede devolver cero filas si todavía no se han agregado productos.

## 8. Detener la aplicación

En la terminal, presiona `Ctrl + C`.

## 9. Desactivar el entorno virtual

```bash
deactivate
```

## Nota

La conexión a la base de datos se configura mediante variables de entorno, por lo que puedes usar diferentes credenciales o servidores sin modificar el código fuente.
