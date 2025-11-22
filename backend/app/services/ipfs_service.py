from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

import requests

from backend.app.config import settings


class IPFSService:
    def __init__(self, public_dir: Path = settings.PUBLIC_PAYLOAD_DIR):
        self.public_dir = public_dir
        self.public_dir.mkdir(parents=True, exist_ok=True)
        self.api_url = settings.IPFS_API_URL
        self.api_key = settings.IPFS_API_KEY
        self.api_secret = settings.IPFS_API_SECRET

    def pin_json(self, cert_id: str, payload: Dict) -> Optional[str]:
        local_path = self.public_dir / f"{cert_id}.json"
        local_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        if not self.api_url:
            return None

        headers = {}
        if self.api_key:
            headers["pinata_api_key"] = self.api_key
        if self.api_secret:
            headers["pinata_secret_api_key"] = self.api_secret

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json={"pinataContent": payload},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            cid = data.get("IpfsHash") or data.get("cid")
            if cid:
                return f"https://ipfs.io/ipfs/{cid}"
        except Exception:
            return None
        return None

