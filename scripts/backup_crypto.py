"""Cifrado autenticado de respaldos. Clave solo desde el entorno."""
import os
import sys
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

MAGIC = b"CEBK1"


def key(salt):
    secret = os.environ["BACKUP_ENCRYPTION_KEY"].encode()
    if len(secret) < 32:
        raise ValueError("La clave de respaldo debe tener al menos 32 caracteres.")
    return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=600000).derive(secret)


def encrypt(source, destination):
    salt, nonce = os.urandom(16), os.urandom(12)
    cipher = Cipher(algorithms.AES(key(salt)), modes.GCM(nonce)).encryptor()
    cipher.authenticate_additional_data(MAGIC + salt + nonce)
    with open(source, "rb") as incoming, open(destination, "wb") as outgoing:
        os.chmod(destination, 0o600)
        outgoing.write(MAGIC + salt + nonce)
        while chunk := incoming.read(1024 * 1024):
            outgoing.write(cipher.update(chunk))
        outgoing.write(cipher.finalize())
        outgoing.write(cipher.tag)


def decrypt(source, destination):
    try:
        with open(source, "rb") as incoming:
            header = incoming.read(33)
            if len(header) != 33 or header[:5] != MAGIC:
                raise ValueError("Archivo de respaldo no reconocido.")
            incoming.seek(-16, 2)
            tag = incoming.read(16)
            remaining = incoming.tell() - 49
            incoming.seek(33)
            cipher = Cipher(algorithms.AES(key(header[5:21])), modes.GCM(header[21:33], tag)).decryptor()
            cipher.authenticate_additional_data(header)
            with open(destination, "wb") as outgoing:
                os.chmod(destination, 0o600)
                while remaining:
                    chunk = incoming.read(min(1024 * 1024, remaining))
                    if not chunk:
                        raise ValueError("El respaldo está incompleto.")
                    outgoing.write(cipher.update(chunk))
                    remaining -= len(chunk)
                outgoing.write(cipher.finalize())
    except Exception:
        Path(destination).unlink(missing_ok=True)
        raise


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in ("encrypt", "decrypt"):
        raise SystemExit("Uso: backup_crypto.py encrypt|decrypt origen destino")
    (encrypt if sys.argv[1] == "encrypt" else decrypt)(sys.argv[2], sys.argv[3])
