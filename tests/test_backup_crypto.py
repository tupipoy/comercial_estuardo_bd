import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from backup_crypto import encrypt, decrypt


class BackupCryptoTests(unittest.TestCase):
    def test_recovers_file_and_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ, {"BACKUP_ENCRYPTION_KEY": "test-only-" * 8}):
            source, archive, recovered = [Path(temporary) / name for name in ("input", "archive", "recovered")]
            source.write_bytes(os.urandom(2 * 1024 * 1024 + 37))
            encrypt(source, archive)
            decrypt(archive, recovered)
            self.assertEqual(source.read_bytes(), recovered.read_bytes())
            corrupted = bytearray(archive.read_bytes())
            corrupted[50] ^= 1
            archive.write_bytes(corrupted)
            with self.assertRaises(Exception):
                decrypt(archive, recovered)
            self.assertFalse(recovered.exists())


if __name__ == "__main__":
    unittest.main()
