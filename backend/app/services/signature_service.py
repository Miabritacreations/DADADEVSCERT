import base64
from pathlib import Path
from typing import Tuple

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from backend.app.config import settings


class SignatureService:
    def __init__(
        self,
        private_key_path: Path = settings.PRIVATE_KEY_PATH,
        public_key_path: Path = settings.PUBLIC_KEY_PATH,
    ):
        self.private_key_path = private_key_path
        self.public_key_path = public_key_path
        self.private_key, self.public_key = self._load_or_create_keys()

    def _load_or_create_keys(self) -> Tuple[ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey]:
        if self.private_key_path.exists() and self.public_key_path.exists():
            private_key = self._load_private_key()
            public_key = self._load_public_key()
            return private_key, public_key

        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        self._persist_keys(private_key, public_key)
        return private_key, public_key

    def _persist_keys(self, private_key, public_key) -> None:
        self.private_key_path.parent.mkdir(parents=True, exist_ok=True)
        self.public_key_path.parent.mkdir(parents=True, exist_ok=True)

        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        self.private_key_path.write_bytes(private_bytes)
        self.public_key_path.write_bytes(public_bytes)

    def _load_private_key(self) -> ed25519.Ed25519PrivateKey:
        data = self.private_key_path.read_bytes()
        return serialization.load_pem_private_key(data, password=None)

    def _load_public_key(self) -> ed25519.Ed25519PublicKey:
        data = self.public_key_path.read_bytes()
        return serialization.load_pem_public_key(data)

    def sign(self, payload: str) -> str:
        signature = self.private_key.sign(payload.encode("utf-8"))
        return base64.b64encode(signature).decode("utf-8")

    def verify(self, payload: str, signature_b64: str) -> bool:
        try:
            signature = base64.b64decode(signature_b64.encode("utf-8"))
            self.public_key.verify(signature, payload.encode("utf-8"))
            return True
        except (InvalidSignature, ValueError, TypeError):
            return False

    def export_public_key_pem(self) -> str:
        return self.public_key_path.read_text(encoding="utf-8")

