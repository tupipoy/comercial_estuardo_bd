"""Configura las credenciales dedicadas del respaldo sin imprimir secretos.

Requiere MYSQL_PUBLIC_URL de Railway, acceso Git de escritura al repositorio
y PyNaCl. La clave de recuperación queda en backups/backup_recovery.env.
"""
import base64
import json
import os
import secrets
import subprocess
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse, unquote, quote
from urllib.request import Request, urlopen
import pymysql
from nacl.public import PublicKey, SealedBox

REPOSITORY = "tupipoy/comercial_estuardo_bd"


def github(method, path, data=None):
    credential = subprocess.run(["git", "credential", "fill"], input="protocol=https\nhost=github.com\nusername=tupipoy\n\n", text=True, capture_output=True, check=True)
    values = dict(line.split("=", 1) for line in credential.stdout.splitlines() if "=" in line)
    token = values.get("password")
    if not token:
        raise RuntimeError("No hay credencial de GitHub disponible.")
    request = Request("https://api.github.com/" + path, data=json.dumps(data).encode() if data is not None else None, method=method,
                      headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "Comercial-Estuardo-Backup"})
    try:
        with urlopen(request, timeout=30) as response:
            body = response.read()
            return json.loads(body) if body else None
    except HTTPError as error:
        raise RuntimeError(f"GitHub rechazó {method} {path}: HTTP {error.code}.") from None


def configure():
    existing = github("GET", f"repos/{REPOSITORY}/actions/secrets")
    recovery = Path("backups/backup_recovery.env")
    if recovery.exists():
        encryption_key = recovery.read_text().strip().split("=", 1)[1]
    else:
        if any(secret["name"] == "BACKUP_ENCRYPTION_KEY" for secret in existing["secrets"]):
            raise RuntimeError("La clave ya está configurada en GitHub, pero falta la copia local de recuperación. No se rotó la clave.")
        encryption_key = secrets.token_hex(32)
        recovery.parent.mkdir(mode=0o700, exist_ok=True)
        descriptor = os.open(recovery, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w") as output:
            output.write("BACKUP_ENCRYPTION_KEY=" + encryption_key + "\n")
    url = urlparse(os.environ["MYSQL_PUBLIC_URL"])
    password = secrets.token_urlsafe(40)
    connection = pymysql.connect(host=url.hostname, port=url.port or 3306, user=unquote(url.username), password=unquote(url.password), autocommit=True)
    try:
        with connection.cursor() as cursor:
            cursor.execute("CREATE USER IF NOT EXISTS 'ce_backup'@'%%' IDENTIFIED BY %s", (password,))
            cursor.execute("ALTER USER 'ce_backup'@'%%' IDENTIFIED BY %s", (password,))
            cursor.execute("GRANT SELECT, SHOW VIEW, TRIGGER, EVENT ON comercial_estuardo_db.* TO 'ce_backup'@'%'")
            cursor.execute("GRANT SHOW_ROUTINE ON *.* TO 'ce_backup'@'%'")
            cursor.execute("GRANT INSERT, UPDATE ON comercial_estuardo_db.RESPALDO_EJECUCION TO 'ce_backup'@'%'")
    finally:
        connection.close()
    public = github("GET", f"repos/{REPOSITORY}/actions/secrets/public-key")
    box = SealedBox(PublicKey(base64.b64decode(public["key"])))
    backup_url = f"mysql://ce_backup:{quote(password,safe='')}@{url.hostname}:{url.port or 3306}/comercial_estuardo_db"
    for name, value in (("MYSQL_BACKUP_URL", backup_url), ("BACKUP_ENCRYPTION_KEY", encryption_key)):
        github("PUT", f"repos/{REPOSITORY}/actions/secrets/{name}", {"encrypted_value": base64.b64encode(box.encrypt(value.encode())).decode(), "key_id": public["key_id"]})
    variables = github("GET", f"repos/{REPOSITORY}/actions/variables")
    if any(item["name"] == "BACKUP_ENABLED" for item in variables["variables"]):
        github("PATCH", f"repos/{REPOSITORY}/actions/variables/BACKUP_ENABLED", {"name": "BACKUP_ENABLED", "value": "true"})
    else:
        github("POST", f"repos/{REPOSITORY}/actions/variables", {"name": "BACKUP_ENABLED", "value": "true"})
    print("Cuenta dedicada y secretos de respaldo configurados. Clave de recuperación: backups/backup_recovery.env (no incluida en Git).")


if __name__ == "__main__":
    configure()
