# Comercial Estuardo — Entrega 4

Sistema de gestión de ventas, compras e inventario por sucursal.

- **Universidad:** Mariano Gálvez de Guatemala · Base de Datos, 2026.
- **Integrantes:** Elvin Guillermo Miranda Gómez — 2690-24-16072; Juan Carlos Ochoa Samayoa — 2690-23-7592.
- **Tecnología:** MySQL 8.4/InnoDB, Python 3.11+, Flask, PyMySQL y Gunicorn.
- **Aplicación:** https://comercialestuardobd-production.up.railway.app
- **Versión de entrega:** tag `entrega-4`.
- **Instalación:** [INSTALL.md](INSTALL.md), con los scripts en el orden indicado. No se requiere cargar datos de demostración en la base productiva.

## Funcionalidad entregada

- Login con hash, protección CSRF, suspensión progresiva y tres perfiles: Administración, Vendedor y Bodega.
- Catálogos de sucursales, empleados, clientes, categorías y productos, con bajas lógicas y permisos.
- Proveedores mediante propuesta de ambos perfiles y aprobación, edición y desactivación exclusivamente administrativas.
- Compras y ventas de varias líneas; motocicletas identificadas por VIN y motor desde la recepción, con selección de unidades al vender.
- Inventario físico, reservado, disponible y en tránsito por sucursal; vista general de consulta para Bodega y consolidado para Administración.
- Traslados con solicitud, aprobación, reserva, despacho y recepción acumulada, incluyendo diferencias.
- Kardex, historial por unidad, conteos físicos autorizados, mínimos por sucursal y alertas.
- Actualización auditada de cabeceras de compra/venta. Devoluciones y anulaciones conservan documentos y líneas; no se permite el borrado destructivo de operaciones emitidas.
- Respaldo diario cifrado a las 02:00 de Guatemala, retención de 14 días y recuperación verificada en MySQL aislado.

## Entrega y evidencias

| Documento | Contenido |
|---|---|
| [Verificación del enunciado](docs/entrega-4/ENTREGA4_VERIFICACION_REQUISITOS.md) | Requisitos del PDF, evidencias y observaciones pendientes |
| [Matriz de cierre](docs/entrega-4/ENTREGA4_MATRIZ_CIERRE.md) | Cierre técnico y responsabilidades del equipo |
| [Trazabilidad final](docs/entrega-4/MATRIZ_TRAZABILIDAD_ENTREGA_4.md) | Requerimiento → implementación → prueba |
| [Manual técnico](docs/entrega-4/ENTREGA4_MANUAL_TECNICO.md) | Arquitectura, instalación, seguridad y SQL |
| [Manual de usuario](docs/entrega-4/ENTREGA4_MANUAL_USUARIO.md) | Flujos y permisos de la aplicación |
| [Informe final](docs/entrega-4/ENTREGA4_INFORME_FINAL.md) | Resultados, decisiones y declaración de integridad |
| [Diccionario vigente](docs/entrega-4/ENTREGA4_DICCIONARIO_DATOS.md) | Las 25 tablas, columnas y restricciones reales |
| [Casos y resultados](docs/casos-prueba/CASOS_PRUEBA_ENTREGA_4.md) | Instalación limpia y pruebas automatizadas |
| [Estructura comprobada](docs/entrega-4/evidencias/VERIFICACION_ENTREGA4.json) | Conteos, objetos, versiones y hashes de scripts |
| [Auditoría del repositorio](docs/entrega-4/evidencias/AUDITORIA_REPOSITORIO.json) | Estructura, participación y búsqueda de patrones sensibles |
| [Certificación](docs/certificaciones/CERTIFICACION_ENTREGA_4.md) | Evidencia técnica y aprobaciones existentes |
| [Bitácora consolidada](docs/bitacora-ia/BITACORA_IA_CONSOLIDADA.md) | Índice y validación del apoyo de IA |
| [Guía de defensa](docs/entrega-4/ENTREGA4_GUIA_DEFENSA.md) | Decisiones que cada integrante debe explicar |

## Diagramas

- Chen base: [editable recuperado](docs/diagramas/comercialchen4.drawio) y [PNG](docs/diagramas/comercialchen3.drawio.png).
- Relacional vigente: [editable](docs/diagramas/ENTREGA4_MODELO_RELACIONAL.drawio), [PNG](docs/diagramas/ENTREGA4_MODELO_RELACIONAL.png) y [PDF de ambos modelos](docs/diagramas/ENTREGA4_DIAGRAMAS.pdf).
- La normalización histórica de Entrega 2 está en [normalizacion.md](docs/entrega-2/normalizacion.md); las extensiones y decisiones actuales se explican en el informe final.

## Antecedentes conservados

[Propuesta](docs/entrega-1/propuesta.md) · [Requerimientos RF/RD/RNF](docs/entrega-1/requerimientos.md) · [Gantt](docs/entrega-1/gantt.md) · [Diccionario de Entrega 2](docs/entrega-2/diccionario_datos.md) · [Trazabilidad de Entrega 3](docs/entrega-3/MATRIZ_TRAZABILIDAD.md). Los tags anteriores mantienen sus versiones originales.

## Estructura

`sql/ddl`, `dml`, `views`, `triggers`, `procedures`, `security` y `migrations`; `web/` contiene aplicación, servicios, conexión, plantillas y estilos; `docs/` conserva las cuatro entregas, diagramas, certificaciones, casos y bitácoras. `tests/` y `scripts/` permiten repetir la verificación.

## Comprobar la entrega

Con las variables de una conexión MySQL autorizada en `TEST_MYSQL_URL` o `MYSQL_PUBLIC_URL`, y el cliente `mysql` instalado:

```bash
python tests/test_delivery4_acceptance.py --isolated
python tests/test_inventory_control.py --isolated
python tests/test_supplier_proposals.py --isolated
python tests/test_backup_crypto.py
python scripts/audit_delivery_repository.py
```

Los tres primeros comandos crean esquemas `ce_acceptance_*` y los eliminan al terminar. El primero también usa roles y usuarios SQL temporales para verificar permisos efectivos. No mostrar ni versionar valores del entorno. Los datos semilla cumplen 50 filas por cada una de las ocho tablas principales.

## Observaciones de cierre

Las tablas conservan `UPPER_SNAKE_CASE` y las columnas `snake_case`; se documenta esta variante frente al criterio S1 del PDF. El equipo está formado por los dos integrantes indicados por el usuario. La revisión técnica no sustituye la aprobación del ER, la ratificación personal de la certificación ni la defensa oral. Ver los detalles en la matriz de verificación.
