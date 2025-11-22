from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional

from backend.app.config import settings


class CertificateStore:
    def __init__(self, db_path: Path = settings.CERT_DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def _read(self) -> Dict[str, Dict]:
        if not self.db_path.exists():
            return {}
        with self.db_path.open("r", encoding="utf-8") as handle:
            try:
                return json.load(handle)
            except json.JSONDecodeError:
                return {}

    def _write(self, data: Dict[str, Dict]) -> None:
        with self.db_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)

    def list_certificates(self) -> List[Dict]:
        with self._lock:
            return list(self._read().values())

    def get_certificate(self, cert_id: str) -> Optional[Dict]:
        with self._lock:
            return self._read().get(cert_id)

    def save_certificate(self, cert: Dict) -> Dict:
        with self._lock:
            data = self._read()
            data[cert["id"]] = cert
            self._write(data)
        return cert

    def revoke_certificate(self, cert_id: str, reason: str) -> Optional[Dict]:
        with self._lock:
            data = self._read()
            cert = data.get(cert_id)
            if not cert:
                return None
            cert["revoked"] = True
            cert["revoked_at"] = cert.get("revoked_at") or cert.get("updated_at")
            cert["revocation_reason"] = reason
            data[cert_id] = cert
            self._write(data)
            return cert

