import os
from pathlib import Path


class Settings:
    """Central configuration for the Dada Devs certificate platform."""

    BASE_DIR = Path(__file__).resolve().parents[2]
    DATA_DIR = BASE_DIR / "backend" / "data"
    PROOF_DIR = DATA_DIR / "ots"
    KEY_DIR = BASE_DIR / "backend" / "keys"
    STATIC_STORAGE = DATA_DIR / "artifacts"

    CERT_DB_PATH = DATA_DIR / "certs.json"
    PUBLIC_PAYLOAD_DIR = DATA_DIR / "public"

    BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "adminpass")

    PRIVATE_KEY_PATH = KEY_DIR / os.environ.get("PRIVATE_KEY_FILE", "ed25519_private.pem")
    PUBLIC_KEY_PATH = KEY_DIR / os.environ.get("PUBLIC_KEY_FILE", "ed25519_public.pem")

    IPFS_API_URL = os.environ.get("IPFS_API_URL")
    IPFS_API_KEY = os.environ.get("IPFS_API_KEY")
    IPFS_API_SECRET = os.environ.get("IPFS_API_SECRET")

    OTS_ENABLED = os.environ.get("ENABLE_OTS", "true").lower() == "true"

    PDF_ORG_NAME = os.environ.get("ORG_NAME", "Dada Devs")
    PDF_SIGNATORY = os.environ.get("SIGNATORY_NAME", "Dada Devs Training Team")


settings = Settings()

