from __future__ import annotations

import csv
import io
import uuid
from typing import Dict, List, Tuple

from backend.app.services.ipfs_service import IPFSService
from backend.app.services.linkedin_service import LinkedInService
from backend.app.services.ots_service import OpenTimestampsService
from backend.app.services.pdf_service import PDFService
from backend.app.services.signature_service import SignatureService
from backend.app.services.storage_service import CertificateStore
from backend.app.utils import canonical_payload, export_public_certificate, utc_now_iso


class CertificateService:
    def __init__(
        self,
        store: CertificateStore,
        signer: SignatureService,
        pdf_service: PDFService,
        ots_service: OpenTimestampsService,
        ipfs_service: IPFSService,
        linkedin_service: LinkedInService,
    ):
        self.store = store
        self.signer = signer
        self.pdf_service = pdf_service
        self.ots_service = ots_service
        self.ipfs_service = ipfs_service
        self.linkedin_service = linkedin_service

    def issue(self, name: str, cohort: str, email: str | None = None, metadata: Dict | None = None) -> Tuple[Dict, bytes]:
        cert_id = str(uuid.uuid4())
        issued_at = utc_now_iso()
        cert = {
            "id": cert_id,
            "name": name,
            "cohort": cohort or "unspecified",
            "email": email,
            "issued_at": issued_at,
            "revoked": False,
            "revoked_at": None,
            "revocation_reason": None,
            "metadata": metadata or {},
        }

        payload = canonical_payload(cert)
        cert["signature"] = self.signer.sign(payload)
        cert["verify_url"] = f"{self.pdf_service.base_url}/verify/{cert_id}"
        cert["linkedin_share_url"] = self.linkedin_service.share_url(cert_id)

        ots_result = self.ots_service.stamp(cert_id, payload)
        cert["ots_status"] = ots_result.get("status")
        cert["ots_proof_path"] = ots_result.get("proof_path")

        public_payload = export_public_certificate(cert)
        cert["public_payload_url"] = self.ipfs_service.pin_json(cert_id, public_payload)

        pdf_buffer = self.pdf_service.generate_pdf(cert)
        cert["artifacts"] = {"pdf_filename": f"certificate-{cert_id}.pdf"}

        self.store.save_certificate(cert)
        return cert, pdf_buffer.getvalue()

    def bulk_issue(self, csv_bytes: bytes) -> List[Dict]:
        buffer = io.StringIO(csv_bytes.decode("utf-8"))
        reader = csv.DictReader(buffer)
        issued = []
        for row in reader:
            name = row.get("name")
            cohort = row.get("cohort", "unspecified")
            email = row.get("email")
            if not name:
                continue
            cert, _ = self.issue(name=name, cohort=cohort, email=email)
            issued.append(cert)
        return issued

    def revoke(self, cert_id: str, reason: str) -> Dict | None:
        cert = self.store.get_certificate(cert_id)
        if not cert:
            return None
        cert["revoked"] = True
        cert["revoked_at"] = utc_now_iso()
        cert["revocation_reason"] = reason
        self.store.save_certificate(cert)
        return cert

    def verify(self, cert_id: str) -> Dict | None:
        cert = self.store.get_certificate(cert_id)
        if not cert:
            return None
        payload = canonical_payload(cert)
        cert["signature_valid"] = self.signer.verify(payload, cert.get("signature", ""))
        cert["ots_verification"] = self.ots_service.verify(cert_id)
        return cert

    def list_history(self) -> List[Dict]:
        return sorted(self.store.list_certificates(), key=lambda c: c["issued_at"], reverse=True)

