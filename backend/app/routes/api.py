from __future__ import annotations

from flask import jsonify, request

from backend.app.routes import api_bp
from backend.app.services.certificate_service import CertificateService


def init_api_routes(service: CertificateService) -> None:
    @api_bp.route("/certificates", methods=["POST"])
    def api_issue():
        payload = request.get_json(force=True)
        name = payload.get("name")
        cohort = payload.get("cohort", "unspecified")
        email = payload.get("email")
        if not name:
            return jsonify({"error": "name required"}), 400
        cert, _ = service.issue(name=name, cohort=cohort, email=email, metadata=payload.get("metadata"))
        return jsonify({"certificate": cert}), 201

    @api_bp.route("/certificates/bulk", methods=["POST"])
    def api_bulk_issue():
        csv_content = request.files.get("file")
        if not csv_content:
            return jsonify({"error": "CSV file required"}), 400
        issued = service.bulk_issue(csv_content.read())
        return jsonify({"issued": len(issued), "certificates": issued}), 201

    @api_bp.route("/certificates/<cert_id>", methods=["GET"])
    def api_get_cert(cert_id: str):
        cert = service.verify(cert_id)
        if not cert:
            return jsonify({"found": False}), 404
        return jsonify({"found": True, "certificate": cert})

    @api_bp.route("/certificates/<cert_id>/revoke", methods=["POST"])
    def api_revoke(cert_id: str):
        payload = request.get_json(force=True)
        reason = payload.get("reason", "No reason provided")
        cert = service.revoke(cert_id, reason)
        if not cert:
            return jsonify({"error": "Certificate not found"}), 404
        return jsonify({"certificate": cert, "status": "revoked"})

