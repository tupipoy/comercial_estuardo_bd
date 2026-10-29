"""Respalda, comprueba una copia y aplica la migración 08 en Railway."""
import gzip
import os
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, unquote
import pymysql

DB = "comercial_estuardo_db"
FILES = ("sql/migrations/08_inventory_control.sql", "sql/triggers/02_inventory_control.sql", "sql/views/01_views.sql")


def main():
    url = urlparse(os.environ["MYSQL_PUBLIC_URL"])
    env = os.environ.copy()
    env["MYSQL_PWD"] = unquote(url.password)
    args = ["-h", url.hostname, "-P", str(url.port or 3306), "-u", unquote(url.username)]
    connection = pymysql.connect(host=url.hostname, port=url.port or 3306, user=unquote(url.username), password=unquote(url.password), database=DB, autocommit=True)

    def execute(sql):
        result = subprocess.run(["mysql", "--default-character-set=utf8mb4", *args], input=sql, env=env, capture_output=True)
        if result.returncode:
            raise RuntimeError(result.stderr.decode())

    def preflight():
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='MOVIMIENTO_INVENTARIO'")
            if cursor.fetchone()[0]:
                raise RuntimeError("La migración 08 ya está iniciada o instalada; no se volvió a aplicar.")
            cursor.execute("""SELECT COUNT(*) FROM TRASLADO t JOIN DETALLE_TRASLADO d USING(id_traslado)
                JOIN PRODUCTO p USING(id_producto) JOIN CATEGORIA c USING(id_categoria)
                WHERE t.estado IN ('Pendiente de aprobación','Aprobado','En tránsito') AND LOWER(c.nombre) LIKE '%moto%'""")
            if cursor.fetchone()[0]:
                raise RuntimeError("Hay traslados de motocicletas abiertos de la versión anterior. Conciliarlos antes de migrar.")
            cursor.execute("""SELECT COUNT(*) FROM (SELECT t.id_sucursal_origen,d.id_producto,SUM(d.cantidad) cantidad
                FROM TRASLADO t JOIN DETALLE_TRASLADO d USING(id_traslado) WHERE t.estado='Aprobado'
                GROUP BY t.id_sucursal_origen,d.id_producto) r LEFT JOIN INVENTARIO_SUCURSAL i
                ON i.id_sucursal=r.id_sucursal_origen AND i.id_producto=r.id_producto
                WHERE COALESCE(i.stock_actual,0)<r.cantidad""")
            if cursor.fetchone()[0]:
                raise RuntimeError("Las aprobaciones anteriores exceden el stock; conciliarlas antes de migrar.")

    clone = "ce_migration_check_" + uuid.uuid4().hex[:12]
    try:
        preflight()
        backup = Path("backups") / f"railway_pre_inventory_control_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.sql.gz"
        backup.parent.mkdir(mode=0o700, exist_ok=True)
        dump = subprocess.Popen(["mysqldump", *args, "--single-transaction", "--routines", "--triggers", "--events", "--no-tablespaces", "--set-gtid-purged=OFF", "--databases", DB], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with gzip.open(backup, "wb") as output:
            while chunk := dump.stdout.read(1024 * 1024):
                output.write(chunk)
        error = dump.stderr.read()
        if dump.wait():
            raise RuntimeError("Falló mysqldump: " + error.decode())
        os.chmod(backup, 0o600)
        with gzip.open(backup, "rb") as incoming:
            contents = incoming.read()
        if b"CREATE TABLE `TRASLADO`" not in contents or b"CREATE TABLE `VENTA`" not in contents:
            raise RuntimeError("El respaldo no contiene el esquema esperado.")
        print("Respaldo íntegro:", backup)
        execute(contents.replace(DB.encode(), clone.encode()))
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT (SELECT COUNT(*) FROM `{clone}`.VENTA),(SELECT COUNT(*) FROM `{clone}`.COMPRA),(SELECT SUM(stock_actual) FROM `{clone}`.INVENTARIO_SUCURSAL)")
            before = cursor.fetchone()
        for file in FILES:
            execute(Path(file).read_bytes().replace(DB.encode(), clone.encode()))
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT (SELECT COUNT(*) FROM `{clone}`.VENTA),(SELECT COUNT(*) FROM `{clone}`.COMPRA),(SELECT SUM(stock_actual) FROM `{clone}`.INVENTARIO_SUCURSAL)")
            if cursor.fetchone() != before:
                raise RuntimeError("La migración de aceptación alteró documentos o cantidades físicas.")
        print("Migración verificada en copia aislada: documentos y existencias conservados.")
        preflight()
        for file in (*FILES, "sql/security/01_roles.sql", "sql/security/02_inventory_control.sql"):
            execute(Path(file).read_bytes())
            print("Aplicado:", file)
    finally:
        with connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE IF EXISTS `{clone}`")
        connection.close()


if __name__ == "__main__":
    main()
