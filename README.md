# Comercial Estuardo

Sistema académico de gestión de inventario, compras y ventas para Comercial Estuardo.

## Datos del proyecto

- **Institución:** Universidad Mariano Gálvez de Guatemala
- **Curso:** Base de Datos, semestre 2026
- **SGBD:** MySQL 8.0 o superior
- **Aplicación:** Python 3.11+, Flask, PyMySQL y Gunicorn
- **Despliegue previsto:** Railway (servicio web Flask + servicio MySQL)
- **Integrantes:**
  - Elvin Guillermo Miranda Gómez — 2690-24-16072
  - Juan Carlos Ochoa Samayoa — 2690-23-7592

## Funcionalidades

- Inicio de sesión con contraseñas guardadas como hash y sesiones Flask.
- Acceso por cargo: Administrador, Vendedor y Bodega.
- Inventario con consulta de existencias y alerta de stock mínimo.
- CRUD de Productos, Clientes y Proveedores, con desactivación lógica.
- Consulta y registro web de Ventas de varios productos mediante `sp_registrar_venta_detallada`; los triggers validan y descuentan existencias.
- Consulta y registro web de Compras de varios productos mediante `sp_registrar_compra_detallada`; el procedimiento actualiza existencias y costo.
- Administración de Categorías, Sucursales y Empleados para el rol Administrador.
- Scripts SQL para datos semilla y masivos, vistas de negocio, triggers, procedimientos y roles MySQL.

## Instalación rápida

Sigue [INSTALL.md](INSTALL.md) para configurar Python, MySQL, las variables de entorno, ejecutar los scripts en el orden correcto y desplegar en Railway con Gunicorn. La prueba de instalación limpia documentada se ejecutó en un esquema temporal y no modificó la base local de trabajo.

## Estructura principal

```text
sql/
  ddl/             esquema principal
  dml/             datos semilla y carga masiva
  views/           vistas de negocio
  triggers/        reglas de inventario para ventas
  procedimiento/  procedimientos transaccionales
  security/        roles y privilegios MySQL
docs/
  entrega-1/       propuesta, requerimientos y cronograma
  entrega-2/       diccionario, normalización y avance web
  entrega-3/       avance web y matriz de trazabilidad
  entrega-4/       manuales, informe final y matriz de cierre
  casos-prueba/    casos funcionales y resultados
  bitacora-ia/     bitácoras de uso de IA
  certificaciones/ certificaciones por entrega
web/
  app.py           rutas y reglas de acceso Flask
  templates/       vistas HTML/Jinja
  static/          estilos
```

## Documentación

- [Guía de instalación](INSTALL.md)
- [Plantilla de variables de entorno](.env.example)
- [Propuesta](docs/entrega-1/propuesta.md)
- [Requerimientos](docs/entrega-1/requerimientos.md)
- [Cronograma](docs/entrega-1/gantt.md)
- [Diagrama ER editable](docs/diagramas/comercialchen4.drawio)
- [Diagrama ER en imagen](docs/diagramas/comercialchen3.drawio.png)
- [Normalización](docs/entrega-2/normalizacion.md)
- [Diccionario de datos](docs/entrega-2/diccionario_datos.md)
- [Diccionario de datos actualizado — Entrega 4](docs/entrega-4/DICCIONARIO_DATOS_ACTUALIZADO.md)
- [Avance web — Entrega 2](docs/entrega-2/AVANCE_WEB.md)
- [Avance web — Entrega 3](docs/entrega-3/AVANCE_WEB_ENTREGA_3.md)
- [Matriz de trazabilidad — Entrega 3](docs/entrega-3/MATRIZ_TRAZABILIDAD.md)
- [Casos de prueba — Entrega 3](docs/casos-prueba/CASOS_PRUEBA_ENTREGA_3.md)
- [Casos de prueba — Entrega 4](docs/casos-prueba/CASOS_PRUEBA_ENTREGA_4.md)
- [Manual técnico — Entrega 4](docs/entrega-4/MANUAL_TECNICO.md)
- [Manual de usuario — Entrega 4](docs/entrega-4/MANUAL_USUARIO.md)
- [Informe final — Entrega 4](docs/entrega-4/INFORME_FINAL.md)
- [Matriz de cierre — Entrega 4](docs/entrega-4/MATRIZ_CIERRE.md)
- [Bitácora IA — Entrega 1](docs/bitacora-ia/BITACORA_IA_ENTREGA_1.md)
- [Bitácora IA — Entrega 2](docs/bitacora-ia/BITACORA_IA_ENTREGA_2.md)
- [Bitácora IA — Entrega 3](docs/bitacora-ia/BITACORA_IA_ENTREGA_3.md)
- [Bitácora IA — Entrega 4](docs/bitacora-ia/BITACORA_IA_ENTREGA_4.md)
- [Bitácora IA consolidada](docs/bitacora-ia/BITACORA_IA_CONSOLIDADA.md)
- [Certificación — Entrega 1](docs/certificaciones/CERTIFICACION_ENTREGA_1.md)
- [Certificación — Entrega 2](docs/certificaciones/CERTIFICACION_ENTREGA_2.md)
- [Certificación — Entrega 3](docs/certificaciones/CERTIFICACION_ENTREGA_3.md)
- [Certificación — Entrega 4](docs/certificaciones/CERTIFICACION_ENTREGA_4.md)
