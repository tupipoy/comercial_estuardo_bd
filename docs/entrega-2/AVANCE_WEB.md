# AVANCE WEB - ENTREGA 2

## Proyecto

Sistema de Gestión de Ventas, Compras e Inventario — Comercial Estuardo.

## Tecnologías

- Python 3 y Flask
- MySQL
- PyMySQL
- HTML5, CSS3 y Jinja2
- python-dotenv para configuración local

## Funcionalidades implementadas

### Inicio de sesión y control de acceso

- Inicio de sesión del empleado mediante correo o CUI y contraseña.
- Verificación de contraseñas almacenadas como hash.
- Sesiones para proteger las rutas de inventario, productos y clientes.
- Cierre de sesión que elimina la sesión activa.

### Navegación y diseño

- Navegación entre Inventario, Productos y Clientes.
- Estilos compartidos y adaptación básica para pantallas pequeñas.

### Inventario

- Consulta de productos activos, categoría, precio de venta y existencias.
- Filtro para mostrar productos en o por debajo del stock mínimo.

### CRUD de productos

- Alta, consulta y edición de productos.
- Desactivación lógica mediante `estado = 0`.
- Validación de campos, precios, existencias y categoría.
- El formulario gestiona precio de costo y precio de venta.

### CRUD de clientes

- Alta, consulta y edición de clientes.
- Desactivación lógica mediante `estado = 0`.
- Validación de campos obligatorios, CUI, teléfono, correo y longitudes.

## Persistencia y configuración

Las rutas CRUD usan consultas SQL parametrizadas y operaciones de confirmación o reversión de transacciones. La conexión usa PyMySQL. Las variables locales se cargan desde `.env`, que está excluido por `.gitignore`.

La base de datos existente necesita las migraciones SQL correspondientes a las nuevas columnas de contraseña de empleado y precio de costo del producto. Las migraciones deben ejecutarse una vez en MySQL; no se debe volver a ejecutar el esquema inicial sobre una base con datos porque este elimina y recrea la base.

## Verificación pendiente en el entorno de despliegue

Las rutas y validaciones de la aplicación se revisaron con pruebas locales y conexión simulada. Falta confirmar contra MySQL real el inicio de sesión y las operaciones de alta, edición y baja lógica antes de dar por validada la persistencia de extremo a extremo.

## Próximos módulos

- Proveedores, compras y ventas.
- Control de acceso por roles.
- Vistas, triggers y procedimientos almacenados.
- Datos de prueba, casos de prueba y reportes.
