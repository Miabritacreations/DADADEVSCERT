from __future__ import annotations

import io
from pathlib import Path

from flask import abort, jsonify, render_template, request, send_file

from backend.app.config import settings

from backend.app.routes import web_bp
from backend.app.services.auth_service import AuthService
from backend.app.services.certificate_service import CertificateService


def init_web_routes(service: CertificateService) -> None:
    @web_bp.route("/", methods=["GET"])
    def landing():
        certificates = service.store.list_certificates()
        stats = {
            "total": len(certificates),
            "revoked": len([c for c in certificates if c.get("revoked")]),
        }
        return render_template("landing.html", stats=stats)

    @web_bp.route("/issue", methods=["POST"])
    def public_issue():
        data = request.form or request.get_json(force=True)
        name = data.get("name")
        cohort = data.get("cohort", "unspecified")
        if not name:
            return jsonify({"error": "name required"}), 400
        cert, pdf_bytes = service.issue(name=name, cohort=cohort)
        return send_file(
            io.BytesIO(pdf_bytes),
            as_attachment=True,
            download_name=f"certificate-{cert['id']}.pdf",
            mimetype="application/pdf",
        )

    @web_bp.route("/verify", methods=["GET"])
    def verify_form():
        cert_id = request.args.get("cert_id")
        if not cert_id:
            return render_template("verify.html", found=False, cert_id=None)
        return verify(cert_id)

    @web_bp.route("/verify/<cert_id>", methods=["GET"])
    def verify(cert_id: str):
        cert = service.verify(cert_id)
        if not cert:
            return render_template("verify.html", found=False, cert_id=cert_id), 404
        signature_valid = cert.get("signature_valid")
        ots = cert.get("ots_verification", {})
        return render_template(
            "verify.html",
            found=True,
            cert=cert,
            signature_valid=signature_valid,
            ots=ots,
        )

    @web_bp.route("/proofs/<cert_id>.ots", methods=["GET"])
    def download_proof(cert_id: str):
        proof_path = Path(settings.PROOF_DIR) / f"{cert_id}.ots"
        if not proof_path.exists():
            abort(404)
        return send_file(
            proof_path,
            mimetype="application/octet-stream",
            as_attachment=True,
            download_name=f"{cert_id}.ots",
        )
    
    @web_bp.route("/verify-identity/<cert_id>", methods=["GET", "POST"])
    def verify_identity(cert_id: str):
        """Student identity verification page."""
        auth_service = AuthService()
        cert = service.store.get_certificate(cert_id)
        
        if not cert:
            return render_template("verify_identity.html", error="Certificate not found"), 404
        
        if request.method == "POST":
            email = request.form.get("email")
            if email and email == cert.get("email"):
                # Generate verification token
                token = auth_service.generate_student_verification_token(email, cert_id)
                verify_url = f"{settings.BASE_URL}/verify-identity/{cert_id}?token={token}"
                return render_template(
                    "verify_identity.html",
                    cert=cert,
                    token=token,
                    verify_url=verify_url,
                    message="Verification link generated! Check your email or use the link below."
                )
            else:
                return render_template(
                    "verify_identity.html",
                    cert=cert,
                    error="Email does not match certificate record"
                )
        
        # Check if token is provided for verification
        token = request.args.get("token")
        if token:
            verification = auth_service.verify_student_token(token)
            if verification and verification.get("cert_id") == cert_id:
                return render_template(
                    "verify_identity.html",
                    cert=cert,
                    verified=True,
                    message="Identity verified successfully!"
                )
            else:
                return render_template(
                    "verify_identity.html",
                    cert=cert,
                    error="Invalid or expired verification token"
                )
        
        return render_template("verify_identity.html", cert=cert)

