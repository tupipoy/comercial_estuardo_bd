# Respaldos y recuperación

El workflow `.github/workflows/daily-backup.yml` se ejecuta diariamente a las 08:00 UTC (02:00 de Guatemala) y también admite ejecución manual desde Actions. Solo se activa al configurar `BACKUP_ENABLED=true`. Usa MySQL 8.4, un usuario dedicado y los secretos `MYSQL_BACKUP_URL` y `BACKUP_ENCRYPTION_KEY`. No usa la cuenta de la aplicación.

Cada ejecución obtiene un dump consistente con datos, vistas, rutinas y triggers, lo comprime y cifra con AES-256-GCM. Luego lo descifra y restaura en un contenedor MySQL sin acceso de red; valida reservas, relaciones y saldos del Kardex. El contenedor se elimina al terminar. El artefacto cifrado se conserva 14 días en GitHub Actions y el resultado aparece en **Respaldos** dentro de la aplicación. Una ejecución fallida o de más de 36 horas aparece en Alertas.

El repositorio es público: únicamente se publica el archivo cifrado. El dump sin cifrar vive en un directorio temporal del runner. La clave de recuperación está en `backups/backup_recovery.env`, excluida de Git y con permisos de lectura para el propietario. Copiar esa clave a un gestor de contraseñas o ubicación independiente del equipo; sin ella no se pueden recuperar las copias cifradas.

## Configuración inicial o renovación de credenciales

`scripts/configure_backup.py`, ejecutado con las variables MySQL de Railway y acceso administrativo a los secretos del repositorio, crea la cuenta `ce_backup` y guarda los secretos cifrados mediante la API de GitHub. Requiere PyNaCl, PyMySQL y una credencial Git de GitHub. Si detecta que existe una clave en GitHub y falta la copia local, se detiene sin rotarla.

## Recuperar un archivo

1. Abrir la ejecución desde **Respaldos** y descargar el artefacto. Extraer el archivo `.sql.gz.enc`.
2. Cargar `BACKUP_ENCRYPTION_KEY` desde la copia de recuperación al entorno de la sesión, sin escribirla en comandos ni archivos versionados.
3. Ejecutar:

   ```bash
   python scripts/backup_crypto.py decrypt copia.sql.gz.enc copia.sql.gz
   gzip -t copia.sql.gz
   ```

4. Restaurar primero en MySQL 8.4 aislado. El dump contiene `CREATE DATABASE` y `USE comercial_estuardo_db`; no apuntarlo a producción para una comprobación.
5. Comprobar documentos, existencias, reservas, unidades y saldos. Para una recuperación productiva, detener las escrituras, guardar un respaldo del estado actual y restaurar la copia elegida. Los movimientos posteriores a esa copia se deben reconciliar antes de reabrir operaciones.

La retención diaria define una pérdida potencial de hasta un día de operaciones. Para reducirla puede aumentarse la frecuencia del workflow.
