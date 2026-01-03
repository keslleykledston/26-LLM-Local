"""
Crypto service for encrypting/decrypting secrets at rest
"""
import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


class CryptoService:
    """Encrypt/decrypt helpers using Fernet derived from SECRET_KEY"""

    def __init__(self) -> None:
        self._fernet = Fernet(self._derive_key(settings.SECRET_KEY))

    @staticmethod
    def _derive_key(secret: str) -> bytes:
        digest = hashlib.sha256(secret.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)

    def encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode("utf-8")).decode("utf-8")

    def decrypt(self, value: str) -> str:
        try:
            return self._fernet.decrypt(value.encode("utf-8")).decode("utf-8")
        except InvalidToken:
            return ""
