"""Respalda Railway, cifra el archivo y verifica una restauración aislada."""
import gzip
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, unquote
import pymysql
from backup_crypto import encrypt, decrypt

ROOT = Path("backup-output")
META = ROOT / "execution.json"
DB = "comercial_estuardo_db"


def source():
    url = urlparse(os.environ["MYSQL_BACKUP_URL"])
    return pymysql.connect(host=url.hostname, port=url.port or 3306, user=unquote(url.username), password=unquote(url.password), database=DB, autocommit=True), url


def command(args, env=None, **kwargs):
    result = subprocess.run(args, env=env, stderr=subprocess.PIPE, **kwargs)
    if result.returncode:
        # Los errores de clientes pueden contener información de conexión.
        raise RuntimeError(f"Falló el paso {args[0]}; código {result.returncode}.")
    return result


def finalize():
    if not META.exists():
        return
    meta = json.loads(META.read_text())
    connection, _ = source()
    try:
        successful = os.environ.get("BACKUP_JOB_STATUS") == "success" and meta.get("verified", False)
        with connection.cursor() as cursor:
            cursor.execute("""UPDATE RESPALDO_EJECUCION SET fin=UTC_TIMESTAMP(),estado=%s,restauracion_verificada=%s,
                archivo=%s,sha256=%s,enlace=%s,detalle=%s WHERE id_respaldo=%s""", (
                "Completado" if successful else "Error", int(meta.get("verified", False)), meta.get("filename"), meta.get("sha256"),
                meta["url"], "Restauración aislada e integridad verificadas; archivo cifrado publicado." if successful else "Revisar la ejecución del respaldo; no se confirmó la publicación y restauración.", meta["id"]))
    finally:
        connection.close()


def main():
    ROOT.mkdir(mode=0o700, exist_ok=True)
    connection, url = source()
    run_url = f"{os.environ.get('GITHUB_SERVER_URL','https://github.com')}/{os.environ.get('GITHUB_REPOSITORY','tupipoy/comercial_estuardo_bd')}/actions/runs/{os.environ.get('GITHUB_RUN_ID','local')}"
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO RESPALDO_EJECUCION(enlace) VALUES(%s)", (run_url,))
        meta = {"id": cursor.lastrowid, "url": run_url, "verified": False}
    connection.close()
    META.write_text(json.dumps(meta))
    environment = os.environ.copy()
    environment["MYSQL_PWD"] = unquote(url.password)
    name = f"ce-restore-{secrets.token_hex(5)}"
    restore_environment = os.environ.copy()
    restore_environment["MYSQL_ROOT_PASSWORD"] = secrets.token_urlsafe(32)
    restore_environment["MYSQL_ROOT_HOST"] = "%"
    restore_environment["MYSQL_PWD"] = restore_environment["MYSQL_ROOT_PASSWORD"]
    started = False
    try:
        with tempfile.TemporaryDirectory(prefix="ce-backup-") as temporary:
            dump, compressed = Path(temporary) / "dump.sql", Path(temporary) / "dump.sql.gz"
            with dump.open("wb") as output:
                command(["docker", "run", "--rm", "-e", "MYSQL_PWD", "mysql:8.4", "mysqldump", "--single-transaction", "--routines", "--triggers", "--events", "--no-tablespaces", "--set-gtid-purged=OFF", "-h", url.hostname, "-P", str(url.port or 3306), "-u", unquote(url.username), "--databases", DB], env=environment, stdout=output)
            with dump.open("rb") as incoming, gzip.open(compressed, "wb") as outgoing:
                shutil.copyfileobj(incoming, outgoing)
            filename = f"comercial-estuardo-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{meta['id']}.sql.gz.enc"
            encrypted = ROOT / filename
            encrypt(compressed, encrypted)
            meta.update(filename=filename, sha256=hashlib.file_digest(encrypted.open("rb"), "sha256").hexdigest())
            META.write_text(json.dumps(meta))
            # Verifica también que la clave descifre exactamente lo que se guardó.
            recovered = Path(temporary) / "recovered.sql.gz"
            decrypt(encrypted, recovered)
            if hashlib.sha256(recovered.read_bytes()).digest() != hashlib.sha256(compressed.read_bytes()).digest():
                raise RuntimeError("El archivo descifrado no coincide con el respaldo.")
            command(["docker", "run", "-d", "--name", name, "--network", "none", "-e", "MYSQL_ROOT_PASSWORD", "-e", "MYSQL_ROOT_HOST", "mysql:8.4"], env=restore_environment, stdout=subprocess.DEVNULL)
            started = True
            for _ in range(90):
                ready = subprocess.run(["docker", "exec", "-e", "MYSQL_PWD", name, "mysqladmin", "-uroot", "-h127.0.0.1", "ping", "--silent"], env=restore_environment, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if ready.returncode == 0:
                    break
                time.sleep(2)
            else:
                raise RuntimeError("La base aislada no inició a tiempo.")
            with dump.open("rb") as incoming:
                command(["docker", "exec", "-i", "-e", "MYSQL_PWD", name, "mysql", "-uroot"], env=restore_environment, stdin=incoming, stdout=subprocess.DEVNULL)
            checks = [
                "SELECT COUNT(*) FROM INVENTARIO_SUCURSAL WHERE stock_actual<0 OR stock_reservado<0 OR stock_reservado>stock_actual",
                "SELECT COUNT(*) FROM DETALLE_VENTA d LEFT JOIN VENTA v USING(id_venta) WHERE v.id_venta IS NULL",
                "SELECT COUNT(*) FROM DETALLE_COMPRA d LEFT JOIN COMPRA c USING(id_compra) WHERE c.id_compra IS NULL",
                "SELECT COUNT(*) FROM INVENTARIO_SUCURSAL i JOIN (SELECT id_sucursal,id_producto,MAX(id_movimiento) ultimo FROM MOVIMIENTO_INVENTARIO GROUP BY id_sucursal,id_producto) x USING(id_sucursal,id_producto) JOIN MOVIMIENTO_INVENTARIO m ON m.id_movimiento=x.ultimo WHERE i.stock_actual<>m.saldo_posterior OR i.stock_reservado<>m.reservado_posterior",
            ]
            for query in checks:
                result = command(["docker", "exec", "-e", "MYSQL_PWD", name, "mysql", "-uroot", "-N", DB, "-e", query], env=restore_environment, stdout=subprocess.PIPE)
                if result.stdout.strip() != b"0":
                    raise RuntimeError("La restauración detectó una inconsistencia en los datos.")
            result = command(["docker", "exec", "-e", "MYSQL_PWD", name, "mysql", "-uroot", "-N", DB, "-e", "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TRIGGERS WHERE TRIGGER_SCHEMA=DATABASE(); SELECT COUNT(*) FROM VENTA; SELECT COUNT(*) FROM COMPRA; SELECT COUNT(*) FROM MOVIMIENTO_INVENTARIO;"], env=restore_environment, stdout=subprocess.PIPE)
            require_triggers = int(result.stdout.splitlines()[0])
            if require_triggers < 10:
                raise RuntimeError("Faltan triggers en la base restaurada.")
            meta["verified"] = True
            META.write_text(json.dumps(meta))
            print("Respaldo cifrado y restauración aislada verificados.")
    finally:
        if started:
            subprocess.run(["docker", "rm", "-f", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    if "--finalize" in sys.argv:
        finalize()
    else:
        main()
