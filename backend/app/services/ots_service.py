from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict

from backend.app.config import settings

try:
    from opentimestamps.client import Client
    from opentimestamps.core.op import OpSHA256
    from opentimestamps.core.timestamp import DetachedTimestampFile

    OTS_AVAILABLE = True
except Exception:  # pragma: no cover
    OTS_AVAILABLE = False


class OpenTimestampsService:
    def __init__(self, proofs_dir: Path = settings.PROOF_DIR):
        self.proofs_dir = proofs_dir
        self.proofs_dir.mkdir(parents=True, exist_ok=True)
        self.enabled = settings.OTS_ENABLED and OTS_AVAILABLE
        self.client = Client() if self.enabled else None

    def stamp(self, cert_id: str, payload: str) -> Dict[str, str]:
        proof_path = self.proofs_dir / f"{cert_id}.ots"

        if not self.enabled:
            proof_path.write_text("OTS disabled for this deployment.")
            return {"status": "disabled", "proof_path": str(proof_path)}

        digest = hashlib.sha256(payload.encode("utf-8")).digest()
        detached = DetachedTimestampFile.from_hash(OpSHA256(), digest)
        try:
            self.client.stamp(detached)
            with proof_path.open("wb") as handle:
                detached.serialize(handle)
            return {"status": "stamped", "proof_path": str(proof_path)}
        except Exception as exc:  # pragma: no cover
            proof_path.write_text(f"OTS stamp failed: {exc}")
            return {"status": "error", "proof_path": str(proof_path), "error": str(exc)}

    def verify(self, cert_id: str) -> Dict[str, str]:
        proof_path = self.proofs_dir / f"{cert_id}.ots"
        if not proof_path.exists():
            return {"status": "missing"}
        if not self.enabled:
            return {"status": "disabled"}
        try:
            with proof_path.open("rb") as handle:
                detached = DetachedTimestampFile.deserialize(handle)
            result = self.client.verify(detached)
            return {"status": "verified", "result": str(result)}
        except Exception as exc:  # pragma: no cover
            return {"status": "unverified", "error": str(exc)}

