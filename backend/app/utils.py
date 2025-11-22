from __future__ import annotations

import datetime as dt
import json
from typing import Dict, Optional


CANONICAL_FIELDS = ("id", "name", "cohort", "issued_at")


def canonical_payload(cert: Dict[str, str]) -> str:
    """Return the canonical string used for signing/verification."""
    parts = [cert.get(field, "") for field in CANONICAL_FIELDS]
    return "|".join(parts)


def utc_now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def export_public_certificate(cert: Dict[str, str]) -> Dict[str, str]:
    """Strip sensitive/internal fields for public storage (IPFS/Arweave)."""
    allowed = {
        "id",
        "name",
        "cohort",
        "issued_at",
        "signature",
        "verify_url",
        "linkedin_share_url",
        "ots_status",
        "revoked",
        "revoked_at",
        "revocation_reason",
    }
    return {k: v for k, v in cert.items() if k in allowed and v is not None}


def json_dumps(data: Dict, *, indent: int = 2) -> str:
    return json.dumps(data, indent=indent, sort_keys=True)

