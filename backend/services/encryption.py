# ============================================================
# Encryption Service — Fernet symmetric encryption
# ============================================================
from cryptography.fernet import Fernet
from backend.config import ENCRYPTION_KEY_FILE
from backend.core.logger import get_logger

log = get_logger("encryption")


class EncryptionService:
    """Encrypt/decrypt sensitive data using Fernet (AES-128-CBC)."""

    def __init__(self):
        self._fernet: Fernet = None
        self._load_or_create_key()

    def _load_or_create_key(self):
        if ENCRYPTION_KEY_FILE.exists():
            key = ENCRYPTION_KEY_FILE.read_bytes().strip()
        else:
            key = Fernet.generate_key()
            ENCRYPTION_KEY_FILE.write_bytes(key)
            # Restrict file permissions on Unix
            try:
                import os, stat
                os.chmod(ENCRYPTION_KEY_FILE, stat.S_IRUSR | stat.S_IWUSR)
            except Exception:
                pass
            log.info("Encryption key generated")
        self._fernet = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string. Returns base64-encoded ciphertext."""
        if not plaintext:
            return ""
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a base64-encoded ciphertext. Returns plaintext."""
        if not ciphertext:
            return ""
        try:
            return self._fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
        except Exception as e:
            log.error(f"Decryption failed: {e}")
            return ""


# Singleton
encryption_service = EncryptionService()
